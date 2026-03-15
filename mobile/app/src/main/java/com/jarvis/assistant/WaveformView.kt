package com.jarvis.assistant

import android.content.Context
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Paint
import android.util.AttributeSet
import android.view.View
import kotlin.math.sin
import kotlin.random.Random

/**
 * Animated circular waveform that pulses when JARVIS is listening.
 * Draws concentric sine-wave bars arranged in a circle.
 */
class WaveformView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyle: Int = 0
) : View(context, attrs, defStyle) {

    private val paint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.parseColor("#00D4FF")  // JARVIS blue
        strokeWidth = 4f
        strokeCap = Paint.Cap.ROUND
    }

    private val glowPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.parseColor("#4400D4FF")
        strokeWidth = 8f
        strokeCap = Paint.Cap.ROUND
    }

    private var animationFrame = 0f
    private var isAnimating = false
    private val barCount = 48
    private val amplitudes = FloatArray(barCount) { Random.nextFloat() }

    private val animRunnable = object : Runnable {
        override fun run() {
            animationFrame += 0.08f
            for (i in 0 until barCount) {
                amplitudes[i] = ((sin(animationFrame + i * 0.3f) + 1f) / 2f * 0.7f + 0.3f)
            }
            invalidate()
            if (isAnimating) postDelayed(this, 16) // ~60fps
        }
    }

    fun startAnimation() {
        isAnimating = true
        post(animRunnable)
    }

    fun stopAnimation() {
        isAnimating = false
        removeCallbacks(animRunnable)
        invalidate()
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        if (!isAnimating) return

        val cx = width / 2f
        val cy = height / 2f
        val radius = minOf(cx, cy) * 0.6f
        val barLength = minOf(cx, cy) * 0.3f

        for (i in 0 until barCount) {
            val angle = (i * (360f / barCount) - 90f)
            val rad = Math.toRadians(angle.toDouble())
            val amp = amplitudes[i]
            val innerR = radius
            val outerR = radius + barLength * amp

            val startX = (cx + innerR * Math.cos(rad)).toFloat()
            val startY = (cy + innerR * Math.sin(rad)).toFloat()
            val stopX = (cx + outerR * Math.cos(rad)).toFloat()
            val stopY = (cy + outerR * Math.sin(rad)).toFloat()

            // Glow layer
            canvas.drawLine(startX, startY, stopX, stopY, glowPaint)
            // Sharp line
            canvas.drawLine(startX, startY, stopX, stopY, paint)
        }
    }
}
