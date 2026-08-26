import type { ReactNode } from "react";
import "./globals.css";

export const metadata = {
  title: "Enterprise AI Incident Agent",
  description:
    "AI-powered software engineering and incident resolution platform",
};

export default function RootLayout({
  children,
}: {
  children: ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}