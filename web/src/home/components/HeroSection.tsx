// home/components/HeroSection.tsx
export default function HeroSection() {
  return (
    <section className="relative z-10 text-center py-20 px-4">
      <h1 className="text-5xl md:text-6xl font-extrabold mb-4">
        Bem-vindo ao <span className="text-yellow-400">PanoPoker</span>
      </h1>
      <p className="text-lg md:text-xl max-w-xl mx-auto mb-8">
        O jogo de pôquer online feito para promotores e jogadores exigentes.
        Baixe agora e comece a sua jornada!
      </p>
      <a
        href="/apk/panopoker.apk"
        className="bg-yellow-500 hover:bg-yellow-600 text-black font-bold py-3 px-6 rounded-full text-xl transition"
      >
        📥 Baixar Agora
      </a>
    </section>
  );
}
