import { NextResponse } from "next/server";

export default function Home() {
  return NextResponse.json({
    name: "JARVIS Backend API",
    version: "1.0.0",
    status: "online",
    endpoints: [
      "POST /api/command",
      "GET  /api/weather?city=<name>",
      "GET  /api/auth",
    ],
  });
}
