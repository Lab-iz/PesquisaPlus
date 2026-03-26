from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.models import ProjectSection, ResearchProject
from app.services.dashboard_service import advisor_dashboard_data
from app.services.feedback_service import add_project_comment, add_section_feedback
from app.utils.decorators import role_required


advisor_bp = Blueprint("advisor", __name__, url_prefix="/advisor")


def _ensure_advisor_project(project):
    if current_user.role_slug == "admin":
        return
    if project.advisor_id != current_user.id:
        abort(403)


@advisor_bp.route("/dashboard")
@login_required
@role_required("advisor", "admin")
def dashboard():
    data = advisor_dashboard_data(current_user) if current_user.role_slug == "advisor" else advisor_dashboard_data(current_user)
    return render_template("advisor/dashboard.html", data=data)


@advisor_bp.route("/sections/<int:section_id>/feedback", methods=["POST"])
@login_required
@role_required("advisor", "admin")
def add_feedback(section_id):
    section = db.session.get(ProjectSection, section_id)
    if section is None:
        abort(404)
    _ensure_advisor_project(section.project)
    add_section_feedback(section, current_user, request.form.get("message", ""), request.form.get("status_tag", "guidance"))
    flash("Feedback registrado na secao.", "success")
    return redirect(url_for("projects.section_editor", project_id=section.project_id, section_key=section.key))


@advisor_bp.route("/projects/<int:project_id>/comment", methods=["POST"])
@login_required
@role_required("advisor", "admin")
def add_comment(project_id):
    project = db.session.get(ResearchProject, project_id)
    if project is None:
        abort(404)
    _ensure_advisor_project(project)
    add_project_comment(project, current_user, request.form.get("message", ""))
    flash("Observacao geral registrada.", "success")
    return redirect(url_for("projects.detail", project_id=project.id))
