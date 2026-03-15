import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "JARVIS Backend API",
  description: "JARVIS AI Assistant backend powered by Next.js",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
