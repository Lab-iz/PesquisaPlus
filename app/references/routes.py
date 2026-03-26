from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import or_

from app.extensions import db
from app.models import ReferenceItem, ResearchProject
from app.services.reference_service import create_reference, toggle_favorite
from app.utils.decorators import role_required, user_can_access_project


references_bp = Blueprint("references", __name__, url_prefix="/references")


def _project_or_404(project_id):
    project = db.session.get(ResearchProject, project_id)
    if project is None:
        abort(404)
    if not user_can_access_project(current_user, project):
        abort(403)
    return project


@references_bp.route("/project/<int:project_id>", methods=["GET", "POST"])
@login_required
def project_references(project_id):
    project = _project_or_404(project_id)
    query = ReferenceItem.query.filter_by(project_id=project.id)
    search = request.args.get("q", "").strip()
    status = request.args.get("status", "").strip()
    favorite = request.args.get("favorite", "").strip()

    if search:
        query = query.filter(or_(ReferenceItem.title.ilike(f"%{search}%"), ReferenceItem.authors.ilike(f"%{search}%")))
    if status:
        query = query.filter_by(reading_status=status)
    if favorite:
        query = query.filter_by(is_favorite=True)

    if request.method == "POST":
        if current_user.role_slug not in {"student", "admin"}:
            abort(403)
        payload = request.form.to_dict()
        payload["section_ids"] = request.form.getlist("section_ids")
        create_reference(project, payload, current_user)
        flash("Referencia adicionada ao projeto.", "success")
        return redirect(url_for("references.project_references", project_id=project.id))

    references = query.order_by(ReferenceItem.updated_at.desc()).all()
    return render_template("references/index.html", project=project, references=references)


@references_bp.route("/<int:reference_id>/favorite", methods=["POST"])
@login_required
@role_required("student", "admin")
def favorite(reference_id):
    reference = db.session.get(ReferenceItem, reference_id)
    if reference is None:
        abort(404)
    if current_user.role_slug == "student" and reference.project.student_id != current_user.id:
        abort(403)
    toggle_favorite(reference, current_user)
    flash("Preferencia atualizada.", "success")
    return redirect(url_for("references.project_references", project_id=reference.project_id))


@references_bp.route("/<int:reference_id>/link", methods=["POST"])
@login_required
@role_required("student", "admin")
def link_section(reference_id):
    reference = db.session.get(ReferenceItem, reference_id)
    if reference is None:
        abort(404)
    if current_user.role_slug == "student" and reference.project.student_id != current_user.id:
        abort(403)

    section_id = int(request.form.get("section_id"))
    section = next((item for item in reference.project.sections if item.id == section_id), None)
    if section is None:
        abort(404)

    if section in reference.sections:
        reference.sections.remove(section)
    else:
        reference.sections.append(section)
    db.session.commit()
    flash("Associacao de referencia atualizada.", "success")
    return redirect(url_for("references.project_references", project_id=reference.project_id))
