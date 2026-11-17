import type { Metadata } from "next";
import "./globals.css";
import Header from "@/components/layout/Header";
import Footer from "@/components/layout/Footer";

export const metadata: Metadata = {
  title: "VELVORAX Careers | Smart Automation, Better Careers",
  description: "Official careers platform of VELVORAX Software Solutions. Discover IT, non-IT, and global hiring opportunities.",
  keywords: "VELVORAX Careers, Software Jobs Hyderabad, IT Recruitment, Next.js, FastAPI, AI CRM",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen flex flex-col antialiased selection:bg-brand-yellow/30 selection:text-brand-deepNavy">
        <Header />
        <main className="flex-grow">{children}</main>
        <Footer />
      </body>
    </html>
  );
}
