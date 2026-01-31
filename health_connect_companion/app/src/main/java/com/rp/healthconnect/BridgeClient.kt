package com.rp.healthconnect

import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONArray
import org.json.JSONObject

class BridgeClient(
    private val httpClient: OkHttpClient = OkHttpClient()
) {
    fun sendPayload(url: String, payload: HealthPayload): Result<String> {
        val json = JSONObject().apply {
            put("steps", payload.steps)
            put("sleepHours", payload.sleepHours)
            put("calories", payload.calories)
            put("distanceKm", payload.distanceKm)
            put("heartRate", payload.heartRate)
            put("restingHeartRate", payload.restingHeartRate)
            put("recovery", payload.recovery)
            val workoutsArray = JSONArray()
            payload.workouts.forEach { workout ->
                val workoutJson = JSONObject().apply {
                    put("type", workout.type)
                    put("duration", workout.duration)
                    put("intensity", workout.intensity)
                    put("performedAt", workout.performedAt)
                }
                workoutsArray.put(workoutJson)
            }
            put("workouts", workoutsArray)
        }

        val body = json.toString().toRequestBody("application/json".toMediaType())
        val request = Request.Builder()
            .url(url)
            .post(body)
            .build()

        return try {
            httpClient.newCall(request).execute().use { response ->
                if (!response.isSuccessful) {
                    return Result.failure(
                        IllegalStateException("Bridge error: ${response.code}")
                    )
                }
                Result.success(response.body?.string().orEmpty())
            }
        } catch (error: Exception) {
            Result.failure(error)
        }
    }
}
