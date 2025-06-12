import { Outlet } from "react-router-dom";
import { Header } from "../components/Header";
import { Footer } from "../components/Footer";
import { BackgroundPokerEffect } from "../components/BackgroundPokerEffect";

export function HomeLayout() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-black via-zinc-900 to-black text-yellow-400 font-sans relative">
      <BackgroundPokerEffect />
      <Header />
      <main className="container mx-auto px-6 py-12">
        <Outlet />
      </main>
      <Footer />
    </div>
  );
}
