import type { FormEvent } from "react";
import { useState } from "react";

type Props = {
  onCriar: (data: {
    user_id: string;
    user_id_mp: string;
    access_token: string;
    refresh_token: string;
    nome: string;
  }) => Promise<void>;
  resultadoCriar: string;
  setResultadoCriar: (msg: string) => void;
};

export function FormCriarPromotor({ onCriar, resultadoCriar, setResultadoCriar }: Props) {
  const [formData, setFormData] = useState({
    user_id: "",
    user_id_mp: "",
    access_token: "",
    refresh_token: "",
    nome: "",
  });

  const campos = [
    { name: "user_id", label: "🆔 user_id (int)", type: "number", required: true },
    { name: "user_id_mp", label: "📦 user_id_mp", type: "text", required: true },
    { name: "access_token", label: "🔑 access_token", type: "text", required: true },
    { name: "refresh_token", label: "♻️ refresh_token", type: "text", required: true },
    { name: "nome", label: "📝 Nome (opcional)", type: "text", required: false },
  ];

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    try {
      await onCriar(formData);
      setFormData({
        user_id: "",
        user_id_mp: "",
        access_token: "",
        refresh_token: "",
        nome: "",
      });
    } catch (err: any) {
      setResultadoCriar("❌ " + (err.message || "Erro desconhecido"));
    }
  }

  return (
    <section className="bg-gray-800 p-6 rounded-lg shadow-md max-w-lg w-full mx-auto">
      <h2 className="text-2xl font-bold mb-4 text-center">⚡ Criar/Atualizar Loja de Promotor</h2>

      <form onSubmit={handleSubmit} className="space-y-4">
        {campos.map(({ name, label, type, required }) => (
          <div key={name}>
            <label className="block text-gray-300 font-medium mb-1">
              {label} {!required && <span className="text-sm text-gray-500">(opcional)</span>}
            </label>
            <input
              type={type}
              name={name}
              value={formData[name as keyof typeof formData]}
              onChange={handleChange}
              required={required}
              placeholder={required ? "" : "Ex: Loja do MK"}
              className="w-full px-3 py-2 rounded bg-gray-700 border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        ))}

        <div className="text-center mt-6">
          <button
            type="submit"
            className="bg-blue-600 hover:bg-blue-700 text-white font-semibold px-8 py-2 rounded transition"
          >
            🚀 Criar/Atualizar
          </button>
        </div>

        {resultadoCriar && (
          <div className="mt-4 text-yellow-400 font-semibold text-center">{resultadoCriar}</div>
        )}
      </form>
    </section>
  );
}
