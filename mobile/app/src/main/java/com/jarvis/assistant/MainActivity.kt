package com.jarvis.assistant

import android.app.AlarmManager
import android.app.PendingIntent
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Bundle
import android.telephony.SmsManager
import android.view.View
import android.view.WindowManager
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import androidx.lifecycle.lifecycleScope
import com.jarvis.assistant.databinding.ActivityMainBinding
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.util.Calendar

class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding
    private lateinit var speechManager: SpeechManager
    private lateinit var jarvisApi: JarvisApiClient
    private var isListening = false

    companion object {
        const val ACTION_WAKE_WORD_DETECTED = "com.jarvis.WAKE_WORD_DETECTED"
        private val REQUIRED_PERMISSIONS = arrayOf(
            android.Manifest.permission.RECORD_AUDIO,
            android.Manifest.permission.CALL_PHONE,
            android.Manifest.permission.SEND_SMS,
            android.Manifest.permission.READ_CONTACTS,
        )
        private const val PERMISSION_REQUEST_CODE = 101
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // Full screen immersive
        window.setFlags(
            WindowManager.LayoutParams.FLAG_LAYOUT_NO_LIMITS,
            WindowManager.LayoutParams.FLAG_LAYOUT_NO_LIMITS
        )

        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        jarvisApi = JarvisApiClient(this)
        speechManager = SpeechManager(this) { spokenText ->
            onCommandReceived(spokenText)
        }

        setupUI()
        requestPermissions()
    }

    private fun setupUI() {
        // Initially idle
        binding.waveformView.visibility = View.INVISIBLE
        binding.statusText.text = getString(R.string.status_idle)

        // Manual tap to activate (fallback when wake word service not running)
        binding.orbContainer.setOnClickListener {
            if (!isListening) triggerActivation()
        }

        // Start wake word service
        startWakeWordService()
    }

    private fun startWakeWordService() {
        val intent = Intent(this, WakeWordService::class.java)
        ContextCompat.startForegroundService(this, intent)
    }

    /** Called by WakeWordService broadcast when "Jarvis" detected */
    fun onWakeWordDetected() {
        if (isListening) return
        runOnUiThread { triggerActivation() }
    }

    private fun triggerActivation() {
        isListening = true
        // Pause wake word service to free mic
        sendBroadcast(Intent(WakeWordService.ACTION_PAUSE))

        // ── Cinematic activation sequence ──────────────────────────────────
        // 1. Darken overlay fades in
        binding.darkOverlay.animate().alpha(0.65f).setDuration(400).start()
        // ... (remaining activation code)

        // 2. Particle / fog animation via Lottie
        binding.fogAnimation.apply {
            visibility = View.VISIBLE
            playAnimation()
        }

        // 3. Orb ring pulses
        binding.orbRing.animate().scaleX(1.25f).scaleY(1.25f).setDuration(500)
            .withEndAction {
                binding.orbRing.animate().scaleX(1f).scaleY(1f).setDuration(400).start()
            }.start()

        // 4. Waveform appears
        binding.waveformView.visibility = View.VISIBLE
        binding.waveformView.startAnimation()

        // 5. Status text
        binding.statusText.text = getString(R.string.status_listening)

        // Speak "Yes?"
        speechManager.speak("Yes?") {
            speechManager.startListening()
        }
    }

    private fun onCommandReceived(text: String) {
        if (text.isEmpty()) {
            // If empty on follow-up, just go back to sleep
            deactivate("I'll be here if you need me, sir.", isFollowUp = false)
            return
        }

        binding.statusText.text = getString(R.string.status_processing)
        binding.waveformView.stopAnimation()

        lifecycleScope.launch {
            val result = withContext(Dispatchers.IO) {
                jarvisApi.sendCommand(text)
            }
            handleCommandResult(result)
        }
    }

    private suspend fun handleCommandResult(json: JSONObject?) {
        if (json == null) {
            deactivate("I couldn't reach the backend right now.", isFollowUp = false)
            return
        }

        val actionsArray = json.optJSONArray("actions")
        val responseText = json.optString("response_text", "Done.")

        if (actionsArray != null && actionsArray.length() > 0) {
            for (i in 0 until actionsArray.length()) {
                val action = actionsArray.getJSONObject(i)
                val intent = action.optString("intent", "general")
                val params = action.optJSONObject("parameters") ?: JSONObject()
                
                // Execute local action
                when (intent) {
                    "alarm"    -> setAlarm(params.optString("time", ""))
                    "reminder" -> setReminder(params.optString("time", ""), params.optString("message", ""))
                    "weather"  -> null 
                    "open_app" -> openApp(params.optString("app", ""), params.optString("url", ""))
                    "call"     -> makeCall(params.optString("contact", ""))
                    "sms"      -> sendSms(params.optString("contact", ""), params.optString("message", ""))
                }
                kotlinx.coroutines.delay(1000) // Delay between multi-actions
            }
        } else {
            // Fallback for old format
            val intent = json.optString("intent")
            if (intent.isNotEmpty()) {
                val params = json.optJSONObject("parameters") ?: JSONObject()
                when (intent) {
                    "alarm"    -> setAlarm(params.optString("time", ""))
                    "open_app" -> openApp(params.optString("app", ""), params.optString("url", ""))
                    // ... other fallbacks if needed
                }
            }
        }

        // After actions, speak response and stay active for follow-up
        deactivate(responseText, isFollowUp = true)
    }

    private fun deactivate(responseText: String, isFollowUp: Boolean = false) {
        speechManager.speak(responseText) {
            runOnUiThread {
                if (isFollowUp) {
                    // Stay in activation state, just clear text and listen again
                    binding.statusText.text = getString(R.string.status_listening)
                    binding.waveformView.startAnimation()
                    speechManager.startListening()
                } else {
                    // Full reset to idle
                    sendBroadcast(Intent(WakeWordService.ACTION_RESUME))
                    binding.darkOverlay.animate().alpha(0f).setDuration(600).start()
                    binding.fogAnimation.pauseAnimation()
                    binding.fogAnimation.visibility = View.INVISIBLE
                    binding.waveformView.stopAnimation()
                    binding.waveformView.visibility = View.INVISIBLE
                    binding.statusText.text = getString(R.string.status_idle)
                    isListening = false
                }
            }
        }
    }

    // ── Local Action Handlers ──────────────────────────────────────────────────

    private fun setAlarm(timeStr: String): String {
        if (timeStr.isEmpty()) return "What time should I set the alarm for?"
        val calendar = parseTimeString(timeStr) ?: return "I couldn't parse that time."
        val alarmManager = getSystemService(ALARM_SERVICE) as AlarmManager
        val alarmIntent = PendingIntent.getBroadcast(
            this, 0, Intent("com.jarvis.ALARM").apply { putExtra("time", timeStr) },
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )
        alarmManager.setExactAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, calendar.timeInMillis, alarmIntent)
        return "Alarm set for $timeStr."
    }

    private fun setReminder(timeStr: String, message: String): String {
        return setAlarm(timeStr) // Reuse alarm for simplicity
    }

    private fun openApp(appName: String, url: String): String {
        if (url.isNotEmpty()) {
            val uri = Uri.parse(if (url.startsWith("http")) url else "https://$url")
            startActivity(Intent(Intent.ACTION_VIEW, uri).apply { flags = Intent.FLAG_ACTIVITY_NEW_TASK })
            return "Opening $url."
        }
        val pm = packageManager
        val intent = pm.getLaunchIntentForPackage(
            findPackageByName(appName) ?: return "I couldn't find the app '$appName'."
        )
        intent?.let { startActivity(it); return "Opening $appName." }
        return "Couldn't open $appName."
    }

    private fun makeCall(contact: String): String {
        if (ContextCompat.checkSelfPermission(this, android.Manifest.permission.CALL_PHONE)
            != PackageManager.PERMISSION_GRANTED) return "Phone call permission not granted."
        val intent = Intent(Intent.ACTION_CALL, Uri.parse("tel:$contact")).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK
        }
        startActivity(intent)
        return "Calling $contact now."
    }

    private fun sendSms(contact: String, message: String): String {
        if (ContextCompat.checkSelfPermission(this, android.Manifest.permission.SEND_SMS)
            != PackageManager.PERMISSION_GRANTED) return "SMS permission not granted."
        if (contact.isEmpty() || message.isEmpty()) return "I need a contact and message to send SMS."
        SmsManager.getDefault().sendTextMessage(contact, null, message, null, null)
        return "Message sent to $contact."
    }

    // ── Helpers ───────────────────────────────────────────────────────────────

    private fun parseTimeString(timeStr: String): Calendar? {
        return try {
            val sdf = java.text.SimpleDateFormat("hh:mm a", java.util.Locale.US)
            val date = sdf.parse(timeStr.uppercase()) ?: return null
            Calendar.getInstance().apply {
                time = date
                set(Calendar.YEAR, Calendar.getInstance().get(Calendar.YEAR))
                set(Calendar.MONTH, Calendar.getInstance().get(Calendar.MONTH))
                set(Calendar.DAY_OF_MONTH, Calendar.getInstance().get(Calendar.DAY_OF_MONTH))
                if (timeInMillis < System.currentTimeMillis()) add(Calendar.DAY_OF_MONTH, 1)
            }
        } catch (e: Exception) { null }
    }

    private fun findPackageByName(appName: String): String? {
        val installed = packageManager.getInstalledApplications(PackageManager.GET_META_DATA)
        val name = appName.lowercase()
        return installed.firstOrNull {
            it.loadLabel(packageManager).toString().lowercase().contains(name)
        }?.packageName
    }

    private fun requestPermissions() {
        val missing = REQUIRED_PERMISSIONS.filter {
            ContextCompat.checkSelfPermission(this, it) != PackageManager.PERMISSION_GRANTED
        }
        if (missing.isNotEmpty()) {
            ActivityCompat.requestPermissions(this, missing.toTypedArray(), PERMISSION_REQUEST_CODE)
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        speechManager.destroy()
    }
}
