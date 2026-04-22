import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "News To Me",
  description: "Your personal daily digital newspaper",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-white text-black antialiased">
        {children}
      </body>
    </html>
  );
}
