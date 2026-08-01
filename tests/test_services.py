import pytest

from app.domain import enums
from app.domain.errors import ConflictError, ValidationError
from app.domain.generator import VarreduraGenerator
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


def test_excluir_job_pendente(app):
    from app.domain.errors import NotFoundError

    service = JobService()
    job = service.criar(competencia="2026-07")
    service.excluir(job.id)
    with pytest.raises(NotFoundError):
        service.obter(job.id)


def test_reexecutar_apos_falha(app, monkeypatch):
    service = JobService()
    job = service.criar(competencia="2026-07")

    def falhar(*args, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(service.generator, "gerar", falhar)
    with pytest.raises(RuntimeError):
        service.executar(job.id)

    job = service.obter(job.id)
    assert job.status == enums.JOB_STATUS_FALHA

    monkeypatch.setattr(service, "generator", VarreduraGenerator())
    job = service.executar(job.id, quantidade=2)
    assert job.status == enums.JOB_STATUS_CONCLUIDO
    assert job.linhas_processadas == 2


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


def test_criar_manual_e_comentar(app):
    svc = InconsistenciaService()
    item = svc.criar_manual(
        tipo=enums.TIPO_CNPJ_INVALIDO,
        severidade=enums.SEVERIDADE_MEDIA,
        titulo="CNPJ curto",
        descricao="Participante com identificador incompleto.",
        referencia="MAN-1",
    )
    assert item.origem == enums.ORIGEM_MANUAL
    comentario = svc.comentar(item.id, autor="Ana", texto="Vou validar.")
    assert comentario.id is not None
    svc.excluir(item.id)


def test_criar_manual_invalido(app):
    with pytest.raises(ValidationError):
        InconsistenciaService().criar_manual(
            tipo="x",
            severidade="y",
            titulo="",
            descricao="",
        )


def test_criar_job_sem_competencia(app):
    with pytest.raises(ValidationError):
        JobService().criar(competencia="  ")
