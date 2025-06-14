// src/types.ts
export interface Promotor {
  id: number;
  user_id: number;
  user_id_mp: string;
  nome: string | null;
  slug: string | null;
  access_token: string | null;
  saldo: number;
  bloqueado: boolean;
  ultima_atividade: string | null;
}
