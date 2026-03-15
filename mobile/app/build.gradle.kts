plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.kotlin.android)
}

android {
    namespace = "com.jarvis.assistant"
    compileSdk = 35

    defaultConfig {
        applicationId = "com.jarvis.assistant"
        minSdk = 26
        targetSdk = 35
        versionCode = 1
        versionName = "1.0.0"

        // Inject API config from local.properties
        buildConfigField("String", "BACKEND_URL", "\"${project.findProperty("BACKEND_URL") ?: "https://your-app.vercel.app"}\"")
        buildConfigField("String", "JARVIS_API_TOKEN", "\"${project.findProperty("JARVIS_API_TOKEN") ?: "change-this-to-a-random-secret"}\"")
        buildConfigField("String", "PICOVOICE_ACCESS_KEY", "\"${project.findProperty("PICOVOICE_ACCESS_KEY") ?: ""}\"")
    }

    buildFeatures {
        buildConfig = true
        viewBinding = true
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = "17"
    }
}

dependencies {
    implementation(libs.androidx.core.ktx)
    implementation(libs.androidx.appcompat)
    implementation(libs.material)

    // Wake word detection
    implementation("ai.picovoice:porcupine-android:3.0.1")

    // Offline speech recognition
    implementation("com.alphacephei:vosk-android:0.3.47")

    // Lottie animations
    implementation("com.airbnb.android:lottie:6.4.0")

    // Networking
    implementation("com.squareup.okhttp3:okhttp:4.12.0")
    implementation("org.json:json:20240303")

    // Coroutines
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.8.1")
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.8.7")
}
