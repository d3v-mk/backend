// src/types.ts
export interface Promotor {
  id: number;
  nome: string;
  slug: string;
  access_token: string | null;
  saldo_repassar: number;
  bloqueado: boolean;
  ultima_atividade?: string | null;
}
