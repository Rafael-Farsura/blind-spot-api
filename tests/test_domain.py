import pytest

from app.domain import enums
from app.domain.errors import ConflictError, ValidationError
from app.domain.generator import VarreduraGenerator
from app.domain.transitions import (
    apply_inconsistencia_status,
    ensure_job_can_run,
    validate_origem,
)


def test_fechar_sem_parecer_falha():
    with pytest.raises(ValidationError):
        apply_inconsistencia_status(
            enums.INCONSISTENCIA_ABERTA,
            enums.INCONSISTENCIA_RESOLVIDA,
            parecer="curto",
        )


def test_fechar_com_parecer_ok():
    status, parecer = apply_inconsistencia_status(
        enums.INCONSISTENCIA_ABERTA,
        enums.INCONSISTENCIA_RESOLVIDA,
        parecer="Divergência conferida e ajustada no livro.",
    )
    assert status == enums.INCONSISTENCIA_RESOLVIDA
    assert "ajustada" in parecer


def test_job_concluido_nao_executa():
    with pytest.raises(ConflictError):
        ensure_job_can_run(enums.JOB_STATUS_CONCLUIDO)


def test_generator_quantidade_e_tipos():
    class FakeJob:
        id = 7

    itens = VarreduraGenerator().gerar(FakeJob(), quantidade=3)
    assert len(itens) == 3
    assert all(i["origem"] == enums.ORIGEM_JOB for i in itens)
    assert all(i["tipo"] in enums.TIPOS_INCONSISTENCIA for i in itens)


def test_origem_job_sem_job_id():
    with pytest.raises(ValidationError):
        validate_origem(enums.ORIGEM_JOB, None)
