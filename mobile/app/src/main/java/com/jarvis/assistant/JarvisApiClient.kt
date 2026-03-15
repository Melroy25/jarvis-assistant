package com.jarvis.assistant

import android.content.Context
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject
import java.util.concurrent.TimeUnit

class JarvisApiClient(private val context: Context) {

    private val client = OkHttpClient.Builder()
        .connectTimeout(10, TimeUnit.SECONDS)
        .readTimeout(20, TimeUnit.SECONDS)
        .writeTimeout(10, TimeUnit.SECONDS)
        .build()

    private val backendUrl = BuildConfig.BACKEND_URL
    private val apiToken = BuildConfig.JARVIS_API_TOKEN
    private val deviceId = android.os.Build.MODEL.replace(" ", "-").lowercase()

    /**
     * Send a voice command text to the backend and get a structured response.
     */
    suspend fun sendCommand(text: String): JSONObject? = withContext(Dispatchers.IO) {
        try {
            val body = JSONObject().apply {
                put("text", text)
                put("deviceId", "android-$deviceId")
            }.toString().toRequestBody("application/json".toMediaType())

            val request = Request.Builder()
                .url("$backendUrl/api/command")
                .addHeader("Authorization", "Bearer $apiToken")
                .post(body)
                .build()

            val response = client.newCall(request).execute()
            val responseBody = response.body?.string() ?: return@withContext null

            if (response.isSuccessful) {
                JSONObject(responseBody)
            } else {
                null
            }
        } catch (e: Exception) {
            e.printStackTrace()
            null
        }
    }

    /**
     * Fetch weather data from the backend.
     */
    suspend fun getWeather(city: String): JSONObject? = withContext(Dispatchers.IO) {
        try {
            val request = Request.Builder()
                .url("$backendUrl/api/weather?city=${city.trim()}")
                .addHeader("Authorization", "Bearer $apiToken")
                .get()
                .build()

            val response = client.newCall(request).execute()
            val responseBody = response.body?.string() ?: return@withContext null

            if (response.isSuccessful) JSONObject(responseBody) else null
        } catch (e: Exception) {
            e.printStackTrace()
            null
        }
    }

    /**
     * Ping the backend to verify connection.
     */
    suspend fun ping(): Boolean = withContext(Dispatchers.IO) {
        try {
            val request = Request.Builder()
                .url("$backendUrl/api/auth")
                .addHeader("Authorization", "Bearer $apiToken")
                .get()
                .build()
            client.newCall(request).execute().isSuccessful
        } catch (e: Exception) { false }
    }
}
