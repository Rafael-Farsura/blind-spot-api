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

## Testes

```bash
pytest --cov=app --cov-report=term-missing
```

## Notas

- Banco local SQLite: `blindspot.db` (criado na primeira subida).
- CORS liberado para o SPA aberto via `file://` (`index.html` no browser).
