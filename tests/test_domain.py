import pytest

from app.domain import enums
from app.domain.errors import ConflictError, ValidationError
from app.domain.generator import VarreduraGenerator
from app.domain.transitions import (
    apply_inconsistencia_status,
    ensure_job_can_delete,
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


def test_status_igual_nao_muda():
    status, parecer = apply_inconsistencia_status(
        enums.INCONSISTENCIA_ABERTA,
        enums.INCONSISTENCIA_ABERTA,
        parecer=None,
    )
    assert status == enums.INCONSISTENCIA_ABERTA
    assert parecer is None


def test_status_invalido():
    with pytest.raises(ValidationError):
        apply_inconsistencia_status(enums.INCONSISTENCIA_ABERTA, "xyz")


def test_nao_reabre_fechada():
    with pytest.raises(ConflictError):
        apply_inconsistencia_status(
            enums.INCONSISTENCIA_RESOLVIDA,
            enums.INCONSISTENCIA_ABERTA,
        )


def test_em_analise_para_aberta():
    status, _ = apply_inconsistencia_status(
        enums.INCONSISTENCIA_EM_ANALISE,
        enums.INCONSISTENCIA_ABERTA,
    )
    assert status == enums.INCONSISTENCIA_ABERTA


def test_job_concluido_nao_executa():
    with pytest.raises(ConflictError):
        ensure_job_can_run(enums.JOB_STATUS_CONCLUIDO)


def test_delete_job_com_filhos_bloqueado():
    with pytest.raises(ConflictError):
        ensure_job_can_delete(enums.JOB_STATUS_PENDENTE, has_inconsistencias=True)


def test_delete_job_pendente_sem_filhos_ok():
    ensure_job_can_delete(enums.JOB_STATUS_PENDENTE, has_inconsistencias=False)


def test_generator_quantidade_e_tipos():
    class FakeJob:
        id = 7

    itens = VarreduraGenerator().gerar(FakeJob(), quantidade=3)
    assert len(itens) == 3
    assert all(i["origem"] == enums.ORIGEM_JOB for i in itens)
    assert all(i["tipo"] in enums.TIPOS_INCONSISTENCIA for i in itens)


def test_generator_quantidade_invalida():
    class FakeJob:
        id = 1

    with pytest.raises(ValidationError):
        VarreduraGenerator().gerar(FakeJob(), quantidade=0)
    with pytest.raises(ValidationError):
        VarreduraGenerator().gerar(FakeJob(), quantidade=99)


def test_origem_job_sem_job_id():
    with pytest.raises(ValidationError):
        validate_origem(enums.ORIGEM_JOB, None)


def test_origem_manual_com_job_id():
    with pytest.raises(ValidationError):
        validate_origem(enums.ORIGEM_MANUAL, 10)


def test_origem_invalida():
    with pytest.raises(ValidationError):
        validate_origem("xyz", None)
