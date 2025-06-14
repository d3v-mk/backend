import React, { useState } from "react";

export type FormData = {
  user_id: string;
  user_id_mp: string;
  access_token: string;
  refresh_token: string;
  nome?: string | null;
};

type FormCriarPromotorProps = {
  onCriar: (data: FormData) => void;
  resultadoCriar: string;
};

export function FormCriarPromotor({ onCriar, resultadoCriar }: FormCriarPromotorProps) {
  const [form, setForm] = useState<FormData>({
    user_id: "",
    user_id_mp: "",
    access_token: "",
    refresh_token: "",
    nome: "",
  });

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    onCriar(form);
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4 w-full max-w-md">
      <input
        name="user_id"
        type="number"
        placeholder="User ID"
        value={form.user_id}
        onChange={handleChange}
        required
        className="p-2 rounded bg-gray-800 border border-gray-600"
      />
      <input
        name="user_id_mp"
        type="text"
        placeholder="User ID MP"
        value={form.user_id_mp}
        onChange={handleChange}
        required
        className="p-2 rounded bg-gray-800 border border-gray-600"
      />
      <input
        name="access_token"
        type="text"
        placeholder="Access Token"
        value={form.access_token}
        onChange={handleChange}
        required
        className="p-2 rounded bg-gray-800 border border-gray-600"
      />
      <input
        name="refresh_token"
        type="text"
        placeholder="Refresh Token"
        value={form.refresh_token}
        onChange={handleChange}
        required
        className="p-2 rounded bg-gray-800 border border-gray-600"
      />
      <input
        name="nome"
        type="text"
        placeholder="Nome (opcional)"
        value={form.nome ?? ""}
        onChange={handleChange}
        className="p-2 rounded bg-gray-800 border border-gray-600"
      />

      <button
        type="submit"
        className="bg-green-600 hover:bg-green-700 transition rounded p-2 font-semibold"
      >
        Criar Loja
      </button>

      {resultadoCriar && <p className="mt-2 text-center">{resultadoCriar}</p>}
    </form>
  );
}
