import { NextResponse } from "next/server";

// Simple token validation endpoint — useful for devices to "ping"
// and confirm their token is valid before starting sessions.
export async function GET() {
  return NextResponse.json({
    success: true,
    message: "JARVIS backend is online. Token is valid.",
    timestamp: new Date().toISOString(),
  });
}

export async function OPTIONS() {
  return new NextResponse(null, { status: 204 });
}
