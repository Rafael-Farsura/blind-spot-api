from app.extensions import db
from app.models import Job, JobEvento


class JobRepository:
    def add(self, job):
        db.session.add(job)
        return job

    def get(self, job_id):
        return db.session.get(Job, job_id)

    def list(self, status=None):
        query = Job.query.order_by(Job.criado_em.desc())
        if status:
            query = query.filter_by(status=status)
        return query.all()

    def delete(self, job):
        db.session.delete(job)

    def add_evento(self, job_id, tipo, mensagem):
        evento = JobEvento(job_id=job_id, tipo=tipo, mensagem=mensagem)
        db.session.add(evento)
        return evento

    def clear_eventos(self, job_id):
        JobEvento.query.filter_by(job_id=job_id).delete()

    def commit(self):
        db.session.commit()

    def flush(self):
        db.session.flush()

    def rollback(self):
        db.session.rollback()
