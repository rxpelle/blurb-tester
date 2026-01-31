package com.rp.healthconnect

import android.content.Context
import android.content.Intent
import android.net.Uri
import android.os.Bundle
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.health.connect.client.HealthConnectClient
import androidx.lifecycle.lifecycleScope
import androidx.work.ExistingPeriodicWorkPolicy
import androidx.work.PeriodicWorkRequestBuilder
import androidx.work.WorkManager
import com.rp.healthconnect.databinding.ActivityMainBinding
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.time.Duration
import java.time.LocalDateTime
import java.time.LocalTime
import java.time.ZoneId
import java.util.concurrent.TimeUnit

class MainActivity : AppCompatActivity() {
    private lateinit var binding: ActivityMainBinding
    private val prefs by lazy {
        getSharedPreferences(PREFS, Context.MODE_PRIVATE)
    }
    private var healthClient: HealthConnectClient? = null
    private var syncer: HealthConnectSyncer? = null

    private val permissionsLauncher =
        registerForActivityResult(ActivityResultContracts.StartActivityForResult()) {
            updatePermissionStatus()
        }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        binding.bridgeUrlInput.setText(
            prefs.getString(KEY_BRIDGE_URL, DEFAULT_BRIDGE_URL)
        )

        binding.buttonSaveUrl.setOnClickListener {
            val url = binding.bridgeUrlInput.text.toString().trim()
            prefs.edit().putString(KEY_BRIDGE_URL, url).apply()
            appendLog("Bridge URL saved.")
        }

        binding.buttonPermissions.setOnClickListener {
            requestPermissions()
        }

        binding.buttonSync.setOnClickListener {
            syncNow()
        }

        initHealthConnect()
        scheduleDailySync()
    }

    private fun initHealthConnect() {
        when (HealthConnectClient.getSdkStatus(this)) {
            HealthConnectClient.SDK_AVAILABLE -> {
                healthClient = HealthConnectClient.getOrCreate(this)
                syncer = HealthConnectSyncer(healthClient!!)
                binding.healthStatusText.text = "Health Connect status: available"
                updatePermissionStatus()
            }
            HealthConnectClient.SDK_UNAVAILABLE_PROVIDER_UPDATE_REQUIRED -> {
                binding.healthStatusText.text =
                    "Health Connect not installed. Install from Play Store."
                binding.buttonPermissions.isEnabled = false
                openHealthConnectInPlayStore()
            }
            else -> {
                binding.healthStatusText.text =
                    "Health Connect unavailable on this device."
                binding.buttonPermissions.isEnabled = false
            }
        }
    }

    private fun openHealthConnectInPlayStore() {
        val intent = Intent(
            Intent.ACTION_VIEW,
            Uri.parse("https://play.google.com/store/apps/details?id=com.google.android.apps.healthdata")
        )
        startActivity(intent)
    }

    private fun requestPermissions() {
        val client = syncer ?: return
        val request = client.requiredPermissions()
        val intent = healthClient
            ?.permissionController
            ?.createRequestPermissionIntent(request)
        if (intent != null) {
            permissionsLauncher.launch(intent)
        } else {
            appendLog("Health Connect not ready.")
        }
    }

    private fun updatePermissionStatus() {
        val client = syncer ?: return
        lifecycleScope.launch {
            val hasPermissions = client.hasPermissions()
            val statusText = if (hasPermissions) {
                "Permissions: granted"
            } else {
                "Permissions: missing"
            }
            binding.statusText.text = statusText
        }
    }

    private fun syncNow() {
        val client = syncer ?: return
        val bridgeUrl = binding.bridgeUrlInput.text.toString().trim()
        if (bridgeUrl.isEmpty()) {
            appendLog("Bridge URL is empty.")
            return
        }

        lifecycleScope.launch {
            if (!client.hasPermissions()) {
                appendLog("Permissions missing. Tap Grant permissions.")
                return@launch
            }

            binding.statusText.text = "Syncing now..."
            val payload = client.readPayload()
            val result = withContext(Dispatchers.IO) {
                BridgeClient().sendPayload(bridgeUrl, payload)
            }
            if (result.isSuccess) {
                val timestamp = LocalDateTime.now().toString()
                binding.lastSyncText.text = "Last sync: $timestamp"
                appendLog("Sync complete.")
            } else {
                appendLog("Sync failed: ${result.exceptionOrNull()?.message}")
            }
            binding.statusText.text = "Ready to sync."
        }
    }

    private fun scheduleDailySync() {
        val now = LocalDateTime.now()
        val nextRun = now.with(LocalTime.of(6, 0))
        val scheduled = if (now.isBefore(nextRun)) nextRun else nextRun.plusDays(1)
        val delay = Duration.between(now, scheduled).toMillis()

        val request = PeriodicWorkRequestBuilder<SyncWorker>(24, TimeUnit.HOURS)
            .setInitialDelay(delay, TimeUnit.MILLISECONDS)
            .setConstraints(SyncWorker.constraints)
            .build()

        WorkManager.getInstance(this).enqueueUniquePeriodicWork(
            "daily-health-sync",
            ExistingPeriodicWorkPolicy.UPDATE,
            request
        )
    }

    private fun appendLog(message: String) {
        val current = binding.logText.text?.toString().orEmpty()
        val timestamp = LocalDateTime.now().atZone(ZoneId.systemDefault()).toLocalTime()
        val next = if (current.isBlank()) {
            "[$timestamp] $message"
        } else {
            "$current\n[$timestamp] $message"
        }
        binding.logText.text = next
    }

    companion object {
        const val PREFS = "health_connect_prefs"
        const val KEY_BRIDGE_URL = "bridge_url"
        const val DEFAULT_BRIDGE_URL = "http://localhost:8787/health-connect"
    }
}
