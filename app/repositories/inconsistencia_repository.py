from app.extensions import db
from app.models import Comentario, Inconsistencia


class InconsistenciaRepository:
    def add(self, inconsistencia):
        db.session.add(inconsistencia)
        return inconsistencia

    def add_many(self, itens):
        for item in itens:
            db.session.add(item)
        return itens

    def get(self, inconsistencia_id):
        return db.session.get(Inconsistencia, inconsistencia_id)

    def list(self, status=None, job_id=None):
        query = Inconsistencia.query.order_by(Inconsistencia.criado_em.desc())
        if status:
            query = query.filter_by(status=status)
        if job_id is not None:
            query = query.filter_by(job_id=job_id)
        return query.all()

    def count_by_job(self, job_id):
        return Inconsistencia.query.filter_by(job_id=job_id).count()

    def delete_by_job(self, job_id):
        Inconsistencia.query.filter_by(job_id=job_id).delete()

    def delete(self, inconsistencia):
        db.session.delete(inconsistencia)

    def add_comentario(self, comentario):
        db.session.add(comentario)
        return comentario

    def commit(self):
        db.session.commit()

    def flush(self):
        db.session.flush()

    def rollback(self):
        db.session.rollback()
