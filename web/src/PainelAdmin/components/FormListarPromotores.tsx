import type { Promotor } from '@/types';
import { useState } from 'react';

type Props = {
  promotores: Promotor[];
};

export function FormListarPromotores({ promotores }: Props) {
  const [loadingId, setLoadingId] = useState<number | null>(null);
  const [actionOpenId, setActionOpenId] = useState<number | null>(null);
  const API_URL = import.meta.env.VITE_API_URL;

  const desbloquearPromotor = async (id: number) => {
    if (!confirm(`Desbloquear promotor ${id}?`)) return;
    setLoadingId(id);
    try {
      const res = await fetch(`${API_URL}/admin/promotor/${id}/desbloquear`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
      });

      let data;
      try {
        data = await res.json();
      } catch {
        throw new Error('Resposta inválida do servidor (sem JSON)');
      }

      if (!res.ok) throw new Error(data?.detail || 'Erro ao desbloquear');

      alert(`✅ ${data.mensagem}`);
      window.location.reload();
    } catch (err: any) {
      alert(`❌ Falha ao desbloquear: ${err.message}`);
    } finally {
      setLoadingId(null);
      setActionOpenId(null);
    }
  };

  if (promotores.length === 0) {
    return (
      <p className="text-center py-6 text-zinc-400 italic select-none">
        Nenhum promotor encontrado
      </p>
    );
  }

  return (
    <>
      {/* Tabela desktop (hidden no mobile) */}
      <div className="hidden sm:block overflow-x-auto rounded-lg shadow-lg bg-zinc-800">
        <table className="min-w-full divide-y divide-zinc-700">
          <thead className="bg-zinc-700">
            <tr>
              <th className="px-4 py-2 text-left text-sm font-semibold text-white whitespace-nowrap">Nome</th>
              <th className="px-4 py-2 text-left text-sm font-semibold text-white whitespace-nowrap">ID</th>
              <th className="px-4 py-2 text-left text-sm font-semibold text-white whitespace-nowrap">Slug</th>
              <th className="px-4 py-2 text-center text-sm font-semibold text-white whitespace-nowrap">Access Token</th>
              <th className="px-4 py-2 text-right text-sm font-semibold text-white whitespace-nowrap">Saldo a Repassar</th>
              <th className="px-4 py-2 text-center text-sm font-semibold text-white whitespace-nowrap">Status</th>
              <th className="px-4 py-2 text-left text-sm font-semibold text-white whitespace-nowrap">Última Atividade</th>
              <th className="px-4 py-2 text-center text-sm font-semibold text-white whitespace-nowrap">Ações</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-700">
            {promotores.map((p) => (
              <tr
                key={p.id}
                className={`${
                  p.bloqueado ? 'bg-red-900' : 'bg-zinc-900'
                } hover:bg-zinc-700 transition-colors`}
              >
                <td className="px-4 py-2 whitespace-nowrap">{p.nome || '-'}</td>
                <td className="px-4 py-2 whitespace-nowrap">{p.id}</td>
                <td className="px-4 py-2 whitespace-nowrap">{p.slug || '-'}</td>
                <td className="px-4 py-2 text-center whitespace-nowrap">
                  {p.access_token ? '✅' : '❌'}
                </td>
                <td className="px-4 py-2 text-right whitespace-nowrap">
                  R$ {p.saldo.toFixed(2)}
                </td>
                <td
                  className={`px-4 py-2 text-center font-semibold whitespace-nowrap ${
                    p.bloqueado ? 'text-red-400' : 'text-green-400'
                  }`}
                >
                  {p.bloqueado ? 'Bloqueado ❌' : 'Liberado ✅'}
                </td>
                <td className="px-4 py-2 whitespace-nowrap">{p.ultima_atividade || '⏳ Sem atividade recente'}</td>
                <td className="px-4 py-2 text-center whitespace-nowrap relative">
                  <button
                    onClick={() =>
                      setActionOpenId(actionOpenId === p.id ? null : p.id)
                    }
                    className="bg-purple-600 hover:bg-purple-700 text-white px-3 py-1 rounded focus:outline-none focus:ring-2 focus:ring-purple-400"
                    aria-expanded={actionOpenId === p.id}
                    aria-controls={`acoes-${p.id}`}
                  >
                    Ações ▼
                  </button>

                  {actionOpenId === p.id && (
                    <div
                      id={`acoes-${p.id}`}
                      className="absolute right-0 mt-2 w-40 bg-zinc-800 rounded shadow-lg flex flex-col gap-2 p-2 z-20"
                    >
                      <button
                        disabled={!p.bloqueado || loadingId === p.id}
                        onClick={() => desbloquearPromotor(p.id)}
                        className={`w-full text-left px-2 py-1 rounded ${
                          !p.bloqueado
                            ? 'opacity-50 cursor-not-allowed'
                            : 'hover:bg-green-600'
                        }`}
                      >
                        {loadingId === p.id ? 'Desbloqueando...' : 'Desbloquear ✅'}
                      </button>

                      {p.slug && (
                        <button
                          onClick={() =>
                            confirm('Apagar loja?') &&
                            console.log('Apagar loja de', p.id)
                          }
                          className="w-full text-left px-2 py-1 rounded hover:bg-red-600 text-red-400"
                        >
                          Apagar Loja 🗑️
                        </button>
                      )}
                    </div>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Cards mobile (visível só no mobile) */}
      <div className="sm:hidden flex flex-col gap-4">
        {promotores.map((p) => (
          <div
            key={p.id}
            className={`bg-zinc-900 rounded-lg p-4 shadow-md ${
              p.bloqueado ? 'border-2 border-red-700' : 'border border-zinc-700'
            }`}
          >
            <div className="flex justify-between items-center mb-2">
              <h4 className="font-semibold text-lg">{p.nome || '-'}</h4>
              <span
                className={`font-semibold ${
                  p.bloqueado ? 'text-red-400' : 'text-green-400'
                }`}
              >
                {p.bloqueado ? 'Bloqueado ❌' : 'Liberado ✅'}
              </span>
            </div>

            <p><strong>ID:</strong> {p.id}</p>
            <p><strong>Slug:</strong> {p.slug || '-'}</p>
            <p>
              <strong>Access Token:</strong> {p.access_token ? '✅' : '❌'}
            </p>
            <p><strong>Saldo a Repassar:</strong> R$ {p.saldo.toFixed(2)}</p>
            <p><strong>Última Atividade:</strong> {p.ultima_atividade || '⏳ Sem atividade recente'}</p>

            <div className="mt-3 flex flex-col gap-2">
              <button
                disabled={!p.bloqueado || loadingId === p.id}
                onClick={() => desbloquearPromotor(p.id)}
                className={`w-full rounded py-2 text-white ${
                  !p.bloqueado
                    ? 'bg-zinc-600 cursor-not-allowed opacity-50'
                    : 'bg-green-600 hover:bg-green-700'
                }`}
              >
                {loadingId === p.id ? 'Desbloqueando...' : 'Desbloquear ✅'}
              </button>

              {p.slug && (
                <button
                  onClick={() =>
                    confirm('Apagar loja?') &&
                    console.log('Apagar loja de', p.id)
                  }
                  className="w-full rounded py-2 bg-red-600 hover:bg-red-700 text-white"
                >
                  Apagar Loja 🗑️
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
    </>
  );
}
