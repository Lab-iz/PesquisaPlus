from flask import Blueprint, Response, render_template
from flask_login import current_user, login_required

from app.services.reporting_service import build_project_rows, build_summary, create_snapshot, export_feedback_csv, export_projects_csv, export_references_csv


reports_bp = Blueprint("reports", __name__, url_prefix="/reports")


def _scope_for_user():
    if current_user.role_slug == "admin":
        return "all"
    if current_user.role_slug == "advisor":
        return "advisor"
    return "student"


@reports_bp.route("/")
@login_required
def index():
    scope = _scope_for_user()
    create_snapshot(scope, current_user)
    return render_template(
        "reports/index.html",
        summary=build_summary(scope=scope, user=current_user),
        rows=build_project_rows(scope=scope, user=current_user),
    )


@reports_bp.route("/export/<string:kind>")
@login_required
def export(kind):
    scope = _scope_for_user()
    if kind == "projects":
        csv_content = export_projects_csv(scope=scope, user=current_user)
        filename = "projetos.csv"
    elif kind == "feedback":
        csv_content = export_feedback_csv(scope=scope, user=current_user)
        filename = "feedback.csv"
    else:
        csv_content = export_references_csv(scope=scope, user=current_user)
        filename = "referencias.csv"

    return Response(
        csv_content,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
