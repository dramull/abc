import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'ABC Multi-Agent Framework',
  description: 'World-class multi-agent framework with optimized UX',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="font-sans">{children}</body>
    </html>
  )
}