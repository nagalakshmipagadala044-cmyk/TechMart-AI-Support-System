import { Inter, IBM_Plex_Mono } from "next/font/google";
import "./globals.css";

const inter = Inter({
  variable: "--font-body",
  subsets: ["latin"],
});

const plexMono = IBM_Plex_Mono({
  variable: "--font-mono",
  weight: ["500", "600"],
  subsets: ["latin"],
});

export const metadata = {
  title: "TechMart Support Terminal",
  description: "AI-powered multi-agent customer support for TechMart Electronics",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className={`${inter.variable} ${plexMono.variable} antialiased`}>
        {children}
      </body>
    </html>
  );
}