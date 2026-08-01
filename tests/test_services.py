import pytest

from app.domain import enums
from app.domain.errors import ConflictError, ValidationError
from app.services.inconsistencia_service import InconsistenciaService
from app.services.job_service import JobService


def test_criar_e_executar_job(app):
    service = JobService()
    job = service.criar(competencia="2026-07", observacao="demo")
    assert job.status == enums.JOB_STATUS_PENDENTE

    job = service.executar(job.id, quantidade=3)
    assert job.status == enums.JOB_STATUS_CONCLUIDO
    assert job.linhas_processadas == 3
    assert len(job.eventos) >= 2

    inconsistencias = InconsistenciaService().listar(job_id=job.id)
    assert len(inconsistencias) == 3


def test_executar_job_concluido_conflito(app):
    service = JobService()
    job = service.criar(competencia="2026-07")
    service.executar(job.id)
    with pytest.raises(ConflictError):
        service.executar(job.id)


def test_resolver_inconsistencia(app):
    jobs = JobService()
    job = jobs.criar(competencia="2026-07")
    jobs.executar(job.id, quantidade=1)

    svc = InconsistenciaService()
    item = svc.listar(job_id=job.id)[0]
    atualizado = svc.atualizar_status(
        item.id,
        enums.INCONSISTENCIA_RESOLVIDA,
        parecer="Conferido com o analista responsável.",
    )
    assert atualizado.status == enums.INCONSISTENCIA_RESOLVIDA
    assert atualizado.fechado_em is not None


def test_criar_job_sem_competencia(app):
    with pytest.raises(ValidationError):
        JobService().criar(competencia="  ")
