// src/pages/PageListarPromotores.tsx
import { useEffect, useState } from 'react';
import { FormListarPromotores } from '@/admin/components/FormListarPromotores';
import type { Promotor } from '@/types';

export default function PageListarPromotores() {
  const [promotores, setPromotores] = useState<Promotor[]>([]);
  const [loading, setLoading] = useState(false);
  const [erro, setErro] = useState('');
  const [ativoFiltro, setAtivoFiltro] = useState<'todos' | 'ativos' | 'bloqueados'>('todos');
  const API_URL = import.meta.env.VITE_API_URL;

  useEffect(() => {
    listarPromotores();
  }, [ativoFiltro]);

  async function listarPromotores() {
    setLoading(true);
    setErro('');
    try {
      const res = await fetch(`${API_URL}/api/admin/promotor/listar?ativo=${ativoFiltro}`, {
        method: "GET",
        credentials: "include",
      });

      if (!res.ok) throw new Error('Falha ao buscar promotores');
      const data = await res.json();
      setPromotores(data);
    } catch (err: any) {
      setErro(err.message || 'Erro desconhecido');
    }
    setLoading(false);
  }

  const copiarId = (id: number) => {
    navigator.clipboard.writeText(id.toString());
    alert("ID copiado: " + id);
  };

  return (
    <div style={{ color: '#eee', fontFamily: 'Segoe UI, Tahoma, Geneva, Verdana, sans-serif' }}>
      <h3 style={{ marginBottom: 12 }}>📋 Lista de Promotores</h3>

      <label style={{ display: 'block', marginBottom: 12, fontWeight: '600' }}>
        Filtro Status:{' '}
        <select
          value={ativoFiltro}
          onChange={e => setAtivoFiltro(e.target.value as any)}
          style={{
            marginLeft: 8,
            padding: '6px 10px',
            borderRadius: 6,
            border: 'none',
            backgroundColor: '#333366',
            color: '#eee',
            fontWeight: '600',
            cursor: 'pointer',
          }}
        >
          <option value="todos">Todos</option>
          <option value="ativos">Ativos</option>
          <option value="bloqueados">Bloqueados</option>
        </select>
      </label>

      {loading && <p style={{ fontStyle: 'italic', color: '#aaa' }}>Carregando...</p>}
      {erro && <p style={{ color: '#ff6666', fontWeight: '700' }}>{erro}</p>}

      <FormListarPromotores promotores={promotores} onCopiarId={copiarId} />
    </div>
  );
}
