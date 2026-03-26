import csv
import io
import json

from app.extensions import db
from app.models import ReferenceItem, ReportSnapshot, ResearchProject, SectionFeedback, User
from app.services.project_service import calculate_project_completion


def build_project_rows(scope="all", user=None):
    query = ResearchProject.query
    if scope == "advisor" and user is not None:
        query = query.filter_by(advisor_id=user.id)
    elif scope == "student" and user is not None:
        query = query.filter_by(student_id=user.id)

    rows = []
    for project in query.order_by(ResearchProject.updated_at.desc()).all():
        rows.append(
            {
                "project_id": project.id,
                "student": project.student.full_name,
                "advisor": project.advisor.full_name if project.advisor else "-",
                "title": project.title,
                "area": project.thematic_area or "-",
                "status": project.status,
                "progress": calculate_project_completion(project),
                "references": len(project.references),
                "feedbacks": len(project.section_feedbacks),
            }
        )
    return rows


def build_summary(scope="all", user=None):
    rows = build_project_rows(scope=scope, user=user)
    return {
        "total_projects": len(rows),
        "average_progress": round(sum(row["progress"] for row in rows) / len(rows)) if rows else 0,
        "total_feedbacks": sum(row["feedbacks"] for row in rows),
        "total_references": sum(row["references"] for row in rows),
    }


def create_snapshot(scope, actor):
    snapshot = ReportSnapshot(
        scope=scope,
        generated_by_id=actor.id,
        summary_json=json.dumps(build_summary(scope=scope, user=actor)),
    )
    db.session.add(snapshot)
    db.session.commit()
    return snapshot


def export_projects_csv(scope="all", user=None):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Projeto", "Estudante", "Orientador", "Area", "Status", "Progresso", "Referencias", "Feedbacks"])
    for row in build_project_rows(scope=scope, user=user):
        writer.writerow(
            [
                row["title"],
                row["student"],
                row["advisor"],
                row["area"],
                row["status"],
                row["progress"],
                row["references"],
                row["feedbacks"],
            ]
        )
    return output.getvalue()


def export_feedback_csv(scope="all", user=None):
    query = SectionFeedback.query
    if scope == "advisor" and user is not None:
        query = query.filter_by(advisor_id=user.id)
    elif scope == "student" and user is not None:
        query = query.join(ResearchProject, SectionFeedback.project_id == ResearchProject.id).filter(ResearchProject.student_id == user.id)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Projeto", "Secao", "Orientador", "Status", "Data", "Mensagem"])
    for feedback in query.order_by(SectionFeedback.created_at.desc()).all():
        writer.writerow(
            [
                feedback.project.title,
                feedback.section.title,
                feedback.advisor.full_name,
                feedback.status_tag,
                feedback.created_at.strftime("%Y-%m-%d"),
                feedback.message,
            ]
        )
    return output.getvalue()


def export_references_csv(scope="all", user=None):
    query = ReferenceItem.query
    if scope == "advisor" and user is not None:
        query = query.join(ResearchProject, ReferenceItem.project_id == ResearchProject.id).filter(ResearchProject.advisor_id == user.id)
    elif scope == "student" and user is not None:
        query = query.join(ResearchProject, ReferenceItem.project_id == ResearchProject.id).filter(ResearchProject.student_id == user.id)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Projeto", "Titulo", "Autores", "Ano", "Tipo", "Status de leitura"])
    for reference in query.order_by(ReferenceItem.created_at.desc()).all():
        writer.writerow(
            [
                reference.project.title,
                reference.title,
                reference.authors,
                reference.year,
                reference.source_type,
                reference.reading_status,
            ]
        )
    return output.getvalue()


def build_admin_user_rows():
    return [
        {
            "name": user.full_name,
            "email": user.email,
            "role": user.role.name,
            "course": user.course_name or "-",
        }
        for user in User.query.order_by(User.full_name).all()
    ]
