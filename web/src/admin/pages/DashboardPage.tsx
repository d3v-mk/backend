import { useEffect, useState } from "react";

export default function DashboardPage() {
  const [visitas, setVisitas] = useState<number | null>(null);
  const API_URL = import.meta.env.VITE_API_URL;

  useEffect(() => {
    if (!API_URL) {
      console.error("API_URL não definido no .env");
      return;
    }
    
    fetch(`${API_URL}/visitas`, {
      credentials: "include",
    })
      .then((res) => res.json())
      .then((data) => setVisitas(data.total))
      .catch((err) => {
        console.error("Erro ao buscar visitas:", err);
        setVisitas(null);
      });
  }, [API_URL]);
  
  return (
    <div className="space-y-4">
      <h1 className="text-3xl font-bold">🏠 Dashboard</h1>

      <div className="bg-gray-800 p-6 rounded shadow text-lg">
        Visitas ao site:{" "}
        {visitas !== null ? (
          <span className="font-bold text-green-400">{visitas}</span>
        ) : (
          <span className="text-red-400">Erro ao carregar</span>
        )}
      </div>
    </div>
  );
}
