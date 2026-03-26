from datetime import date

from app.extensions import db
from app.models import RiskAlert


def refresh_project_alerts(project, commit=True):
    for alert in project.alerts:
        alert.is_active = False

    today = date.today()
    overdue_stages = [stage for stage in project.stages if stage.due_date and stage.due_date < today and stage.status != "completed"]
    for stage in overdue_stages:
        db.session.add(
            RiskAlert(
                project=project,
                alert_type="delay",
                message=f"Etapa em atraso: {stage.title}.",
                severity="warning",
            )
        )

    missing_core = [
        label
        for label, value in {
            "problema": project.research_problem,
            "objetivo geral": project.general_objective,
            "justificativa": project.justification,
            "metodologia": project.methodology_summary,
        }.items()
        if not (value or "").strip()
    ]
    if missing_core:
        db.session.add(
            RiskAlert(
                project=project,
                alert_type="incomplete",
                message=f"Campos essenciais pendentes: {', '.join(missing_core[:3])}.",
                severity="info",
            )
        )

    if commit:
        db.session.commit()
