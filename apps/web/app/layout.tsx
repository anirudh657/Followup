import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ActionFlow",
  description: "Meetings into executed work.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-white text-neutral-900 antialiased">
        {children}
      </body>
    </html>
  );
}
