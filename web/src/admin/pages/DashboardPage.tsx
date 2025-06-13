import { useEffect, useState } from "react";

export default function DashboardPage() {
  const [visitas, setVisitas] = useState<number | null>(null);

  useEffect(() => {
    fetch("http://localhost:8000/visitas", {
      credentials: "include",
    })
      .then((res) => res.json())
      .then((data) => setVisitas(data.total))
      .catch((err) => {
        console.error("Erro ao buscar visitas:", err);
        setVisitas(null);
      });
  }, []);

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
