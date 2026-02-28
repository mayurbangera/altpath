import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AltPath — Life Structure Simulation Engine",
  description:
    "Simulate probable future trajectories under uncertainty. Make decisions with data, not guesswork.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="antialiased">{children}</body>
    </html>
  );
}
