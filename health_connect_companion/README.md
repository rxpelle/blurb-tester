# Health Connect Companion (Android)

## What this does
This Android app reads Samsung Health data through Health Connect and posts it
to your local bridge endpoint so the personal assistant dashboard can sync it.

## Requirements
- Samsung phone (S20+ is good)
- Health Connect installed (or built-in on Android 14+)
- Phone and computer on the same Wi-Fi network
- Local bridge running on your computer (`personal_assistant/server.js`)

## Setup
1) Open `personal_assistant/server.js` on your computer:
```bash
node personal_assistant/server.js
```
2) Find your computer's local IP (example: `192.168.1.42`).
3) In the Android app, set Bridge URL to:
```
http://192.168.1.42:8787/health-connect
```

## Permissions
Tap **Grant permissions** in the app and allow:
- Steps
- Sleep
- Exercise sessions
- Distance
- Calories burned
- Heart rate

## Sync schedule
Auto sync is scheduled daily at **6:00 AM** using WorkManager.
You can always tap **Sync now**.

## Data sent to the bridge
The app posts JSON with steps, sleep, calories, distance, heart rate,
resting heart rate (approx), recovery (heuristic), and recent workouts.

## Build in Android Studio
Open `health_connect_companion` as a project and let Android Studio sync.
If the Health Connect dependency changes, update the version in
`app/build.gradle.kts`.

## Notes
- Resting heart rate is approximated from the lowest heart-rate samples
  during the last 24 hours.
- If Health Connect is not installed, the app will prompt you to install it.
