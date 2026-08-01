from datetime import datetime, timezone

from app.domain import enums
from app.extensions import db


def _now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Job(db.Model):
    __tablename__ = "job"
    __table_args__ = (
        db.Index("ix_job_status", "status"),
        db.Index("ix_job_criado_em", "criado_em"),
    )

    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(40), nullable=False, default=enums.JOB_TIPO_VARREDURA)
    competencia = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), nullable=False, default=enums.JOB_STATUS_PENDENTE)
    observacao = db.Column(db.Text, nullable=True)
    criado_em = db.Column(db.DateTime, nullable=False, default=_now)
    atualizado_em = db.Column(db.DateTime, nullable=False, default=_now, onupdate=_now)
    iniciado_em = db.Column(db.DateTime, nullable=True)
    finalizado_em = db.Column(db.DateTime, nullable=True)
    linhas_processadas = db.Column(db.Integer, nullable=False, default=0)

    eventos = db.relationship(
        "JobEvento",
        back_populates="job",
        cascade="all, delete-orphan",
        order_by="JobEvento.criado_em",
    )
    inconsistencias = db.relationship(
        "Inconsistencia",
        back_populates="job",
        lazy="dynamic",
    )


class JobEvento(db.Model):
    __tablename__ = "job_evento"

    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey("job.id", ondelete="CASCADE"), nullable=False)
    tipo = db.Column(db.String(30), nullable=False)
    mensagem = db.Column(db.Text, nullable=False)
    criado_em = db.Column(db.DateTime, nullable=False, default=_now)

    job = db.relationship("Job", back_populates="eventos")


class Inconsistencia(db.Model):
    __tablename__ = "inconsistencia"
    __table_args__ = (
        db.Index("ix_inconsistencia_status", "status"),
        db.Index("ix_inconsistencia_job_id", "job_id"),
        db.Index("ix_inconsistencia_criado_em", "criado_em"),
    )

    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey("job.id"), nullable=True)
    origem = db.Column(db.String(20), nullable=False)
    tipo = db.Column(db.String(40), nullable=False)
    severidade = db.Column(db.String(10), nullable=False)
    status = db.Column(db.String(20), nullable=False, default=enums.INCONSISTENCIA_ABERTA)
    titulo = db.Column(db.String(120), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    referencia = db.Column(db.String(80), nullable=True)
    parecer = db.Column(db.Text, nullable=True)
    criado_em = db.Column(db.DateTime, nullable=False, default=_now)
    atualizado_em = db.Column(db.DateTime, nullable=False, default=_now, onupdate=_now)
    fechado_em = db.Column(db.DateTime, nullable=True)

    job = db.relationship("Job", back_populates="inconsistencias")
    comentarios = db.relationship(
        "Comentario",
        back_populates="inconsistencia",
        cascade="all, delete-orphan",
        order_by="Comentario.criado_em",
    )


class Comentario(db.Model):
    __tablename__ = "comentario"
    __table_args__ = (
        db.Index("ix_comentario_inconsistencia_criado", "inconsistencia_id", "criado_em"),
    )

    id = db.Column(db.Integer, primary_key=True)
    inconsistencia_id = db.Column(
        db.Integer,
        db.ForeignKey("inconsistencia.id", ondelete="CASCADE"),
        nullable=False,
    )
    autor = db.Column(db.String(80), nullable=False)
    texto = db.Column(db.Text, nullable=False)
    criado_em = db.Column(db.DateTime, nullable=False, default=_now)

    inconsistencia = db.relationship("Inconsistencia", back_populates="comentarios")
