// src/layouts/RankLayout.tsx
import type { ReactNode } from "react";
import { useState } from "react";

import { BackgroundPokerEffect } from "@/home/components/BackgroundPokerEffect";
import { SidebarMenu } from "@/home/components/SidebarMenu";

function Header({ onMenuClick }: { onMenuClick: () => void }) {
  return (
    <div className="fixed top-4 right-4 z-50">
      <button
        onClick={onMenuClick}
        aria-label="Abrir menu"
        className="text-yellow-400 hover:text-yellow-300 focus:outline-none bg-black bg-opacity-70 p-2 rounded-full shadow-lg"
      >
        <svg
          className="w-8 h-8"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          viewBox="0 0 24 24"
        >
          <line x1="3" y1="7" x2="21" y2="7" />
          <line x1="3" y1="12" x2="21" y2="12" />
          <line x1="3" y1="17" x2="21" y2="17" />
        </svg>
      </button>
    </div>
  );
}

type Props = {
  children: ReactNode;
};

export function RankLayout({ children }: Props) {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  return (
    <div
      className="relative min-h-screen bg-black overflow-hidden flex flex-col"
      style={{ zIndex: 0 }}
    >
      <div
        className="relative flex flex-col flex-grow bg-gradient-to-b from-gray-900 via-black to-gray-900 text-white"
        style={{ zIndex: 0 }}
      >
        <header className="py-12 px-6 text-center">
          <h1 className="text-5xl font-extrabold tracking-tight drop-shadow-[0_0_12px_rgba(255,255,255,0.5)]">
            🏆 Ranking dos Jogadores
          </h1>
          <p className="mt-2 text-gray-400 max-w-xl mx-auto font-medium">
            Os melhores do PanoPoker em um só lugar — battle pra valer!
          </p>
        </header>

        <div className="absolute inset-0 pointer-events-none" style={{ zIndex: 0 }}>
          <BackgroundPokerEffect />
        </div>

        {/* Aqui vão SidebarMenu e Header */}
        <SidebarMenu isOpen={isSidebarOpen} onClose={() => setIsSidebarOpen(false)} />
        <Header onMenuClick={() => setIsSidebarOpen(true)} />

        <main className="flex-grow max-w-5xl w-full mx-auto px-6 pb-12 overflow-auto scrollbar-thin scrollbar-thumb-gray-700 scrollbar-track-gray-900 z-10">
          {children}
        </main>

        <footer className="text-center text-gray-600 py-6 text-sm select-none z-10">
          PanoPoker &copy; {new Date().getFullYear()} — Lenda reconhece Lenda!
        </footer>
      </div>
    </div>
  );
}
