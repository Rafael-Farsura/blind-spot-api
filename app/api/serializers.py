def job_to_dict(job, include_eventos=False, inconsistencias_count=None):
    data = {
        "id": job.id,
        "tipo": job.tipo,
        "competencia": job.competencia,
        "status": job.status,
        "observacao": job.observacao,
        "criado_em": _dt(job.criado_em),
        "atualizado_em": _dt(job.atualizado_em),
        "iniciado_em": _dt(job.iniciado_em),
        "finalizado_em": _dt(job.finalizado_em),
        "linhas_processadas": job.linhas_processadas,
    }
    if inconsistencias_count is not None:
        data["inconsistencias_count"] = inconsistencias_count
    if include_eventos:
        data["eventos"] = [evento_to_dict(e) for e in job.eventos]
    return data


def evento_to_dict(evento):
    return {
        "id": evento.id,
        "job_id": evento.job_id,
        "tipo": evento.tipo,
        "mensagem": evento.mensagem,
        "criado_em": _dt(evento.criado_em),
    }


def inconsistencia_to_dict(item, include_comentarios=False):
    data = {
        "id": item.id,
        "job_id": item.job_id,
        "origem": item.origem,
        "tipo": item.tipo,
        "severidade": item.severidade,
        "status": item.status,
        "titulo": item.titulo,
        "descricao": item.descricao,
        "referencia": item.referencia,
        "parecer": item.parecer,
        "criado_em": _dt(item.criado_em),
        "atualizado_em": _dt(item.atualizado_em),
        "fechado_em": _dt(item.fechado_em),
    }
    if include_comentarios:
        data["comentarios"] = [comentario_to_dict(c) for c in item.comentarios]
    return data


def comentario_to_dict(comentario):
    return {
        "id": comentario.id,
        "inconsistencia_id": comentario.inconsistencia_id,
        "autor": comentario.autor,
        "texto": comentario.texto,
        "criado_em": _dt(comentario.criado_em),
    }


def _dt(value):
    if value is None:
        return None
    return value.isoformat(sep=" ", timespec="seconds")
