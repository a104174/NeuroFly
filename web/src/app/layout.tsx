import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";

import { THEME_INIT_SCRIPT } from "@/lib/theme";
import "@/styles/tokens.css";
import "./globals.css";
import "./cockpit.css";
import "./scenarios.css";
import "./product.css";

const geistSans = Geist({ subsets: ["latin"], variable: "--font-geist-sans", display: "swap" });
const geistMono = Geist_Mono({ subsets: ["latin"], variable: "--font-geist-mono", display: "swap" });

export const metadata: Metadata = {
  title: "NeuroFly · Experiment Browser",
  description: "Read-only inspection of reproducible NeuroFly model experiments.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    // data-theme is set by the inline script before hydration, so React must not warn about it.
    <html lang="en" className={`${geistSans.variable} ${geistMono.variable}`} suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: THEME_INIT_SCRIPT }} />
      </head>
      <body>{children}</body>
    </html>
  );
}
