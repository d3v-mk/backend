import { useEffect, useState } from "react";
import HeroSection from "../components/HeroSection";
import { BackgroundPokerEffect } from "../components/BackgroundPokerEffect";

function JogadoresDoMes() {
  const jogadores = [
    { nome: "LendárioMK", rank: "Grandmaster", avatar: "/img/avatar1.png", pontos: 2540 },
    { nome: "ProDevsoul", rank: "Master", avatar: "/img/avatar2.png", pontos: 1985 },
    { nome: "AsCartas", rank: "Diamond", avatar: "/img/avatar3.png", pontos: 1730 },
    { nome: "CartasMágicas", rank: "Platinum", avatar: "/img/avatar4.png", pontos: 1500 },
    { nome: "FullHouse", rank: "Gold", avatar: "/img/avatar5.png", pontos: 1400 },
    { nome: "PokerFace", rank: "Silver", avatar: "/img/avatar6.png", pontos: 1300 },
    { nome: "ReiDosBluffs", rank: "Bronze", avatar: "/img/avatar7.png", pontos: 1200 },
    { nome: "RainhaDeCopas", rank: "Master", avatar: "/img/avatar8.png", pontos: 1800 },
  ];

  const [indexAtual, setIndexAtual] = useState(0);
  const [fade, setFade] = useState(true);

  useEffect(() => {
    const interval = setInterval(() => {
      setFade(false); // inicia fade out

      setTimeout(() => {
        setIndexAtual((old) => (old + 1) % jogadores.length);
        setFade(true); // fade in do próximo
      }, 500); // duração do fade out

    }, 4000); // troca a cada 4 segundos

    return () => clearInterval(interval);
  }, [jogadores.length]);

  const { nome, rank, avatar, pontos } = jogadores[indexAtual];

  return (
    <section className="max-w-md mx-auto px-4 py-16">
      <h2 className="text-4xl font-extrabold text-yellow-400 text-center mb-4 drop-shadow-lg">
        👑 Top 1 Mensal 👑
      </h2>

      <div
        className={`bg-gray-900 bg-opacity-70 p-8 rounded-3xl shadow-2xl flex flex-col items-center text-center max-w-sm mx-auto transition-opacity duration-500 ${
          fade ? "opacity-100" : "opacity-0"
        }`}
      >
        <img
          src={avatar}
          alt={`${nome} avatar`}
          className="w-28 h-28 rounded-full border-4 border-yellow-400 mb-6 object-cover"
          loading="lazy"
        />
        <h3 className="text-2xl font-extrabold text-yellow-400 mb-2">{nome}</h3>
        <p className="text-sm text-gray-300 mb-4">{rank}</p>
        <p className="text-yellow-300 font-semibold text-lg">🏆 {pontos} pts</p>
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





function GaleriaDoJogo() {
  const fotos = [
    { src: "/img/pic2.png", alt: "Lobby 1" },
    { src: "/img/pic3.png", alt: "Lobby 2" },
    { src: "/img/pic1.png", alt: "Mesa de Jogo" },
  ];

  const [indexAtual, setIndexAtual] = useState(0);
  const [fade, setFade] = useState(true);

  useEffect(() => {
    const interval = setInterval(() => {
      setFade(false); // começa o fade out

      setTimeout(() => {
        setIndexAtual((oldIndex) => (oldIndex + 1) % fotos.length);
        setFade(true); // fade in da próxima imagem
      }, 500); // 500ms para o fade out

    }, 3000); // troca total a cada 3 segundos

    return () => clearInterval(interval);
  }, [fotos.length]);

  return (
    <section className="max-w-6xl mx-auto px-4 py-20">
      <h2 className="text-4xl font-extrabold text-yellow-400 text-center mb-10 drop-shadow-lg">
        🎲 Galeria do Jogo
      </h2>
      <div className="flex justify-center items-center">
        <img
          src={fotos[indexAtual].src}
          alt={fotos[indexAtual].alt}
          loading="lazy"
          className={`rounded-xl shadow-lg border border-yellow-500 max-h-[300px] max-w-[400px] object-cover transition-opacity duration-500 ease-in-out ${
            fade ? "opacity-100" : "opacity-0"
          }`}
        />
      </div>
    </section>
  );
}

export default function HomePage() {
  return (
    <main className="relative min-h-screen bg-black text-white overflow-x-hidden z-0">
      <BackgroundPokerEffect />

      <HeroSection />

      <JogadoresDoMes />

      <GaleriaDoJogo />

      {/* Seção de Recursos */}
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

      {/* CTA: Baixar APK */}
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
