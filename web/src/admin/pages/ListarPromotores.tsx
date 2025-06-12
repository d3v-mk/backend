import { FormListarPromotores } from '../components/FormListarPromotores';

export function ListarPromotores() {
  return (
    <div
      style={{
        maxWidth: 1100,
        margin: '30px auto',
        padding: 20,
        backgroundColor: '#1e1e2f',
        borderRadius: 8,
        boxShadow: '0 4px 12px rgba(0,0,0,0.4)',
        color: '#eee',
        fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
      }}
    >
      <h2
        style={{
          marginBottom: 20,
          fontWeight: '700',
          fontSize: '1.8rem',
          textAlign: 'center',
          color: '#FFD700',
          textShadow: '0 0 6px #FFD700aa',
        }}
      >
        👑 Painel de Promotores
      </h2>

      <div
        style={{
          overflowX: 'auto',
          paddingBottom: 10,
          borderRadius: 6,
          backgroundColor: '#2a2a3d',
        }}
      >
        <FormListarPromotores />
      </div>
    </div>
  );
}
