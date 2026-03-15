import { NextRequest, NextResponse } from "next/server";

const PROTECTED_PATHS = ["/api/command", "/api/weather", "/api/auth"];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Only protect API routes
  if (PROTECTED_PATHS.some((path) => pathname.startsWith(path))) {
    const token = process.env.JARVIS_API_TOKEN;
    const authHeader = request.headers.get("authorization");

    if (!authHeader || authHeader !== `Bearer ${token}`) {
      return NextResponse.json(
        { error: "Unauthorized", message: "Invalid or missing API token." },
        { status: 401 }
      );
    }
  }

  // Add CORS headers for all API routes
  const response = NextResponse.next();
  response.headers.set("Access-Control-Allow-Origin", "*");
  response.headers.set(
    "Access-Control-Allow-Methods",
    "GET, POST, PUT, DELETE, OPTIONS"
  );
  response.headers.set(
    "Access-Control-Allow-Headers",
    "Content-Type, Authorization"
  );

  return response;
}

export const config = {
  matcher: "/api/:path*",
};
