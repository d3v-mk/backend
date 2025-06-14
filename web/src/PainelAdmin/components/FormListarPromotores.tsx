// src/components/FormListarPromotores.tsx
import type { Promotor } from '@/types';

type Props = {
  promotores: Promotor[];
  onCopiarId: (id: number) => void;
};

export function FormListarPromotores({ promotores, onCopiarId }: Props) {
  return (
    <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: 10 }}>
      <thead>
        <tr style={{ backgroundColor: '#444477' }}>
          <th>Nome</th>
          <th>ID</th>
          <th>Slug</th>
          <th>Access Token</th>
          <th>Saldo a Repassar</th>
          <th>Status</th>
          <th>Última Atividade</th>
          <th>Ações</th>
        </tr>
      </thead>
      <tbody>
        {promotores.length === 0 && (
          <tr>
            <td colSpan={8} style={{ textAlign: 'center', padding: 20 }}>
              Nenhum promotor encontrado
            </td>
          </tr>
        )}
        {promotores.map(p => (
          <tr key={p.id} style={{ backgroundColor: p.bloqueado ? '#5a1a1a' : 'transparent' }}>
            <td>{p.nome || '-'}</td>
            <td>
              {p.id}{' '}
              <button onClick={() => onCopiarId(p.id)} style={{ cursor: 'pointer' }}>📋</button>
            </td>
            <td>{p.slug || '-'}</td>
            <td>{p.access_token ? '✅' : '❌'}</td>
            <td>R$ {p.saldo.toFixed(2)}</td>
            <td style={{ color: p.bloqueado ? 'red' : '#0f0' }}>
              {p.bloqueado ? 'Bloqueado ❌' : 'Liberado ✅'}
            </td>
            <td>{p.ultima_atividade || '⏳ Sem atividade recente'}</td>
            <td>
              <details>
                <summary style={{ cursor: 'pointer' }}>Ações ▼</summary>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                  <button disabled={!p.bloqueado}>Desbloquear ✅</button>
                  {p.slug && (
                    <button
                      onClick={() => confirm('Apagar loja?') && console.log('Apagar loja de', p.id)}
                      style={{ color: 'red' }}
                    >
                      Apagar Loja 🗑️
                    </button>
                  )}
                </div>
              </details>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
