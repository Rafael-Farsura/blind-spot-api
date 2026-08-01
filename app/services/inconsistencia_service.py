from datetime import datetime, timezone

from app.domain import enums
from app.domain.errors import NotFoundError, ValidationError
from app.domain.transitions import apply_inconsistencia_status, validate_origem
from app.models import Comentario, Inconsistencia
from app.repositories.inconsistencia_repository import InconsistenciaRepository


def _now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class InconsistenciaService:
    def __init__(self, repo=None):
        self.repo = repo or InconsistenciaRepository()

    def listar(self, status=None, job_id=None):
        return self.repo.list(status=status, job_id=job_id)

    def obter(self, inconsistencia_id):
        item = self.repo.get(inconsistencia_id)
        if not item:
            raise NotFoundError("Inconsistência não encontrada.")
        return item

    def criar_manual(self, tipo, severidade, titulo, descricao, referencia=None):
        tipo = (tipo or "").strip()
        severidade = (severidade or "").strip()
        titulo = (titulo or "").strip()
        descricao = (descricao or "").strip()

        campos = {}
        if tipo not in enums.TIPOS_INCONSISTENCIA:
            campos["tipo"] = "invalido"
        if severidade not in enums.SEVERIDADES:
            campos["severidade"] = "invalida"
        if not titulo:
            campos["titulo"] = "obrigatorio"
        if not descricao:
            campos["descricao"] = "obrigatorio"
        if campos:
            raise ValidationError("Dados inválidos para inconsistência.", campos)

        validate_origem(enums.ORIGEM_MANUAL, None)

        item = Inconsistencia(
            job_id=None,
            origem=enums.ORIGEM_MANUAL,
            tipo=tipo,
            severidade=severidade,
            status=enums.INCONSISTENCIA_ABERTA,
            titulo=titulo,
            descricao=descricao,
            referencia=(referencia or "").strip() or None,
        )
        self.repo.add(item)
        self.repo.commit()
        return item

    def atualizar_status(self, inconsistencia_id, status, parecer=None):
        item = self.obter(inconsistencia_id)
        novo, parecer_limpo = apply_inconsistencia_status(
            item.status, status, parecer=parecer
        )
        item.status = novo
        item.atualizado_em = _now()
        if novo in enums.INCONSISTENCIA_FECHADAS:
            item.parecer = parecer_limpo
            item.fechado_em = item.atualizado_em
        self.repo.commit()
        return item

    def comentar(self, inconsistencia_id, autor, texto):
        item = self.obter(inconsistencia_id)
        autor = (autor or "").strip()
        texto = (texto or "").strip()
        campos = {}
        if not autor:
            campos["autor"] = "obrigatorio"
        if not texto:
            campos["texto"] = "obrigatorio"
        elif len(texto) > 2000:
            campos["texto"] = "muito_longo"
        if campos:
            raise ValidationError("Comentário inválido.", campos)

        comentario = Comentario(
            inconsistencia_id=item.id,
            autor=autor,
            texto=texto,
        )
        self.repo.add_comentario(comentario)
        self.repo.commit()
        return comentario

    def excluir(self, inconsistencia_id):
        item = self.obter(inconsistencia_id)
        self.repo.delete(item)
        self.repo.commit()
