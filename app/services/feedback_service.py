from app.extensions import db
from app.models import AdvisorComment, SectionFeedback
from app.services.audit_service import log_action
from app.services.project_service import refresh_project_progress


def add_section_feedback(section, advisor, message, status_tag="guidance"):
    feedback = SectionFeedback(
        project_id=section.project_id,
        section_id=section.id,
        advisor_id=advisor.id,
        message=message.strip(),
        status_tag=status_tag,
    )
    db.session.add(feedback)

    if status_tag == "approved":
        section.status = "approved"
    elif status_tag in {"review", "needs_revision"}:
        section.status = "reviewed"

    log_action(advisor.id, "SectionFeedback", section.id, "create", f"Feedback {status_tag}")
    db.session.commit()
    refresh_project_progress(section.project, commit=True)
    return feedback


def add_project_comment(project, advisor, message):
    comment = AdvisorComment(project_id=project.id, advisor_id=advisor.id, message=message.strip())
    db.session.add(comment)
    log_action(advisor.id, "AdvisorComment", project.id, "create", "Observacao geral")
    db.session.commit()
    return comment
