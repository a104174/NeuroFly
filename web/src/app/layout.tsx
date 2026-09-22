import type { Metadata } from "next";

import "./globals.css";
import "./cockpit.css";

export const metadata: Metadata = {
  title: "NeuroFly · Experiment Browser",
  description: "Read-only inspection of reproducible NeuroFly model experiments.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
