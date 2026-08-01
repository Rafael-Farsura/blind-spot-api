from app.domain import enums
from app.domain.errors import ConflictError, ValidationError


def ensure_job_can_run(status):
    if status not in enums.JOB_EXECUTABLE:
        raise ConflictError(
            "Job só pode ser executado quando está pendente ou em falha."
        )


def ensure_job_can_delete(status, has_inconsistencias):
    if status in (enums.JOB_STATUS_PENDENTE, enums.JOB_STATUS_CANCELADO) and not has_inconsistencias:
        return
    raise ConflictError(
        "Não é possível excluir este job. Remova as inconsistências "
        "ou cancele apenas jobs pendentes sem achados."
    )


def apply_inconsistencia_status(atual, novo, parecer=None):
    if novo not in enums.INCONSISTENCIA_STATUSES:
        raise ValidationError("Status de inconsistência inválido.", {"status": novo})

    if novo == atual:
        return atual, parecer

    if atual in enums.INCONSISTENCIA_FECHADAS:
        raise ConflictError("Inconsistência já encerrada não pode mudar de status.")

    permitidas = {
        enums.INCONSISTENCIA_ABERTA: {
            enums.INCONSISTENCIA_EM_ANALISE,
            enums.INCONSISTENCIA_RESOLVIDA,
            enums.INCONSISTENCIA_DESCARTADA,
        },
        enums.INCONSISTENCIA_EM_ANALISE: {
            enums.INCONSISTENCIA_ABERTA,
            enums.INCONSISTENCIA_RESOLVIDA,
            enums.INCONSISTENCIA_DESCARTADA,
        },
    }

    if novo not in permitidas.get(atual, set()):
        raise ConflictError(f"Transição de status inválida: {atual} → {novo}.")

    if novo in enums.INCONSISTENCIA_FECHADAS:
        texto = (parecer or "").strip()
        if len(texto) < enums.PARECER_MIN_CHARS:
            raise ValidationError(
                f"Parecer obrigatório com pelo menos {enums.PARECER_MIN_CHARS} caracteres.",
                {"parecer": "muito_curto"},
            )
        return novo, texto

    return novo, parecer


def validate_origem(origem, job_id):
    if origem == enums.ORIGEM_JOB and job_id is None:
        raise ValidationError(
            "Inconsistência com origem job precisa de job_id.",
            {"job_id": "obrigatorio"},
        )
    if origem == enums.ORIGEM_MANUAL and job_id is not None:
        raise ValidationError(
            "Inconsistência manual não deve ter job_id.",
            {"job_id": "deve_ser_nulo"},
        )
    if origem not in (enums.ORIGEM_JOB, enums.ORIGEM_MANUAL):
        raise ValidationError("Origem inválida.", {"origem": origem})
