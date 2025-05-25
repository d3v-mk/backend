from sqlalchemy.orm import Session
from panopoker.usuarios.models.usuario import Usuario


def conq_beta_tester(usuario: Usuario, db: Session):
    from panopoker.usuarios.models.estatisticas import EstatisticasJogador
    from datetime import datetime, timezone

    estatisticas = EstatisticasJogador(usuario_id=usuario.id)
    if datetime.now(timezone.utc) < datetime(2025, 7, 1, tzinfo=timezone.utc):
        estatisticas.beta_tester = 1
    db.add(estatisticas)
    db.commit()