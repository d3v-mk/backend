// src/layouts/RankLayout.tsx
import type { ReactNode } from "react";
import { BackgroundPokerEffect } from "@/home/components/BackgroundPokerEffect";

type Props = {
  children: ReactNode;
};

export function RankLayout({ children }: Props) {
  return (
    <div
      className="relative min-h-screen bg-black overflow-hidden flex flex-col"
      style={{ zIndex: 0 }}
    >
      {/* Fundo animado - fica na frente do gradiente */}
      <div
        className="absolute inset-0 pointer-events-none"
        style={{ zIndex: 2 }}
      >
        <BackgroundPokerEffect />
      </div>

      {/* Conteúdo com gradiente */}
      <div
        className="relative flex flex-col flex-grow bg-gradient-to-b from-gray-900 via-black to-gray-900 text-white"
        style={{ zIndex: 1 }}
      >
        <header className="py-12 px-6 text-center">
          <h1 className="text-5xl font-extrabold tracking-tight drop-shadow-[0_0_12px_rgba(255,255,255,0.5)]">
            🏆 Ranking dos Jogadores
          </h1>
          <p className="mt-2 text-gray-400 max-w-xl mx-auto font-medium">
            Os melhores do PanoPoker em um só lugar — battle pra valer!
          </p>
        </header>

        <main className="flex-grow max-w-5xl w-full mx-auto px-6 pb-12 overflow-auto scrollbar-thin scrollbar-thumb-gray-700 scrollbar-track-gray-900">
          {children}
        </main>

        <footer className="text-center text-gray-600 py-6 text-sm select-none">
          PanoPoker &copy; {new Date().getFullYear()} — Lenda reconhece Lenda!
        </footer>
      </div>
    </div>
  );
}
