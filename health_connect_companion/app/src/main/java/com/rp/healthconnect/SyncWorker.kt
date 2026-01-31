package com.rp.healthconnect

import android.content.Context
import androidx.health.connect.client.HealthConnectClient
import androidx.work.Constraints
import androidx.work.CoroutineWorker
import androidx.work.NetworkType
import androidx.work.WorkerParameters
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

class SyncWorker(
    appContext: Context,
    workerParams: WorkerParameters
) : CoroutineWorker(appContext, workerParams) {
    override suspend fun doWork(): Result = withContext(Dispatchers.IO) {
        val prefs = applicationContext.getSharedPreferences(
            MainActivity.PREFS,
            Context.MODE_PRIVATE
        )
        val bridgeUrl = prefs.getString(
            MainActivity.KEY_BRIDGE_URL,
            MainActivity.DEFAULT_BRIDGE_URL
        ) ?: MainActivity.DEFAULT_BRIDGE_URL

        val status = HealthConnectClient.getSdkStatus(applicationContext)
        if (status != HealthConnectClient.SDK_AVAILABLE) {
            return@withContext Result.retry()
        }

        val client = HealthConnectClient.getOrCreate(applicationContext)
        val syncer = HealthConnectSyncer(client)
        val hasPermissions = syncer.hasPermissions()
        if (!hasPermissions) {
            return@withContext Result.retry()
        }

        return@withContext try {
            val payload = syncer.readPayload()
            val result = BridgeClient().sendPayload(bridgeUrl, payload)
            if (result.isSuccess) Result.success() else Result.retry()
        } catch (error: Exception) {
            Result.retry()
        }
    }

    companion object {
        val constraints = Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED)
            .build()
    }
}
