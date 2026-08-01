from flask import jsonify

from app.domain.errors import ConflictError, DomainError, NotFoundError, ValidationError


def register_error_handlers(app):
    @app.errorhandler(ValidationError)
    def handle_validation(err):
        body = {"erro": err.message}
        if getattr(err, "fields", None):
            body["campos"] = err.fields
        return jsonify(body), 400

    @app.errorhandler(NotFoundError)
    def handle_not_found(err):
        return jsonify(erro=err.message), 404

    @app.errorhandler(ConflictError)
    def handle_conflict(err):
        return jsonify(erro=err.message), 409

    @app.errorhandler(DomainError)
    def handle_domain(err):
        return jsonify(erro=err.message), 400
