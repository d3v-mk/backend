import { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { BackgroundPokerEffect } from "@/home/components/BackgroundPokerEffect";
import { Header } from "@/home/components/Header";
import { Footer } from "@/home/components/Footer";
import { SidebarMenu } from "@/home/components/SidebarMenu"; // ajuste o path se necessário

export function LojaPromotorLayout() {
  const { slug } = useParams<{ slug: string }>();
  const [nome, setNome] = useState("Carregando...");
  const [avatar_url, setAvatarUrl] = useState<string | null>(null);
  const [timestamp, setTimestamp] = useState(Date.now());
  const [valorEscolhido, setValorEscolhido] = useState<number | null>(null);
  const [codigoPix, setCodigoPix] = useState<string | null>(null);
  const [copiado, setCopiado] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [menuAberto, setMenuAberto] = useState(false);

  const API_URL = import.meta.env.VITE_API_URL;
  const valores = [3, 5, 10, 20, 50, 100];

  useEffect(() => {
    if (!slug) return;

    async function fetchPromotor() {
      setError(null);
      try {
        const res = await fetch(`${API_URL}/loja/promotor/${slug}`);
        if (!res.ok) throw new Error("Promotor não encontrado");
        const data = await res.json();
        setNome(data.nome);
        setAvatarUrl(data.avatar_url);
        setTimestamp(data.timestamp);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Erro desconhecido");
        setNome("Promotor não encontrado");
        setAvatarUrl(null);
        setTimestamp(Date.now());
      }
    }

    fetchPromotor();
  }, [slug]);

  async function gerarPix(valor: number) {
    if (!slug) return alert("Slug inválido");
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/gerar_pix/${slug}/${valor}`, {
        credentials: "include",
      });
      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || "Erro ao gerar Pix");
      }
      const data = await res.json();
      setValorEscolhido(valor);
      setCodigoPix(data.pix_copia_cola);
      setCopiado(false);
    } catch (err) {
      alert(err instanceof Error ? err.message : "Erro desconhecido");
    } finally {
      setLoading(false);
    }
  }

  function copiarPix() {
    if (!codigoPix) return;
    navigator.clipboard.writeText(codigoPix).then(() => {
      setCopiado(true);
      setTimeout(() => setCopiado(false), 2000);
    });
  }

  if (!slug) {
    return (
      <main className="p-6 text-center text-red-500">
        <h1>Slug não encontrado na URL</h1>
      </main>
    );
  }

  if (error) {
    return (
      <main className="p-6 text-center text-red-500">
        <h1>{error}</h1>
      </main>
    );
  }

  return (
    <main className="relative min-h-screen bg-black text-white overflow-hidden">
      {/* Efeito de fundo */}
      <div className="absolute inset-0 pointer-events-none z-0">
        <BackgroundPokerEffect />
      </div>

      {/* Header com botão de menu */}
      <div className="relative z-20">
        <Header onMenuClick={() => setMenuAberto(true)} />
      </div>

      {/* Overlay que fecha menu ao clicar fora */}
      {menuAberto && (
        <div
          className="fixed inset-0 bg-black bg-opacity-60 z-40"
          onClick={() => setMenuAberto(false)}
        />
      )}

      {/* SidebarMenu com controle */}
      <SidebarMenu isOpen={menuAberto} onClose={() => setMenuAberto(false)} />

      {/* Conteúdo principal */}
      <div className="relative z-10 flex flex-col items-center justify-start pt-24 px-4 py-10 sm:px-6 md:px-10 max-w-2xl mx-auto">
        <img
          src={avatar_url ?? "https://i.imgur.com/1MfqtXH.png"}
          alt={`Avatar do promotor ${nome}`}
          className="rounded-full w-28 h-28 sm:w-32 sm:h-32 object-cover border-4 border-yellow-500 shadow-lg hover:scale-105 transition-transform duration-300"
          key={timestamp}
        />

        <h1 className="mt-6 text-3xl sm:text-4xl font-extrabold text-yellow-400 drop-shadow-md text-center">
          {nome}
        </h1>

        <p className="mt-3 mb-6 text-gray-300 text-base sm:text-lg text-center">
          Escolha um valor para gerar um Pix instantâneo:
        </p>

        <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 w-full max-w-md">
          {valores.map((v) => (
            <button
              key={v}
              onClick={() => gerarPix(v)}
              disabled={loading}
              className="bg-yellow-500 hover:bg-yellow-400 text-black font-bold py-2 rounded shadow-md transition-transform duration-200 hover:scale-105 active:scale-95 disabled:opacity-50"
            >
              R$ {v}
            </button>
          ))}
        </div>

        {valorEscolhido !== null && codigoPix && (
          <section
            id="resultado-pix"
            className="mt-8 w-full bg-gray-900 border border-gray-700 p-5 rounded-lg shadow-lg text-white max-w-md"
          >
            <div className="mb-3 text-lg">
              <strong className="text-yellow-400">Valor:</strong> R$ {valorEscolhido}
            </div>

            <div
              className="my-3 p-4 bg-gray-800 rounded-lg break-words select-all text-green-400 font-mono text-sm border border-gray-700"
              id="codigo-pix"
            >
              {codigoPix}
            </div>

            <button
              onClick={copiarPix}
              className="mt-4 w-full bg-yellow-500 hover:bg-yellow-400 text-black font-semibold py-2 px-4 rounded transition"
            >
              {copiado ? "Copiado! ✅" : "Copiar código Pix"}
            </button>
          </section>
        )}
      </div>

      {/* Footer bonitão */}
      <div className="relative z-10 mt-12">
        <Footer />
      </div>
    </main>
  );
}
