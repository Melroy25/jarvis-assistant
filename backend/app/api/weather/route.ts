import { NextRequest, NextResponse } from "next/server";

const OPENWEATHER_BASE = "https://api.openweathermap.org/data/2.5/weather";

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const city = searchParams.get("city") ?? "London";
    const units = searchParams.get("units") ?? "metric";
    const apiKey = process.env.WEATHER_API_KEY;

    if (!apiKey) {
      return NextResponse.json(
        { error: "Server Error", message: "Weather API key not configured." },
        { status: 500 }
      );
    }

    const weatherRes = await fetch(
      `${OPENWEATHER_BASE}?q=${encodeURIComponent(city)}&appid=${apiKey}&units=${units}`
    );

    if (!weatherRes.ok) {
      const errData = await weatherRes.json();
      return NextResponse.json(
        { error: "Weather API Error", message: errData.message ?? "Failed to fetch weather." },
        { status: weatherRes.status }
      );
    }

    const data = await weatherRes.json();

    const summary = {
      city: data.name,
      country: data.sys?.country,
      temperature: data.main?.temp,
      feels_like: data.main?.feels_like,
      humidity: data.main?.humidity,
      description: data.weather?.[0]?.description,
      icon: data.weather?.[0]?.icon,
      wind_speed: data.wind?.speed,
      units: units === "metric" ? "°C" : "°F",
      response_text: `It is currently ${Math.round(data.main?.temp)}${units === "metric" ? "°C" : "°F"} and ${data.weather?.[0]?.description} in ${data.name}.`,
    };

    return NextResponse.json({ success: true, weather: summary });
  } catch (error) {
    console.error("[JARVIS] /api/weather error:", error);
    return NextResponse.json(
      { error: "Internal Server Error", message: "Failed to fetch weather data." },
      { status: 500 }
    );
  }
}

export async function OPTIONS() {
  return new NextResponse(null, { status: 204 });
}
