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
import traceback

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
        print(f"[WS][ACCEPTED] mesa_id={mesa_id}")

        # Autenticação
        auth_msg = await websocket.receive_json()
        print(f"[WS][AUTH_MSG] {auth_msg}")
        if not (isinstance(auth_msg, dict) and auth_msg.get("type") == "auth" and auth_msg.get("token")):
            print(f"[WS][AUTH_FAIL] msg={auth_msg}")
            await websocket.close(code=4003)
            return
        try:
            payload = decode_jwt(auth_msg["token"])
            user_id = int(payload["sub"])
            print(f"[WS][AUTH_OK] user_id={user_id}")
        except Exception as e:
            print("[WS][AUTH_JWT_EXCEPTION]", e)
            traceback.print_exc()
            await websocket.close(code=4001)
            return

        # Conexão multi-device
        await connection_manager.connect(mesa_id, user_id, websocket)
        print(f"[WS][CONNECT] Mesa {mesa_id} conectado, user_id: {user_id} devices={len(connection_manager.active_connections.get((mesa_id,user_id),[]))}")

        # Inicializa motores se for mesa real
        if mesa_id != 0:
            mesa = db.query(Mesa).get(mesa_id)
            print(f"[WS][LOAD_MESA] mesa={repr(mesa)}")
            if not mesa:
                print(f"[WS][MESA_NOT_FOUND] mesa_id={mesa_id}")
                await websocket.close(code=4004)
                return
            controlador_acoes = ExecutorDeAcoes(mesa, db)
            controlador_mesa = ControladorDeMesa(mesa, db)
            controlador_partida = ControladorDePartida(mesa, db)

        # Loop principal
        while True:
            try:
                msg = await websocket.receive_json()
                print(f"[WS][RECEIVED_MSG] {msg}")
            except WebSocketDisconnect:
                print(f"[WS][DISCONNECT] mesa {mesa_id}, user_id {user_id}")
                break
            except RuntimeError as e:
                print(f"[WS][RUNTIME_SOCKET_FECHADO] mesa {mesa_id}, user_id {user_id} err={e}")
                traceback.print_exc()
                break

            acao = msg.get("action")
            valor = msg.get("valor")
            print(f"[WS][ACTION] user_id={user_id} mesa_id={mesa_id} acao={acao} valor={valor}")

            # Matchmaking
            if mesa_id == 0 and acao == "matchmaking":
                tipo = msg.get("tipo")
                buy_in = {"bronze":0.30, "prata":2, "ouro":5}.get(tipo)
                print(f"[WS][MATCHMAKING] tipo={tipo} buy_in={buy_in}")
                if buy_in:
                    mesa_disp = matchmaking_helper(db, buy_in)
                    print(f"[WS][MATCH_FOUND] {mesa_disp}")
                    try:
                        await websocket.send_json({"evento":"match_encontrado","mesa_id":mesa_disp.id})
                    except Exception as e:
                        print(f"[WS][EXC_SEND_JSON][MATCH] {type(e)} {e}")
                        traceback.print_exc()
                else:
                    print(f"[WS][MATCH_NOT_FOUND]")
                    try:
                        await websocket.send_json({"evento":"match_nao_encontrado"})
                    except Exception as e:
                        print(f"[WS][EXC_SEND_JSON][NO_MATCH] {type(e)} {e}")
                        traceback.print_exc()
                continue

            # Ações mesa real
            if mesa_id != 0:
                try:
                    db.refresh(mesa)
                except Exception as e:
                    print(f"[WS][DB_REFRESH_EXCEPTION] {e}")
                    traceback.print_exc()

                usuario = db.query(Usuario).get(user_id)
                print(f"[WS][USUARIO] {usuario}")
                if not usuario:
                    print(f"[WS][USUARIO_NAO_ENCONTRADO] id={user_id}")
                    continue

                try:
                    # Entrada ou saída
                    if acao == "entrar":
                        print(f"[WS][ENTRAR] user_id={user_id}")
                        await controlador_mesa.entrar_na_mesa(usuario)
                        print(f"[WS][ENTRAR_OK]")
                        if mesa.status == MesaStatus.aberta and len(mesa.jogadores) >= 2:
                            await controlador_partida.iniciar_partida()
                            print(f"[WS][PARTIDA_INICIADA]")
                            db.commit()
                            print(f"[WS][DB_COMMIT] apos iniciar_partida")
                        try:
                            await connection_manager.broadcast_mesa(mesa_id, {"evento":"mesa_atualizada"})
                        except Exception as e:
                            print(f"[WS][EXC_BROADCAST][ENTRAR] {type(e)} {e}")
                            traceback.print_exc()

                    elif acao == "sair":
                        print(f"[WS][SAIR] user_id={user_id}")
                        usuario = db.query(Usuario).get(user_id)
                        if not usuario:
                            try:
                                await websocket.send_json({"error":"404: Usuário não encontrado"})
                            except Exception as e:
                                print(f"[WS][EXC_SEND_JSON][SAIR][USUARIO] {type(e)} {e}")
                                traceback.print_exc()
                        else:
                            try:
                                await controlador_mesa.sair_da_mesa(usuario)
                                print(f"[WS][SAIR_OK]")
                                await connection_manager.broadcast_mesa(mesa_id, {"evento":"mesa_atualizada"})
                            except HTTPException as he:
                                try:
                                    await websocket.send_json({"error": f"{he.status_code}: {he.detail}"})
                                except Exception as e:
                                    print(f"[WS][EXC_SEND_JSON][SAIR][HTTP] {type(e)} {e}")
                                    traceback.print_exc()
                            except Exception as e:
                                print(f"[WS][EXC_SAIR_MESA] {e}")
                                traceback.print_exc()
                                break

                    # Ações de jogo
                    elif acao in ("call","fold","check","raise","allin"):
                        print(f"[WS][ACAO_JOGO] acao={acao} user_id={user_id}")
                        if mesa.status == MesaStatus.aberta:
                            await controlador_partida.iniciar_partida()
                            print(f"[WS][PARTIDA_INICIADA_AUTO]")
                        try:
                            if acao == "raise":
                                await controlador_acoes.acao_raise(user_id, valor)
                            else:
                                await getattr(controlador_acoes, f"acao_{acao}")(user_id)
                            db.commit()
                            print(f"[WS][DB_COMMIT] apos acao {acao}")
                            try:
                                await connection_manager.broadcast_mesa(mesa_id, {"evento":"mesa_atualizada"})
                                print(f"[WS][BROADCAST_OK]")
                            except Exception as e:
                                print(f"[WS][EXC_BROADCAST][JOGO] {type(e)} {e}")
                                traceback.print_exc()
                        except HTTPException as he:
                            try:
                                await websocket.send_json({"error":f"{he.status_code}: {he.detail}"})
                            except Exception as e:
                                print(f"[WS][EXC_SEND_JSON][JOGO][HTTP] {type(e)} {e}")
                                traceback.print_exc()
                            continue
                        except Exception as e:
                            print(f"[WS][ERRO_INESPERADO_JOGO] {e}")
                            traceback.print_exc()
                            break

                    else:
                        print(f"[WS][ACAO_DESCONHECIDA] acao={acao}")
                        raise HTTPException(status_code=400, detail=f"Ação desconhecida: {acao}")

                    print(f"[WS][ACAO_REALIZADA] Mesa {mesa_id} AÇÃO: {acao} (user_id={user_id})")

                except HTTPException as he:
                    try:
                        await websocket.send_json({"error":f"{he.status_code}: {he.detail}"})
                    except Exception as e:
                        print(f"[WS][EXC_SEND_JSON][LOOP][HTTP] {type(e)} {e}")
                        traceback.print_exc()
                    continue
                except Exception as e:
                    print(f"[WS][ERRO_INESPERADO_LOOP] {e}")
                    traceback.print_exc()
                    break

        # fim loop
    except Exception as e:
        print(f"[WS][ERRO_GERAL] mesa {mesa_id}, user_id {user_id}: {e}")
        traceback.print_exc()
    finally:
        try:
            print(f"[WS][FINALLY] Desconectando mesa={mesa_id} user={user_id}")
            connection_manager.disconnect(mesa_id, user_id, websocket)
            if hasattr(db, 'is_active'):
                print(f"[WS][FINALLY] DB is_active={db.is_active}")
            try:
                db.rollback()  # Garante rollback se ficou sujo
                print(f"[WS][FINALLY] DB rollback realizado")
            except Exception as e:
                print(f"[WS][FINALLY][DB_ROLLBACK_EXCEPTION] {e}")
                traceback.print_exc()
        except Exception as e:
            print(f"[WS][FINALLY][DISCONNECT_EXCEPTION] {e}")
            traceback.print_exc()
