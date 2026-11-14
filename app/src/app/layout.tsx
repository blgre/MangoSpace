import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Hubas",
  description: "Which Cebu and Bohol towns enter El Niño driest. Measured by NISAR, not forecast.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
