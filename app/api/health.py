from flask import Blueprint, jsonify

bp = Blueprint("health", __name__)


@bp.get("/health")
def health():
    """Status da API.
    ---
    tags:
      - Sistema
    responses:
      200:
        description: API no ar
        schema:
          type: object
          properties:
            status:
              type: string
              example: ok
            service:
              type: string
              example: blind-spot-api
    """
    return jsonify(status="ok", service="blind-spot-api")
