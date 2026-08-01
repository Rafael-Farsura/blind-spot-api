from app.domain import enums


def test_criar_job_e_listar(client):
    response = client.post(
        "/api/jobs",
        json={"competencia": "2026-07", "observacao": "teste"},
    )
    assert response.status_code == 201
    job = response.get_json()
    assert job["status"] == enums.JOB_STATUS_PENDENTE

    lista = client.get("/api/jobs").get_json()
    assert len(lista) == 1


def test_criar_job_sem_competencia(client):
    response = client.post("/api/jobs", json={})
    assert response.status_code == 400
    assert "erro" in response.get_json()


def test_executar_job(client):
    criado = client.post("/api/jobs", json={"competencia": "2026-07"}).get_json()
    response = client.post(f"/api/jobs/{criado['id']}/executar", json={"quantidade": 3})
    assert response.status_code == 200
    job = response.get_json()
    assert job["status"] == enums.JOB_STATUS_CONCLUIDO
    assert job["linhas_processadas"] == 3
    assert len(job["eventos"]) >= 2

    achados = client.get(f"/api/inconsistencias?job_id={criado['id']}").get_json()
    assert len(achados) == 3


def test_job_inexistente(client):
    response = client.get("/api/jobs/9999")
    assert response.status_code == 404


def test_patch_resolver_com_parecer(client):
    job = client.post("/api/jobs", json={"competencia": "2026-07"}).get_json()
    client.post(f"/api/jobs/{job['id']}/executar", json={"quantidade": 1})
    item = client.get(f"/api/inconsistencias?job_id={job['id']}").get_json()[0]

    response = client.patch(
        f"/api/inconsistencias/{item['id']}",
        json={
            "status": enums.INCONSISTENCIA_RESOLVIDA,
            "parecer": "Divergência ajustada após conferência.",
        },
    )
    assert response.status_code == 200
    assert response.get_json()["status"] == enums.INCONSISTENCIA_RESOLVIDA


def test_comentar_e_deletar_inconsistencia(client):
    job = client.post("/api/jobs", json={"competencia": "2026-07"}).get_json()
    client.post(f"/api/jobs/{job['id']}/executar", json={"quantidade": 1})
    item = client.get(f"/api/inconsistencias?job_id={job['id']}").get_json()[0]

    comentario = client.post(
        f"/api/inconsistencias/{item['id']}/comentarios",
        json={"autor": "Ana", "texto": "Checando no livro."},
    )
    assert comentario.status_code == 201

    detalhe = client.get(f"/api/inconsistencias/{item['id']}").get_json()
    assert len(detalhe["comentarios"]) == 1

    deleted = client.delete(f"/api/inconsistencias/{item['id']}")
    assert deleted.status_code == 204


def test_seed(client):
    response = client.post("/api/dev/seed")
    assert response.status_code == 200
    body = response.get_json()
    assert body["ok"] is True
    assert body["inconsistencias"] == 3


def test_criar_inconsistencia_manual(client):
    response = client.post(
        "/api/inconsistencias",
        json={
            "tipo": "campo_obrigatorio",
            "severidade": "baixa",
            "titulo": "Campo X vazio",
            "descricao": "Registro sem município de prestação.",
            "referencia": "M-99",
        },
    )
    assert response.status_code == 201
    assert response.get_json()["origem"] == "manual"


def test_excluir_job_pendente(client):
    job = client.post("/api/jobs", json={"competencia": "2026-08"}).get_json()
    response = client.delete(f"/api/jobs/{job['id']}")
    assert response.status_code == 204


def test_detalhar_job(client):
    job = client.post("/api/jobs", json={"competencia": "2026-08"}).get_json()
    response = client.get(f"/api/jobs/{job['id']}")
    assert response.status_code == 200
    assert response.get_json()["id"] == job["id"]
