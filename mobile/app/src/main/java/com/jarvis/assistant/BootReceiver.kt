package com.jarvis.assistant

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import androidx.core.content.ContextCompat

/**
 * Restarts the WakeWordService after device reboot.
 */
class BootReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        if (intent.action == Intent.ACTION_BOOT_COMPLETED) {
            ContextCompat.startForegroundService(
                context,
                Intent(context, WakeWordService::class.java)
            )
        }
    }
}
