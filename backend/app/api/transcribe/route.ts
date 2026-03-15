import Groq from "groq-sdk";
import { NextRequest, NextResponse } from "next/server";
import { writeFile, unlink } from "fs/promises";
import { join } from "path";
import { tmpdir } from "os";

const groq = new Groq({ apiKey: process.env.GROQ_API_KEY });

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const file = formData.get("file") as File;

    if (!file) {
      return NextResponse.json(
        { error: "Bad Request", message: "Audio file is required." },
        { status: 400 }
      );
    }

    // Save temporary file for Groq SDK
    const bytes = await file.arrayBuffer();
    const buffer = Buffer.from(bytes);
    const tempPath = join(tmpdir(), `jarvis-audio-${Date.now()}.wav`);
    await writeFile(tempPath, buffer);

    // Transcribe via Groq Whisper-large-v3
    const transcription = await groq.audio.transcriptions.create({
      file: require("fs").createReadStream(tempPath),
      model: "whisper-large-v3",
      language: "en", // Optional: could be dynamic based on user settings
      response_format: "json",
    });

    // Clean up
    await unlink(tempPath);

    return NextResponse.json({
      success: true,
      text: transcription.text,
    });
  } catch (error: any) {
    console.error("[JARVIS] /api/transcribe error:", error);
    return NextResponse.json(
      { error: "Internal Server Error", message: error.message },
      { status: 500 }
    );
  }
}

export async function OPTIONS() {
  return new NextResponse(null, { status: 204 });
}
