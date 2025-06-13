// src/home/pages/HomePage.tsx
import { useEffect } from "react";
import { HeroSection } from "../components/HeroSection";

export default function HomePage() {

  const API_URL = import.meta.env.VITE_API_URL;

  useEffect(() => {
    // const ultimaVisita = localStorage.getItem("ultima-visita");
    // const agora = Date.now();

    // Só conta 1 vez por hora
    // if (!ultimaVisita || agora - parseInt(ultimaVisita) > 3600 * 1000) {
    fetch(`${API_URL}/visitas`, {
      method: "GET",
      credentials: "include",
    }).catch((err) => console.error("Erro ao contar visita:", err));

    // localStorage.setItem("ultima-visita", agora.toString());
    // }
  }, []);

  return (
    <main className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-r from-purple-600 to-indigo-700 text-white p-8">
      <HeroSection />
    </main>
  );
}
