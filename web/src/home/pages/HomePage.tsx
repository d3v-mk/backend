import { useEffect, useState } from "react";
import HeroSection from "../components/HeroSection";
import { BackgroundPokerEffect } from "../components/BackgroundPokerEffect";

type Jogador = {
  usuario_id: number;
  nome: string;
  avatar_url?: string | null;
  vitorias: number;
  rodadas_jogadas: number;
  porcentagem_vitorias: number;
};

export default function HomePage() {
  // --- Componente JogadoresDoMes inline ---
  function JogadoresDoMes() {
  const [jogadores, setJogadores] = useState<Jogador[]>([]);
  const [indexAtual, setIndexAtual] = useState(0);
  const [fade, setFade] = useState(true);

  useEffect(() => {
    const carregarRanking = async () => {
      try {
        const res = await fetch(`${import.meta.env.VITE_API_URL}/ranking/geral`);
        const data = await res.json();
        setJogadores(data.ranking);
      } catch (err) {
        console.error("Erro ao buscar ranking:", err);
      }
    };

    carregarRanking();
  }, []);

  // Define os filtros para pegar o top 1 por critério
  const filtros = [
    {
      nome: "Mais Vitórias",
      key: "vitorias",
      ordenar: (a: Jogador, b: Jogador) => b.vitorias - a.vitorias,
      legenda: (j: Jogador) => `Vitórias: ${j.vitorias}`,
    },
    {
      nome: "Maior Win Rate",
      key: "porcentagem_vitorias",
      ordenar: (a: Jogador, b: Jogador) => b.porcentagem_vitorias - a.porcentagem_vitorias,
      legenda: (j: Jogador) => `Win Rate: ${j.porcentagem_vitorias.toFixed(2)}%`,
    },
    {
      nome: "Mais Rodadas Jogadas",
      key: "rodadas_jogadas",
      ordenar: (a: Jogador, b: Jogador) => b.rodadas_jogadas - a.rodadas_jogadas,
      legenda: (j: Jogador) => `Rodadas: ${j.rodadas_jogadas}`,
    },
  ];

  // Pega o jogador top 1 para o filtro do índice atual
  const jogadorAtual = jogadores.length
    ? [...jogadores].sort(filtros[indexAtual].ordenar)[0]
    : null;

  useEffect(() => {
    if (jogadores.length === 0) return;

    const interval = setInterval(() => {
      setFade(false);
      setTimeout(() => {
        setIndexAtual((old) => (old + 1) % filtros.length);
        setFade(true);
      }, 500);
    }, 5000);

    return () => clearInterval(interval);
  }, [jogadores]);

  if (!jogadorAtual) {
    return (
      <section className="max-w-md mx-auto px-4 py-16 text-center text-yellow-400">
        Carregando ranking...
      </section>
    );
  }

  return (
    <section className="max-w-md mx-auto px-4 py-16">
      <h2 className="text-4xl font-extrabold text-yellow-400 text-center mb-4 drop-shadow-lg">
        👑 Top 1 👑
      </h2>

      <div
        className={`bg-gray-900 bg-opacity-70 p-8 rounded-3xl shadow-2xl flex flex-col items-center text-center max-w-sm mx-auto transition-opacity duration-500 ${
          fade ? "opacity-100" : "opacity-0"
        }`}
      >
        <img
          src={jogadorAtual.avatar_url || `https://api.dicebear.com/7.x/initials/svg?seed=${jogadorAtual.nome}`}
          alt={`${jogadorAtual.nome} avatar`}
          className="w-28 h-28 rounded-full border-4 border-yellow-400 mb-6 object-cover"
          loading="lazy"
        />
        <p className="text-yellow-300 font-semibold text-lg">🏆 {filtros[indexAtual].nome}</p>
        <h3 className="text-2xl font-extrabold text-yellow-400 mb-2">{jogadorAtual.nome}</h3>
        <p className="text-sm text-gray-300 mb-4">{filtros[indexAtual].legenda(jogadorAtual)}</p>
      </div>

      <div className="text-center mt-3 mb-10">
        <a
          href="/rank"
          className="text-yellow-300 hover:text-yellow-500 underline cursor-pointer transition"
        >
          ver ranking completo
        </a>
      </div>
    </section>
  );
}


  // --- Componente GaleriaDoJogo inline ---
  function GaleriaDoJogo() {
    const fotos = [
      { src: "/img/pic2.png", alt: "Lobby 1", orientacao: "paisagem" },
      { src: "/img/pic3.png", alt: "Lobby 2", orientacao: "paisagem" },
      { src: "/img/pic1.png", alt: "Mesa de Jogo", orientacao: "retrato" },
    ];

    const [indexAtual, setIndexAtual] = useState(0);
    const [fade, setFade] = useState(true);

    useEffect(() => {
      const interval = setInterval(() => {
        setFade(false);
        setTimeout(() => {
          setIndexAtual((oldIndex) => (oldIndex + 1) % fotos.length);
          setFade(true);
        }, 500);
      }, 5000);

      return () => clearInterval(interval);
    }, [fotos.length]);

    const imagemAtual = fotos[indexAtual];

    return (
      <section className="max-w-6xl mx-auto px-4 py-20">
        <h2 className="text-4xl font-extrabold text-yellow-400 text-center mb-10 drop-shadow-lg">
          🎲 PanoPoker
        </h2>
        <div className="flex justify-center items-center">
          <div
            className={`relative w-full 
              max-w-[320px] sm:max-w-[400px] md:max-w-[800px]
              h-[500px] md:h-auto md:aspect-[4/3]
              rounded-xl shadow-lg overflow-hidden 
              transition-opacity duration-500 ease-in-out ${
                fade ? "opacity-100" : "opacity-0"
              }`}
          >
            <img
              src={imagemAtual.src}
              alt={imagemAtual.alt}
              loading="lazy"
              className="absolute inset-0 w-full h-full object-contain"
            />
          </div>
        </div>
      </section>
    );
  }

  useEffect(() => {
    const registrarVisita = async () => {
      try {
        await fetch(`${import.meta.env.VITE_API_URL}/registrar/visita`, {
          method: "POST",
          credentials: "include",
        });
      } catch (err) {
        console.error("Erro ao registrar visita:", err);
      }
    };

    registrarVisita();
  }, []);

  return (
    <main className="relative min-h-screen bg-black text-white overflow-x-hidden z-0">
      <BackgroundPokerEffect />

      <HeroSection />

      <JogadoresDoMes />

      <GaleriaDoJogo />

      <section className="max-w-5xl mx-auto px-4 py-16">
        <h2 className="text-4xl font-extrabold mb-10 text-center text-yellow-400 drop-shadow-lg">
          🔥 Recursos do Jogo
        </h2>
        <ul className="grid grid-cols-1 md:grid-cols-2 gap-8 text-xl text-gray-300">
          {[
            "🃏 Controle de turnos com timer sincronizado",
            "⚡ Comunicação em tempo real com WebSocket",
            "📲 App Android com Jetpack Compose",
            "🛠️ Painéis de promotor e admin integrados",
            "💰 Integração com Mercado Pago",
            "🏆 Sistema de conquistas e estatísticas",
          ].map((item, i) => (
            <li
              key={i}
              className="flex items-center gap-3 bg-gray-800 bg-opacity-60 p-4 rounded-lg shadow-lg hover:bg-yellow-600 hover:text-black transition cursor-default"
            >
              <span className="text-2xl">{item.slice(0, 2)}</span>
              {item.slice(2)}
            </li>
          ))}
        </ul>
      </section>

      <section className="relative text-center py-20 px-4">
        <div className="bg-gradient-to-r from-yellow-400 via-yellow-300 to-yellow-400 rounded-3xl max-w-xl mx-auto shadow-2xl p-10">
          <h3 className="text-3xl font-extrabold text-black mb-6">
            📱 Baixe agora o app oficial!
          </h3>
          <a
            href="/apk/panopoker.apk"
            className="inline-block bg-black text-yellow-400 font-extrabold py-4 px-10 rounded-full text-2xl uppercase tracking-wider shadow-md hover:bg-yellow-500 hover:text-black transition"
          >
            📥 Baixar APK
          </a>
        </div>
      </section>
    </main>
  );
}
