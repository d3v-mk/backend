import { useEffect, useState } from 'react';

interface Promotor {
  user_id: number;
  user_id_mp: string;
  nome: string | null;
  saldo: number;
  ativo: boolean;
}

export function FormListarPromotores() {
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
        const res = await fetch(`${API_URL}/api/admin/promotor/listar?ativo=todos`, {
        method: "GET",
        credentials: "include", // cookie é enviado só assim
        })

        if (!res.ok) throw new Error('Falha ao buscar promotores');
        const data = await res.json();
        setPromotores(data);
    } catch (err: any) {
        setErro(err.message || 'Erro desconhecido');
    }
    setLoading(false);
    }

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

      <table
        style={{
          width: '100%',
          borderCollapse: 'collapse',
          marginTop: 10,
          backgroundColor: '#2a2a3d',
          borderRadius: 8,
          overflow: 'hidden',
        }}
      >
        <thead>
          <tr style={{ backgroundColor: '#444477', textTransform: 'uppercase' }}>
            <th style={{ padding: '10px 12px' }}>User ID</th>
            <th style={{ padding: '10px 12px' }}>User ID MP</th>
            <th style={{ padding: '10px 12px' }}>Nome</th>
            <th style={{ padding: '10px 12px' }}>Saldo</th>
            <th style={{ padding: '10px 12px' }}>Ativo</th>
          </tr>
        </thead>
        <tbody>
          {promotores.length === 0 && !loading && (
            <tr>
              <td colSpan={5} style={{ textAlign: 'center', padding: 20, color: '#999' }}>
                Nenhum promotor encontrado
              </td>
            </tr>
          )}
          {promotores.map(p => (
            <tr
              key={p.user_id}
              style={{
                backgroundColor: p.ativo ? 'transparent' : '#5a1a1a',
                cursor: 'default',
                transition: 'background-color 0.3s',
              }}
              onMouseEnter={e => (e.currentTarget.style.backgroundColor = '#444466')}
              onMouseLeave={e =>
                (e.currentTarget.style.backgroundColor = p.ativo ? 'transparent' : '#5a1a1a')
              }
            >
              <td style={{ padding: '8px 12px', textAlign: 'center' }}>{p.user_id}</td>
              <td style={{ padding: '8px 12px', textAlign: 'center' }}>{p.user_id_mp}</td>
              <td style={{ padding: '8px 12px' }}>{p.nome || '-'}</td>
              <td style={{ padding: '8px 12px', textAlign: 'right' }}>
                R$ {p.saldo.toFixed(2)}
              </td>
              <td
                style={{
                  padding: '8px 12px',
                  textAlign: 'center',
                  color: p.ativo ? '#4caf50' : '#f44336',
                  fontWeight: '700',
                }}
              >
                {p.ativo ? 'Ativo ✅' : 'Bloqueado ❌'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
