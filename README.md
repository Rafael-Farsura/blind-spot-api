# Blind Spot API

API do **Blind Spot** — painel que mostra o ponto cego da rotina fiscal: checagens (jobs), inconsistências e pareceres.

Documentação de produto: https://github.com/Rafael-Farsura/blind-spot

Front (repo separado): https://github.com/Rafael-Farsura/blind-spot-web

## Requisitos

- Python 3.10+ (testado com 3.x)
- pip / venv

## Setup

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/macOS
# source .venv/bin/activate

pip install -r requirements.txt
python run.py
```

API: http://127.0.0.1:5000  
Health: http://127.0.0.1:5000/api/health  
Swagger: http://127.0.0.1:5000/api/docs/

## Seed de demonstração

```bash
curl -X POST http://127.0.0.1:5000/api/dev/seed
```

Recria a base local com 1 job concluído, 3 inconsistências e um comentário.

## Principais rotas

| Método | Path |
|--------|------|
| POST/GET | `/api/jobs` |
| GET/DELETE | `/api/jobs/{id}` |
| POST | `/api/jobs/{id}/executar` |
| GET/POST | `/api/inconsistencias` |
| GET/PATCH/DELETE | `/api/inconsistencias/{id}` |
| POST | `/api/inconsistencias/{id}/comentarios` |

## Testes

```bash
pytest --cov=app --cov-report=term-missing
```

Alvo: domínio/services ≥ 80%, rotas ≥ 70%.

## Notas

- Banco local SQLite: `blindspot.db` (criado na primeira subida).
- CORS liberado para o SPA aberto via `file://` (`index.html` no browser).
