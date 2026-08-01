from flask import Blueprint, jsonify, request

from app.api.serializers import job_to_dict
from app.repositories.inconsistencia_repository import InconsistenciaRepository
from app.services.job_service import JobService

bp = Blueprint("jobs", __name__)


@bp.post("/jobs")
def criar_job():
    """Cria um job de checagem.
    ---
    tags:
      - Jobs
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - competencia
          properties:
            competencia:
              type: string
              example: "2026-07"
            tipo:
              type: string
              example: varredura_divergencias
            observacao:
              type: string
    responses:
      201:
        description: Job criado
      400:
        description: Validação
    """
    payload = request.get_json(silent=True) or {}
    job = JobService().criar(
        competencia=payload.get("competencia"),
        tipo=payload.get("tipo"),
        observacao=payload.get("observacao"),
    )
    return jsonify(job_to_dict(job)), 201


@bp.get("/jobs")
def listar_jobs():
    """Lista jobs (filtro opcional por status).
    ---
    tags:
      - Jobs
    parameters:
      - in: query
        name: status
        type: string
        required: false
    responses:
      200:
        description: Lista de jobs
    """
    status = request.args.get("status")
    jobs = JobService().listar(status=status)
    repo = InconsistenciaRepository()
    data = [
        job_to_dict(j, inconsistencias_count=repo.count_by_job(j.id))
        for j in jobs
    ]
    return jsonify(data)


@bp.get("/jobs/<int:job_id>")
def detalhar_job(job_id):
    """Detalhe do job com eventos.
    ---
    tags:
      - Jobs
    parameters:
      - in: path
        name: job_id
        type: integer
        required: true
    responses:
      200:
        description: Job encontrado
      404:
        description: Não encontrado
    """
    job = JobService().obter(job_id)
    count = InconsistenciaRepository().count_by_job(job.id)
    return jsonify(
        job_to_dict(job, include_eventos=True, inconsistencias_count=count)
    )


@bp.post("/jobs/<int:job_id>/executar")
def executar_job(job_id):
    """Executa a checagem do job (síncrona, simulada).
    ---
    tags:
      - Jobs
    parameters:
      - in: path
        name: job_id
        type: integer
        required: true
      - in: body
        name: body
        required: false
        schema:
          type: object
          properties:
            quantidade:
              type: integer
              example: 3
    responses:
      200:
        description: Job concluído
      404:
        description: Não encontrado
      409:
        description: Estado inválido para execução
    """
    payload = request.get_json(silent=True) or {}
    job = JobService().executar(job_id, quantidade=payload.get("quantidade"))
    count = InconsistenciaRepository().count_by_job(job.id)
    return jsonify(
        job_to_dict(job, include_eventos=True, inconsistencias_count=count)
    )


@bp.delete("/jobs/<int:job_id>")
def excluir_job(job_id):
    """Exclui job pendente/cancelado sem inconsistências.
    ---
    tags:
      - Jobs
    parameters:
      - in: path
        name: job_id
        type: integer
        required: true
    responses:
      204:
        description: Removido
      404:
        description: Não encontrado
      409:
        description: Exclusão não permitida
    """
    JobService().excluir(job_id)
    return "", 204
