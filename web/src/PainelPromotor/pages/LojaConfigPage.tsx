import { useEffect, useState } from "react";

type LojaForm = {
  slug: string;
  whatsapp: string;
  nome: string;
};

export default function LojaConfigPage() {
  const [form, setForm] = useState<LojaForm>({
    slug: "",
    whatsapp: "",
    nome: "",
  });

  const [loading, setLoading] = useState(false);
  const [erro, setErro] = useState("");
  const API_URL = import.meta.env.VITE_API_URL;

  useEffect(() => {
    fetch(`${API_URL}/loja/configurar`, {
      credentials: "include",
    })
      .then(async (res) => {
        if (!res.ok) throw new Error("Erro ao buscar dados");
        const data = await res.json();
        setForm(data);
      })
      .catch(() => setErro("Erro ao carregar dados da loja."));
  }, [API_URL]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setErro("");

    try {
      const res = await fetch(`${API_URL}/loja/configurar`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify(form),
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || "Erro ao salvar");
      }

      const data = await res.json();
      window.location.href = `/loja/${data.slug}`;
    } catch (err: any) {
      setErro(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-xl mx-auto p-4 mt-8 bg-zinc-900 text-white rounded-xl shadow-lg">
      <h1 className="text-2xl font-bold mb-4 text-center">Configurar Loja</h1>

      {erro && (
        <div className="bg-red-600 text-white px-4 py-2 mb-4 rounded">{erro}</div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm mb-1">Link (slug) da loja</label>
          <input
            name="slug"
            placeholder="ex: panopoker.com/loja/slug"
            value={form.slug}
            onChange={handleChange}
            required
            className="w-full px-3 py-2 rounded bg-zinc-800 border border-zinc-700 focus:outline-none focus:ring focus:ring-purple-500"
          />
        </div>

        <div>
          <label className="block text-sm mb-1">WhatsApp (ex: 5511911112222)</label>
          <input
            name="whatsapp"
            placeholder="ex: 55999999999"
            value={form.whatsapp}
            onChange={handleChange}
            required
            className="w-full px-3 py-2 rounded bg-zinc-800 border border-zinc-700 focus:outline-none focus:ring focus:ring-purple-500"
          />
        </div>

        <div>
          <label className="block text-sm mb-1">Nome de exibição</label>
          <input
            name="nome"
            placeholder="ex: Leticia ou Loja da Leticia"
            value={form.nome}
            onChange={handleChange}
            className="w-full px-3 py-2 rounded bg-zinc-800 border border-zinc-700 focus:outline-none focus:ring focus:ring-purple-500"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-purple-600 hover:bg-purple-700 transition px-4 py-2 rounded font-semibold disabled:opacity-50"
        >
          {loading ? "Salvando..." : "Salvar Configuração"}
        </button>
      </form>
    </div>
  );
}
