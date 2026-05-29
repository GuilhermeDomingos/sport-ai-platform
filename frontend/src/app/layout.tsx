import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AXON | Análise biomecânica inteligente",
  description:
    "Transforme vídeos de Crossfit em métricas, score e feedback de performance com IA.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="pt-BR" className="h-full antialiased">
      <body className="min-h-full bg-background text-foreground">{children}</body>
    </html>
  );
}
