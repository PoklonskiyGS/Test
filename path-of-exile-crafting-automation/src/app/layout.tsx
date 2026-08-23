import type { Metadata } from "next";
import type { ReactNode } from "react";
import "./globals.css";

export const metadata: Metadata = {
  title: "PoE Craft Simulator — Path of Exile Crafting Tool",
  description: "Simulate Path of Exile item crafting with currencies, prefixes, and suffixes",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="ru">
      <body className="antialiased">{children}</body>
    </html>
  );
}
