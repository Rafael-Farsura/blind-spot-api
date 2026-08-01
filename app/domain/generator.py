from app.domain import enums
from app.domain.errors import ValidationError


# catálogo fixo — demo estável (seed + execução)
_CATALOGO = (
    {
        "tipo": enums.TIPO_DIVERGENCIA_VALOR,
        "severidade": enums.SEVERIDADE_ALTA,
        "titulo": "Valor do documento difere do livro",
        "descricao": (
            "O valor total do documento fiscal não confere com o "
            "lançamento correspondente no livro auxiliar."
        ),
        "referencia": "DOC-2026-001",
    },
    {
        "tipo": enums.TIPO_CNPJ_INVALIDO,
        "severidade": enums.SEVERIDADE_MEDIA,
        "titulo": "CNPJ com tamanho insuficiente",
        "descricao": (
            "Identificador do participante possui menos de 14 caracteres "
            "após normalização."
        ),
        "referencia": "PART-88421",
    },
    {
        "tipo": enums.TIPO_CAMPO_OBRIGATORIO,
        "severidade": enums.SEVERIDADE_BAIXA,
        "titulo": "Município de prestação ausente",
        "descricao": (
            "Campo de município de prestação está vazio em registro "
            "que exige o preenchimento."
        ),
        "referencia": "REG-SERV-77",
    },
)


class VarreduraGenerator:
    """Gera inconsistências fictícias a partir de um job (sem ler arquivo real)."""

    def gerar(self, job, quantidade=None):
        n = enums.DEFAULT_QUANTIDADE_VARREDURA if quantidade is None else int(quantidade)
        if n < 1:
            raise ValidationError("Quantidade deve ser pelo menos 1.", {"quantidade": n})
        if n > enums.MAX_INCONSISTENCIAS_POR_EXECUCAO:
            raise ValidationError(
                f"Quantidade máxima é {enums.MAX_INCONSISTENCIAS_POR_EXECUCAO}.",
                {"quantidade": n},
            )

        itens = []
        for i in range(n):
            base = _CATALOGO[i % len(_CATALOGO)]
            itens.append(
                {
                    "job_id": job.id,
                    "origem": enums.ORIGEM_JOB,
                    "tipo": base["tipo"],
                    "severidade": base["severidade"],
                    "status": enums.INCONSISTENCIA_ABERTA,
                    "titulo": base["titulo"],
                    "descricao": base["descricao"],
                    "referencia": f"{base['referencia']}-{job.id}-{i + 1}",
                }
            )
        return itens
