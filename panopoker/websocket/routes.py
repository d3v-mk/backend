from fastapi import WebSocket, WebSocketDisconnect, APIRouter, HTTPException
from panopoker.core.security import decode_jwt
from panopoker.poker.game.ExecutorDeAcoes import ExecutorDeAcoes
from panopoker.poker.game.ControladorDeMesa import ControladorDeMesa
from panopoker.poker.game.ControladorDePartida import ControladorDePartida
from panopoker.poker.models.mesa import Mesa, MesaStatus
from panopoker.core.database import get_db
from panopoker.websocket.manager import connection_manager
from panopoker.websocket.utils.matchmaking_helper import matchmaking_helper
from panopoker.usuarios.models.usuario import Usuario

router = APIRouter()

@router.websocket("/ws/mesa/{mesa_id}")
async def websocket_mesa(websocket: WebSocket, mesa_id: int):
    db = next(get_db())
    user_id = None
    mesa = None
    controlador_acoes = None
    controlador_mesa = None
    controlador_partida = None

    try:
        await websocket.accept()

        # Autenticação
        auth_msg = await websocket.receive_json()
        if not (isinstance(auth_msg, dict) and auth_msg.get("type") == "auth" and auth_msg.get("token")):
            await websocket.close(code=4003)
            return
        try:
            payload = decode_jwt(auth_msg["token"])
            user_id = int(payload["sub"])
        except Exception as e:
            print("Erro validação JWT:", e)
            await websocket.close(code=4001)
            return

        # Conexão multi-device
        await connection_manager.connect(mesa_id, user_id, websocket)
        print(f"[WS] Mesa {mesa_id} conectado, user_id: {user_id} devices={len(connection_manager.active_connections.get((mesa_id,user_id),[]))}")

        # Inicializa motores se for mesa real
        if mesa_id != 0:
            mesa = db.query(Mesa).get(mesa_id)
            if not mesa:
                await websocket.close(code=4004)
                return
            controlador_acoes = ExecutorDeAcoes(mesa, db)
            controlador_mesa = ControladorDeMesa(mesa, db)
            controlador_partida = ControladorDePartida(mesa, db)

        # Loop principal
        while True:
            try:
                msg = await websocket.receive_json()
            except WebSocketDisconnect:
                print(f"[WS] DISCONNECT mesa {mesa_id}, user_id {user_id}")
                break
            except RuntimeError:
                print(f"[WS] socket fechado mesa {mesa_id}, user_id {user_id}")
                break

            acao = msg.get("action")
            valor = msg.get("valor")
            print(f"[WS] RECEBIDO user_id={user_id}: {msg}")

            # Matchmaking
            if mesa_id == 0 and acao == "matchmaking":
                tipo = msg.get("tipo")
                buy_in = {"bronze":0.30, "prata":2, "ouro":5}.get(tipo)
                if buy_in:
                    mesa_disp = matchmaking_helper(db, buy_in)
                    if mesa_disp:
                        await websocket.send_json({"evento":"match_encontrado","mesa_id":mesa_disp.id})
                    else:
                        await websocket.send_json({"evento":"match_nao_encontrado"})
                else:
                    await websocket.send_json({"evento":"match_nao_encontrado"})
                continue

            # Ações mesa real
            if mesa_id != 0:
                # atualiza estado no DB
                db.refresh(mesa)

                usuario = db.query(Usuario).get(user_id)
                if not usuario:
                    print(f"[ERRO] Usuario id={user_id} não encontrado")
                    continue

                try:
                    # Entrada ou saída
                    if acao == "entrar":
                        await controlador_mesa.entrar_na_mesa(usuario)
                        if mesa.status == MesaStatus.aberta and len(mesa.jogadores) >= 2:
                            await controlador_partida.iniciar_partida()
                            db.commit()
                        await connection_manager.broadcast_mesa(mesa_id, {"evento":"mesa_atualizada"})

                    elif acao == "sair":
                        # primeiro garante que você tem o model Usuario
                        usuario = db.query(Usuario).get(user_id)
                        if not usuario:
                            await websocket.send_json({"error":"404: Usuário não encontrado"})
                        else:
                            # passe o objeto, não o ID
                            try:
                                await controlador_mesa.sair_da_mesa(usuario)
                                await connection_manager.broadcast_mesa(mesa_id, {"evento":"mesa_atualizada"})
                            except HTTPException as he:
                                await websocket.send_json({"error": f"{he.status_code}: {he.detail}"})
                            except Exception as e:
                                print(f"[WS] erro ao sair_da_mesa: {e}")
                                break


                    # Ações de jogo
                    elif acao in ("call","fold","check","raise","allin"):
                        if mesa.status == MesaStatus.aberta:
                            await controlador_partida.iniciar_partida()
                        if acao == "raise":
                            await controlador_acoes.acao_raise(user_id, valor)
                        else:
                            await getattr(controlador_acoes, f"acao_{acao}")(user_id)
                        db.commit()
                        await connection_manager.broadcast_mesa(mesa_id, {"evento":"mesa_atualizada"})

                    else:
                        raise HTTPException(status_code=400, detail=f"Ação desconhecida: {acao}")

                    print(f"[WS] Mesa {mesa_id} AÇÃO: {acao} (user_id={user_id})")

                except HTTPException as he:
                    # erro de negócio (ex: fora de vez) não derruba a conexão
                    await websocket.send_json({"error":f"{he.status_code}: {he.detail}"})
                    continue
                except Exception as e:
                    # outros erros, encerra loop
                    print(f"[WS] ERRO inesperado ao processar {acao}: {e}")
                    break

        # fim loop
    except Exception as e:
        print(f"[WS] ERRO geral mesa {mesa_id}, user_id {user_id}: {e}")
    finally:
        connection_manager.disconnect(mesa_id, user_id, websocket)
