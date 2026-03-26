import pytest

from app import create_app
from app.extensions import db
from app.models import Role, User
from app.services.project_service import create_project

from config import TestingConfig


@pytest.fixture
def app():
    app = create_app(TestingConfig)
    with app.app_context():
        db.create_all()
        for slug, name in [("student", "Estudante"), ("advisor", "Orientador"), ("admin", "Coordenador")]:
            db.session.add(Role(slug=slug, name=name, description=name))
        db.session.commit()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def users(app):
    with app.app_context():
        roles = {role.slug: role for role in Role.query.all()}

        student = User(full_name="Teste Estudante", email="student@test.local", role_id=roles["student"].id, course_name="Pedagogia")
        student.set_password("student123")
        advisor = User(full_name="Teste Orientador", email="advisor@test.local", role_id=roles["advisor"].id, course_name="Metodologia")
        advisor.set_password("advisor123")
        admin = User(full_name="Teste Admin", email="admin@test.local", role_id=roles["admin"].id, course_name="Coordenacao")
        admin.set_password("admin123")
        db.session.add_all([student, advisor, admin])
        db.session.commit()
        return {
            "student": {"id": student.id, "email": student.email, "password": "student123"},
            "advisor": {"id": advisor.id, "email": advisor.email, "password": "advisor123"},
            "admin": {"id": admin.id, "email": admin.email, "password": "admin123"},
        }


@pytest.fixture
def project(app, users):
    with app.app_context():
        student = db.session.get(User, users["student"]["id"])
        project = create_project(
            student,
            {
                "advisor_id": users["advisor"]["id"],
                "project_type": "TCC",
                "title": "Projeto de teste",
                "thematic_area": "Educacao",
                "theme": "Tema de teste",
                "research_problem": "Como testar fluxos do sistema?",
                "general_objective": "Validar o MVP.",
                "specific_objectives": "Criar projeto\nSalvar secao",
                "justification": "Cobertura do fluxo principal.",
                "methodology_summary": "Estudo aplicado.",
                "keywords": "teste, fluxo",
            },
        )
        return project.id
