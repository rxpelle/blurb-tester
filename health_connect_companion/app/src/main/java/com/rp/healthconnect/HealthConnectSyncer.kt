package com.rp.healthconnect

import androidx.health.connect.client.HealthConnectClient
import androidx.health.connect.client.aggregate.AggregateRequest
import androidx.health.connect.client.permission.HealthPermission
import androidx.health.connect.client.records.DistanceRecord
import androidx.health.connect.client.records.ExerciseSessionRecord
import androidx.health.connect.client.records.HeartRateRecord
import androidx.health.connect.client.records.SleepSessionRecord
import androidx.health.connect.client.records.StepsRecord
import androidx.health.connect.client.records.TotalCaloriesBurnedRecord
import androidx.health.connect.client.time.TimeRangeFilter
import java.time.Duration
import java.time.Instant
import java.time.ZoneId
import java.time.ZonedDateTime
import kotlin.math.roundToInt

data class WorkoutPayload(
    val type: String,
    val duration: Int,
    val intensity: String,
    val performedAt: String
)

data class HealthPayload(
    val steps: Long,
    val sleepHours: Double,
    val calories: Double?,
    val distanceKm: Double?,
    val heartRate: Int?,
    val restingHeartRate: Int?,
    val recovery: String,
    val workouts: List<WorkoutPayload>
)

class HealthConnectSyncer(
    private val client: HealthConnectClient
) {
    suspend fun readPayload(): HealthPayload {
        val now = Instant.now()
        val dayStart = now.minus(Duration.ofDays(1))
        val weekStart = now.minus(Duration.ofDays(7))

        val steps = aggregateSteps(dayStart, now)
        val sleepHours = aggregateSleepHours(dayStart, now)
        val calories = aggregateCalories(dayStart, now)
        val distanceKm = aggregateDistance(dayStart, now)
        val heartRateStats = aggregateHeartRate(dayStart, now)
        val workouts = readWorkouts(weekStart, now)
        val recovery = recoveryScore(sleepHours)

        return HealthPayload(
            steps = steps,
            sleepHours = sleepHours,
            calories = calories,
            distanceKm = distanceKm,
            heartRate = heartRateStats.first,
            restingHeartRate = heartRateStats.second,
            recovery = recovery,
            workouts = workouts
        )
    }

    suspend fun hasPermissions(): Boolean {
        val granted = client.permissionController.getGrantedPermissions()
        return granted.containsAll(requiredPermissions())
    }

    fun requiredPermissions(): Set<String> {
        return setOf(
            HealthPermission.getReadPermission(StepsRecord::class),
            HealthPermission.getReadPermission(SleepSessionRecord::class),
            HealthPermission.getReadPermission(ExerciseSessionRecord::class),
            HealthPermission.getReadPermission(TotalCaloriesBurnedRecord::class),
            HealthPermission.getReadPermission(DistanceRecord::class),
            HealthPermission.getReadPermission(HeartRateRecord::class)
        )
    }

    private suspend fun aggregateSteps(start: Instant, end: Instant): Long {
        val response = client.aggregate(
            AggregateRequest(
                metrics = setOf(StepsRecord.COUNT_TOTAL),
                timeRangeFilter = TimeRangeFilter.between(start, end)
            )
        )
        return response[StepsRecord.COUNT_TOTAL] ?: 0L
    }

    private suspend fun aggregateSleepHours(start: Instant, end: Instant): Double {
        val response = client.readRecords(
            SleepSessionRecord::class,
            timeRangeFilter = TimeRangeFilter.between(start, end)
        )
        val totalMinutes = response.records.sumOf { record ->
            Duration.between(record.startTime, record.endTime).toMinutes()
        }
        return totalMinutes / 60.0
    }

    private suspend fun aggregateCalories(start: Instant, end: Instant): Double? {
        val response = client.aggregate(
            AggregateRequest(
                metrics = setOf(TotalCaloriesBurnedRecord.ENERGY_TOTAL),
                timeRangeFilter = TimeRangeFilter.between(start, end)
            )
        )
        val calories = response[TotalCaloriesBurnedRecord.ENERGY_TOTAL]
        return calories?.inKilocalories
    }

    private suspend fun aggregateDistance(start: Instant, end: Instant): Double? {
        val response = client.aggregate(
            AggregateRequest(
                metrics = setOf(DistanceRecord.DISTANCE_TOTAL),
                timeRangeFilter = TimeRangeFilter.between(start, end)
            )
        )
        val distance = response[DistanceRecord.DISTANCE_TOTAL]
        return distance?.inKilometers
    }

    private suspend fun aggregateHeartRate(
        start: Instant,
        end: Instant
    ): Pair<Int?, Int?> {
        val response = client.readRecords(
            HeartRateRecord::class,
            timeRangeFilter = TimeRangeFilter.between(start, end)
        )
        val values = response.records.flatMap { record ->
            record.samples.map { it.beatsPerMinute }
        }
        if (values.isEmpty()) return null to null
        val avg = values.average().roundToInt()
        val min = values.minOrNull()
        return avg to min
    }

    private suspend fun readWorkouts(
        start: Instant,
        end: Instant
    ): List<WorkoutPayload> {
        val response = client.readRecords(
            ExerciseSessionRecord::class,
            timeRangeFilter = TimeRangeFilter.between(start, end)
        )
        return response.records.map { record ->
            val duration = Duration.between(record.startTime, record.endTime)
                .toMinutes()
                .toInt()
            WorkoutPayload(
                type = exerciseTypeLabel(record.exerciseType),
                duration = duration,
                intensity = "Moderate",
                performedAt = formatInstant(record.startTime)
            )
        }
    }

    private fun recoveryScore(sleepHours: Double): String {
        return when {
            sleepHours >= 7.5 -> "High"
            sleepHours >= 6.0 -> "Medium"
            else -> "Low"
        }
    }

    private fun formatInstant(instant: Instant): String {
        val zoned = ZonedDateTime.ofInstant(instant, ZoneId.systemDefault())
        return zoned.toString()
    }

    private fun exerciseTypeLabel(type: Int): String {
        return when (type) {
            ExerciseSessionRecord.EXERCISE_TYPE_STRENGTH_TRAINING -> "Strength"
            ExerciseSessionRecord.EXERCISE_TYPE_HIKING -> "Hiking"
            ExerciseSessionRecord.EXERCISE_TYPE_RUNNING -> "Running"
            ExerciseSessionRecord.EXERCISE_TYPE_WALKING -> "Walking"
            ExerciseSessionRecord.EXERCISE_TYPE_CYCLING -> "Cycling"
            ExerciseSessionRecord.EXERCISE_TYPE_YOGA -> "Yoga"
            ExerciseSessionRecord.EXERCISE_TYPE_HIGH_INTENSITY_INTERVAL_TRAINING -> "HIIT"
            ExerciseSessionRecord.EXERCISE_TYPE_SWIMMING -> "Swimming"
            ExerciseSessionRecord.EXERCISE_TYPE_ROWING -> "Rowing"
            ExerciseSessionRecord.EXERCISE_TYPE_OTHER_WORKOUT -> "Workout"
            else -> "Workout"
        }
    }
}
