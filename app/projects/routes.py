from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.models import ProjectSection, ResearchProject, ResearchStage, Role, StageChecklistItem, User
from app.services.project_service import calculate_project_completion, create_project, refresh_project_progress, sync_stage_status, update_project_core, update_section
from app.services.text_assist_service import analyze_abstract, section_guidance
from app.utils.decorators import role_required, user_can_access_project


projects_bp = Blueprint("projects", __name__, url_prefix="/projects")


def get_project_or_404(project_id):
    project = db.session.get(ResearchProject, project_id)
    if project is None:
        abort(404)
    if not user_can_access_project(current_user, project):
        abort(403)
    return project


@projects_bp.route("/")
@login_required
def index():
    if current_user.role_slug == "student":
        projects = ResearchProject.query.filter_by(student_id=current_user.id).order_by(ResearchProject.updated_at.desc()).all()
    elif current_user.role_slug == "advisor":
        projects = ResearchProject.query.filter_by(advisor_id=current_user.id).order_by(ResearchProject.updated_at.desc()).all()
    else:
        projects = ResearchProject.query.order_by(ResearchProject.updated_at.desc()).all()
    return render_template("projects/index.html", projects=projects, calculate_project_completion=calculate_project_completion)


@projects_bp.route("/create", methods=["GET", "POST"])
@login_required
@role_required("student")
def create():
    advisors = User.query.join(User.role).filter(Role.slug == "advisor").order_by(User.full_name).all()
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        if not title:
            flash("Informe um titulo provisorio para iniciar o projeto.", "warning")
        else:
            project = create_project(current_user, request.form)
            flash("Projeto criado com sucesso.", "success")
            return redirect(url_for("projects.detail", project_id=project.id))
    return render_template("projects/create.html", advisors=advisors)


@projects_bp.route("/<int:project_id>")
@login_required
def detail(project_id):
    project = get_project_or_404(project_id)
    abstract_section = next((section for section in project.sections if section.key == "abstract"), None)
    abstract_analysis = analyze_abstract(abstract_section.content if abstract_section else "")
    return render_template(
        "projects/detail.html",
        project=project,
        project_progress=calculate_project_completion(project),
        abstract_analysis=abstract_analysis,
    )


@projects_bp.route("/<int:project_id>/edit", methods=["GET", "POST"])
@login_required
@role_required("student", "admin")
def edit_core(project_id):
    project = get_project_or_404(project_id)
    if current_user.role_slug == "student" and project.student_id != current_user.id:
        abort(403)

    advisors = User.query.join(User.role).filter(Role.slug == "advisor").order_by(User.full_name).all()
    if request.method == "POST":
        update_project_core(project, request.form, current_user)
        if current_user.role_slug == "admin" and request.form.get("advisor_id"):
            project.advisor_id = int(request.form.get("advisor_id"))
            db.session.commit()
        flash("Estrutura guiada atualizada.", "success")
        return redirect(url_for("projects.detail", project_id=project.id))
    return render_template("projects/edit.html", project=project, advisors=advisors)


@projects_bp.route("/<int:project_id>/sections/<string:section_key>", methods=["GET", "POST"])
@login_required
def section_editor(project_id, section_key):
    project = get_project_or_404(project_id)
    section = ProjectSection.query.filter_by(project_id=project.id, key=section_key).first_or_404()
    can_edit = current_user.role_slug == "admin" or (current_user.role_slug == "student" and project.student_id == current_user.id)

    if request.method == "POST":
        if not can_edit:
            abort(403)
        status = request.form.get("status") or "draft"
        update_section(section, request.form.get("content", ""), status, current_user)
        flash("Secao salva com sucesso.", "success")
        return redirect(url_for("projects.section_editor", project_id=project.id, section_key=section.key))

    return render_template(
        "projects/section_editor.html",
        project=project,
        section=section,
        can_edit=can_edit,
        guidance=section_guidance(section.key),
        abstract_analysis=analyze_abstract(section.content) if section.key == "abstract" else None,
    )


@projects_bp.route("/<int:project_id>/stages/<int:stage_id>/items/<int:item_id>", methods=["POST"])
@login_required
@role_required("student", "admin")
def toggle_stage_item(project_id, stage_id, item_id):
    project = get_project_or_404(project_id)
    if current_user.role_slug == "student" and project.student_id != current_user.id:
        abort(403)

    stage = ResearchStage.query.filter_by(project_id=project.id, id=stage_id).first_or_404()
    item = StageChecklistItem.query.filter_by(stage_id=stage.id, id=item_id).first_or_404()
    item.is_done = not item.is_done
    sync_stage_status(stage)

    linked_deadline = next((deadline for deadline in project.deadlines if deadline.title == stage.title), None)
    if linked_deadline:
        linked_deadline.status = "done" if stage.status == "completed" else "planned"

    db.session.commit()
    refresh_project_progress(project, commit=True)
    flash("Checklist de etapa atualizado.", "success")
    return redirect(url_for("projects.detail", project_id=project.id))
