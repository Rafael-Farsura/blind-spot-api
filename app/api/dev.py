from flask import Blueprint, jsonify

from app.domain import enums
from app.extensions import db
from app.models import Comentario, Inconsistencia, Job, JobEvento
from app.services.job_service import JobService

bp = Blueprint("dev", __name__)


@bp.post("/dev/seed")
def seed():
    """Recria base de demonstração (ambiente local).
    ---
    tags:
      - Dev
    responses:
      200:
        description: Seed aplicado
    """
    # limpa na ordem das FKs
    Comentario.query.delete()
    Inconsistencia.query.delete()
    JobEvento.query.delete()
    Job.query.delete()
    db.session.commit()

    jobs = JobService()
    job = jobs.criar(
        competencia="2026-07",
        tipo=enums.JOB_TIPO_VARREDURA,
        observacao="Carga de demonstração",
    )
    job = jobs.executar(job.id, quantidade=3)

    from app.services.inconsistencia_service import InconsistenciaService

    inconsistencias = InconsistenciaService()
    primeira = inconsistencias.listar(job_id=job.id)[0]
    inconsistencias.comentar(
        primeira.id,
        autor="Ana",
        texto="Vou conferir o valor no livro auxiliar.",
    )
    inconsistencias.atualizar_status(
        primeira.id,
        enums.INCONSISTENCIA_EM_ANALISE,
    )

    return jsonify(
        {
            "ok": True,
            "job_id": job.id,
            "inconsistencias": job.linhas_processadas,
            "mensagem": "Base de demonstração carregada.",
        }
    )
