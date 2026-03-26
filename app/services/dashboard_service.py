from collections import Counter

from app.models import MethodologyModule, ProgressRecord, ResearchProject, RiskAlert, Role, SectionFeedback, User
from app.services.methodology_service import get_catalog_for_student, get_global_progress
from app.services.project_service import calculate_project_completion


def student_dashboard_data(student):
    project = student.active_project
    if project is None:
        return {
            "project": None,
            "methodology_progress": get_global_progress(student.id),
            "catalog": get_catalog_for_student(student.id),
            "recent_feedback": [],
            "pending_sections": [],
            "next_stages": [],
            "active_alerts": [],
            "project_progress": 0,
            "recent_progress": [],
        }

    return {
        "project": project,
        "project_progress": calculate_project_completion(project),
        "methodology_progress": get_global_progress(student.id),
        "catalog": get_catalog_for_student(student.id),
        "recent_feedback": project.section_feedbacks[:4],
        "pending_sections": [section for section in project.sections if section.status != "approved"][:5],
        "next_stages": [stage for stage in project.stages if stage.status != "completed"][:4],
        "active_alerts": [alert for alert in project.alerts if alert.is_active][:4],
        "recent_progress": project.progress_records[:6],
    }


def advisor_dashboard_data(advisor):
    projects = ResearchProject.query.filter_by(advisor_id=advisor.id).order_by(ResearchProject.updated_at.desc()).all()
    delayed = [project for project in projects if any(alert.is_active and alert.alert_type == "delay" for alert in project.alerts)]
    pending_reviews = sum(
        1
        for project in projects
        for section in project.sections
        if section.status in {"submitted", "reviewed"}
    )
    theme_counter = Counter(project.thematic_area or "Nao informado" for project in projects)
    return {
        "projects": projects,
        "project_count": len(projects),
        "delayed_count": len(delayed),
        "pending_reviews": pending_reviews,
        "recent_feedback": SectionFeedback.query.filter_by(advisor_id=advisor.id).order_by(SectionFeedback.created_at.desc()).limit(5).all(),
        "top_themes": theme_counter.most_common(4),
    }


def admin_dashboard_data():
    projects = ResearchProject.query.order_by(ResearchProject.updated_at.desc()).all()
    students = User.query.join(User.role).filter(Role.slug == "student").count()
    advisors = User.query.join(User.role).filter(Role.slug == "advisor").count()
    average_progress = round(
        sum(calculate_project_completion(project) for project in projects) / len(projects)
    ) if projects else 0
    difficult_sections = Counter(
        feedback.section.title
        for feedback in SectionFeedback.query.all()
        if feedback.status_tag in {"review", "needs_revision", "guidance"}
    ).most_common(5)
    return {
        "projects": projects[:8],
        "project_count": len(projects),
        "students": students,
        "advisors": advisors,
        "average_progress": average_progress,
        "delayed_count": RiskAlert.query.filter_by(alert_type="delay", is_active=True).count(),
        "module_count": MethodologyModule.query.count(),
        "difficult_sections": difficult_sections,
        "recent_progress": ProgressRecord.query.order_by(ProgressRecord.recorded_at.desc()).limit(8).all(),
    }
