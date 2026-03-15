package com.jarvis.assistant

import ai.picovoice.porcupine.Porcupine
import ai.picovoice.porcupine.PorcupineActivationException
import ai.picovoice.porcupine.PorcupineException
import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.Intent
import android.os.IBinder
import androidx.core.app.NotificationCompat
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.launch

class WakeWordService : Service() {

    private var porcupine: Porcupine? = null
    private var porcupineManager: ai.picovoice.porcupine.PorcupineManager? = null
    private val serviceJob = Job()
    private val serviceScope = CoroutineScope(Dispatchers.IO + serviceJob)

    companion object {
        private const val CHANNEL_ID = "jarvis_wake_word"
        private const val NOTIFICATION_ID = 1001
        const val ACTION_PAUSE = "com.jarvis.PAUSE_WAKE_WORD"
        const val ACTION_RESUME = "com.jarvis.RESUME_WAKE_WORD"
    }

    private val receiver = object : android.content.BroadcastReceiver() {
        override fun onReceive(context: android.content.Context?, intent: android.content.Intent?) {
            when (intent?.action) {
                ACTION_PAUSE  -> porcupineManager?.stop()
                ACTION_RESUME -> try { porcupineManager?.start() } catch (e: Exception) {}
            }
        }
    }

    override fun onCreate() {
        super.onCreate()
        createNotificationChannel()
        startForeground(NOTIFICATION_ID, buildNotification())
        registerReceiver(receiver, android.content.IntentFilter().apply {
            addAction(ACTION_PAUSE)
            addAction(ACTION_RESUME)
        })
        startWakeWordEngine()
    }

    private fun startWakeWordEngine() {
        serviceScope.launch {
            try {
                porcupineManager = ai.picovoice.porcupine.PorcupineManager.Builder()
                    .setAccessKey(BuildConfig.PICOVOICE_ACCESS_KEY)
                    .setKeyword(ai.picovoice.porcupine.Porcupine.BuiltInKeyword.JARVIS)
                    .setSensitivity(0.6f)
                    .build(applicationContext) { keywordIndex ->
                        if (keywordIndex == 0) onWakeWordDetected()
                    }

                porcupineManager?.start()
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }

    private fun onWakeWordDetected() {
        // Pause self before broadcasting so mic is free for STT
        porcupineManager?.stop()
        val intent = Intent(MainActivity.ACTION_WAKE_WORD_DETECTED)
        sendBroadcast(intent)
    }

    private fun broadcastError(msg: String) {
        val intent = Intent("com.jarvis.ERROR").apply { putExtra("message", msg) }
        sendBroadcast(intent)
    }

    private fun createNotificationChannel() {
        val channel = NotificationChannel(
            CHANNEL_ID,
            "JARVIS Wake Word",
            NotificationManager.IMPORTANCE_LOW
        ).apply {
            description = "Listening for 'Jarvis' wake word"
            setShowBadge(false)
        }
        getSystemService(NotificationManager::class.java).createNotificationChannel(channel)
    }

    private fun buildNotification(): Notification {
        val openIntent = PendingIntent.getActivity(
            this, 0,
            Intent(this, MainActivity::class.java),
            PendingIntent.FLAG_IMMUTABLE
        )
        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("JARVIS is listening")
            .setContentText("Say 'Jarvis' to activate")
            .setSmallIcon(R.drawable.ic_jarvis)
            .setContentIntent(openIntent)
            .setOngoing(true)
            .setSilent(true)
            .build()
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        return START_STICKY
    }

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onDestroy() {
        super.onDestroy()
        porcupineManager?.stop()
        porcupineManager?.delete()
        serviceJob.cancel()
    }
}
