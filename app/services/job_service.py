from datetime import datetime, timezone

from app.domain import enums
from app.domain.errors import NotFoundError, ValidationError
from app.domain.generator import VarreduraGenerator
from app.domain.transitions import ensure_job_can_delete, ensure_job_can_run
from app.models import Inconsistencia, Job
from app.repositories.inconsistencia_repository import InconsistenciaRepository
from app.repositories.job_repository import JobRepository


def _now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class JobService:
    def __init__(self, jobs=None, inconsistencias=None, generator=None):
        self.jobs = jobs or JobRepository()
        self.inconsistencias = inconsistencias or InconsistenciaRepository()
        self.generator = generator or VarreduraGenerator()

    def criar(self, competencia, tipo=None, observacao=None):
        competencia = (competencia or "").strip()
        if not competencia:
            raise ValidationError("Competência é obrigatória.", {"competencia": "obrigatorio"})

        job = Job(
            tipo=(tipo or enums.JOB_TIPO_VARREDURA).strip() or enums.JOB_TIPO_VARREDURA,
            competencia=competencia,
            status=enums.JOB_STATUS_PENDENTE,
            observacao=(observacao or "").strip() or None,
        )
        self.jobs.add(job)
        self.jobs.commit()
        return job

    def listar(self, status=None):
        return self.jobs.list(status=status)

    def obter(self, job_id):
        job = self.jobs.get(job_id)
        if not job:
            raise NotFoundError("Job não encontrado.")
        return job

    def executar(self, job_id, quantidade=None):
        job = self.obter(job_id)
        ensure_job_can_run(job.status)

        try:
            if job.status == enums.JOB_STATUS_FALHA:
                self.inconsistencias.delete_by_job(job.id)
                self.jobs.clear_eventos(job.id)

            agora = _now()
            job.status = enums.JOB_STATUS_EM_EXECUCAO
            job.iniciado_em = agora
            job.finalizado_em = None
            job.atualizado_em = agora
            self.jobs.add_evento(job.id, enums.EVENTO_INICIO, "Checagem iniciada.")
            self.jobs.flush()

            payloads = self.generator.gerar(job, quantidade=quantidade)
            registros = [
                Inconsistencia(
                    job_id=p["job_id"],
                    origem=p["origem"],
                    tipo=p["tipo"],
                    severidade=p["severidade"],
                    status=p["status"],
                    titulo=p["titulo"],
                    descricao=p["descricao"],
                    referencia=p["referencia"],
                )
                for p in payloads
            ]
            self.inconsistencias.add_many(registros)

            job.linhas_processadas = len(registros)
            job.status = enums.JOB_STATUS_CONCLUIDO
            job.finalizado_em = _now()
            job.atualizado_em = job.finalizado_em
            self.jobs.add_evento(
                job.id,
                enums.EVENTO_FIM,
                f"Checagem concluída com {len(registros)} inconsistência(s).",
            )
            self.jobs.commit()
            return job
        except Exception:
            self.jobs.rollback()
            job = self.jobs.get(job_id)
            if job:
                job.status = enums.JOB_STATUS_FALHA
                job.finalizado_em = _now()
                job.atualizado_em = job.finalizado_em
                self.jobs.add_evento(job.id, enums.EVENTO_ERRO, "Falha na execução da checagem.")
                self.jobs.commit()
            raise

    def excluir(self, job_id):
        job = self.obter(job_id)
        qtd = self.inconsistencias.count_by_job(job.id)
        ensure_job_can_delete(job.status, has_inconsistencias=qtd > 0)
        self.jobs.delete(job)
        self.jobs.commit()
