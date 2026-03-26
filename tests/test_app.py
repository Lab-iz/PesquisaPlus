from app.extensions import db
from app.models import ReferenceItem, ResearchProject, SectionFeedback


def login(client, email, password):
    return client.post(
        "/auth/login",
        data={"email": email, "password": password},
        follow_redirects=True,
    )


def test_login_success(client, users):
    response = login(client, users["student"]["email"], users["student"]["password"])
    assert response.status_code == 200
    assert b"Painel do estudante" in response.data


def test_role_protection_blocks_student_from_admin(client, users):
    login(client, users["student"]["email"], users["student"]["password"])
    response = client.get("/admin/dashboard")
    assert response.status_code == 403


def test_create_project(client, app, users):
    login(client, users["student"]["email"], users["student"]["password"])
    response = client.post(
        "/projects/create",
        data={
            "title": "Novo projeto testado",
            "advisor_id": users["advisor"]["id"],
            "project_type": "TCC",
            "thematic_area": "Saude",
            "research_problem": "Qual o efeito de um fluxo guiado?",
            "general_objective": "Medir apoio ao estudante.",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Novo projeto testado" in response.data
    with app.app_context():
        assert ResearchProject.query.filter_by(title="Novo projeto testado").count() == 1


def test_update_section(client, app, users, project):
    login(client, users["student"]["email"], users["student"]["password"])
    response = client.post(
        f"/projects/{project}/sections/introduction",
        data={"content": "Conteudo atualizado para a introducao.", "status": "submitted"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    with app.app_context():
        refreshed = db.session.get(ResearchProject, project)
        section = next(section for section in refreshed.sections if section.key == "introduction")
        assert section.content == "Conteudo atualizado para a introducao."
        assert section.status == "submitted"


def test_create_reference(client, app, users, project):
    login(client, users["student"]["email"], users["student"]["password"])
    with app.app_context():
        project_obj = db.session.get(ResearchProject, project)
        introduction = next(section for section in project_obj.sections if section.key == "introduction")
    response = client.post(
        f"/references/project/{project}",
        data={
            "source_type": "artigo",
            "authors": "Autor Teste",
            "title": "Referencia de teste",
            "year": "2024",
            "section_ids": [str(introduction.id)],
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    with app.app_context():
        assert ReferenceItem.query.filter_by(title="Referencia de teste").count() == 1


def test_register_feedback(client, app, users, project):
    login(client, users["advisor"]["email"], users["advisor"]["password"])
    with app.app_context():
        project_obj = db.session.get(ResearchProject, project)
        section = next(section for section in project_obj.sections if section.key == "introduction")
    response = client.post(
        f"/advisor/sections/{section.id}/feedback",
        data={"message": "Bom caminho, mas refine o recorte.", "status_tag": "review"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    with app.app_context():
        assert SectionFeedback.query.filter_by(section_id=section.id).count() == 1


def test_report_export(client, users, project):
    login(client, users["advisor"]["email"], users["advisor"]["password"])
    response = client.get("/reports/export/projects")
    assert response.status_code == 200
    assert response.mimetype == "text/csv"
    assert "Projeto de teste" in response.text
