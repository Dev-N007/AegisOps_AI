import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Sidebar from "@/components/layout/Sidebar";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "AegisOps AI — Autonomous Incident Intelligence Platform",
  description: "From Alert to Resolution — Powered by Autonomous AI Agents. Actively monitoring, triaging, and fixing incident clusters in real-time.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${inter.variable} h-full antialiased`}>
      <body className="min-h-full bg-navy-950 text-gray-100 flex">
        {/* Left Hand Sidebar Navigation */}
        <Sidebar />
        
        {/* Right Hand Page Content Wrapper */}
        <main className="flex-1 pl-64 min-h-screen bg-transparent">
          {children}
        </main>
      </body>
    </html>
  );
}
