import Groq from "groq-sdk";
import { NextRequest, NextResponse } from "next/server";
import { addActions } from "@/lib/remoteQueue";

const groq = new Groq({ apiKey: process.env.GROQ_API_KEY });

const SYSTEM_PROMPT = `You are JARVIS, an AI assistant. When given a user command, respond with a JSON object containing:
- "actions": An array of action objects. Each object should have:
    - "intent": one of ["alarm", "reminder", "weather", "open_app", "call", "sms", "screenshot", "type_text", "press_key", "hotkey", "volume_control", "general"]
    - "parameters": an object with relevant details (e.g., {"text": "hello"}, {"keys": ["ctrl", "s"]})
- "response_text": A short, natural-sounding spoken response from JARVIS.

**CRITICAL: For saving files, you need BOTH a filename (e.g., "test.txt") and a location (e.g., "Desktop", "Drive E"). If either is missing, ask for it.**

Examples:
User: "Save this file" → 
{
  "actions": [{"intent":"general","parameters":{}}],
  "response_text": "Of course, sir. What would you like to name the file, and where should I save it?"
}

User: "Save it as Melroy in Drive E" → 
{
  "actions": [
    {"intent":"hotkey","parameters":{"keys":["ctrl","s"]}},
    {"intent":"type_text","parameters":{"text":"E:\\Melroy.txt"}},
    {"intent":"press_key","parameters":{"key":"enter"}}
  ],
  "response_text": "Saving the file as Melroy.txt in Drive E, sir."
}

Always respond with valid JSON only. No extra text outside the JSON.`;

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { text, deviceId } = body;

    if (!text || typeof text !== "string") {
      return NextResponse.json(
        { error: "Bad Request", message: "Field 'text' is required." },
        { status: 400 }
      );
    }

    const completion = await groq.chat.completions.create({
      model: "llama-3.3-70b-versatile",
      messages: [
        { role: "system", content: SYSTEM_PROMPT },
        { role: "user", content: text },
      ],
      temperature: 0.3,
      response_format: { type: "json_object" },
    });

    const rawContent = completion.choices[0]?.message?.content ?? "{}";
    let parsed: Record<string, unknown>;

    try {
      parsed = JSON.parse(rawContent);
    } catch {
      parsed = { intent: "general", parameters: {}, response_text: rawContent };
    }

    const desktopIntents = ["open_app", "type_text", "press_key", "hotkey", "screenshot", "volume_control"];
    const actions = (parsed.actions as any[]) || [];
    
    // If command from mobile contains PC actions, queue them
    if (deviceId !== "desktop-1" && actions.some(a => desktopIntents.includes(a.intent))) {
      console.log(`[PROXY] Forwarding ${actions.length} actions from ${deviceId} to remote queue.`);
      const { addActions } = require("@/lib/remoteQueue");
      addActions(actions);
    }

    console.log(
      `[JARVIS] Device=${deviceId} | Command="${text}" | Actions=${actions.length}`
    );

    return NextResponse.json({
      success: true,
      command: text,
      deviceId: deviceId ?? "unknown",
      ...parsed,
    });
  } catch (error: unknown) {
    console.error("[JARVIS] /api/command error:", error);

    // Handle Groq rate limit errors
    if (error && typeof error === "object" && "status" in error) {
      const status = (error as { status: number }).status;
      if (status === 429) {
        return NextResponse.json(
          {
            error: "Rate Limit",
            message: "Groq rate limit hit. Please wait a moment and try again.",
            intent: "general",
            parameters: {},
            response_text: "I'm momentarily overloaded. Please try again in a few seconds.",
          },
          { status: 429 }
        );
      }
    }

    return NextResponse.json(
      { error: "Internal Server Error", message: "Failed to process command." },
      { status: 500 }
    );
  }
}

export async function OPTIONS() {
  return new NextResponse(null, { status: 204 });
}
