from flask import Blueprint, jsonify, request

from app.api.serializers import comentario_to_dict, inconsistencia_to_dict
from app.services.inconsistencia_service import InconsistenciaService

bp = Blueprint("inconsistencias", __name__)


@bp.get("/inconsistencias")
def listar_inconsistencias():
    """Lista inconsistências.
    ---
    tags:
      - Inconsistencias
    parameters:
      - in: query
        name: status
        type: string
        required: false
      - in: query
        name: job_id
        type: integer
        required: false
    responses:
      200:
        description: Lista
    """
    status = request.args.get("status")
    job_id = request.args.get("job_id", type=int)
    itens = InconsistenciaService().listar(status=status, job_id=job_id)
    return jsonify([inconsistencia_to_dict(i) for i in itens])


@bp.post("/inconsistencias")
def criar_inconsistencia():
    """Abre inconsistência manual.
    ---
    tags:
      - Inconsistencias
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - tipo
            - severidade
            - titulo
            - descricao
          properties:
            tipo:
              type: string
            severidade:
              type: string
            titulo:
              type: string
            descricao:
              type: string
            referencia:
              type: string
    responses:
      201:
        description: Criada
      400:
        description: Validação
    """
    payload = request.get_json(silent=True) or {}
    item = InconsistenciaService().criar_manual(
        tipo=payload.get("tipo"),
        severidade=payload.get("severidade"),
        titulo=payload.get("titulo"),
        descricao=payload.get("descricao"),
        referencia=payload.get("referencia"),
    )
    return jsonify(inconsistencia_to_dict(item)), 201


@bp.get("/inconsistencias/<int:item_id>")
def detalhar_inconsistencia(item_id):
    """Detalhe com comentários.
    ---
    tags:
      - Inconsistencias
    parameters:
      - in: path
        name: item_id
        type: integer
        required: true
    responses:
      200:
        description: Encontrada
      404:
        description: Não encontrada
    """
    item = InconsistenciaService().obter(item_id)
    return jsonify(inconsistencia_to_dict(item, include_comentarios=True))


@bp.patch("/inconsistencias/<int:item_id>")
def atualizar_inconsistencia(item_id):
    """Atualiza status (e parecer ao fechar).
    ---
    tags:
      - Inconsistencias
    parameters:
      - in: path
        name: item_id
        type: integer
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - status
          properties:
            status:
              type: string
            parecer:
              type: string
    responses:
      200:
        description: Atualizada
      400:
        description: Validação
      404:
        description: Não encontrada
      409:
        description: Transição inválida
    """
    payload = request.get_json(silent=True) or {}
    item = InconsistenciaService().atualizar_status(
        item_id,
        status=payload.get("status"),
        parecer=payload.get("parecer"),
    )
    return jsonify(inconsistencia_to_dict(item, include_comentarios=True))


@bp.post("/inconsistencias/<int:item_id>/comentarios")
def comentar_inconsistencia(item_id):
    """Adiciona comentário.
    ---
    tags:
      - Inconsistencias
    parameters:
      - in: path
        name: item_id
        type: integer
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - autor
            - texto
          properties:
            autor:
              type: string
            texto:
              type: string
    responses:
      201:
        description: Comentário criado
      400:
        description: Validação
      404:
        description: Não encontrada
    """
    payload = request.get_json(silent=True) or {}
    comentario = InconsistenciaService().comentar(
        item_id,
        autor=payload.get("autor"),
        texto=payload.get("texto"),
    )
    return jsonify(comentario_to_dict(comentario)), 201


@bp.delete("/inconsistencias/<int:item_id>")
def excluir_inconsistencia(item_id):
    """Remove inconsistência e comentários.
    ---
    tags:
      - Inconsistencias
    parameters:
      - in: path
        name: item_id
        type: integer
        required: true
    responses:
      204:
        description: Removida
      404:
        description: Não encontrada
    """
    InconsistenciaService().excluir(item_id)
    return "", 204
