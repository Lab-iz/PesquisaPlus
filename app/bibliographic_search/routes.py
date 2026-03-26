from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.models import BibliographicSearch, ResearchProject
from app.services.bibliographic_search_service import add_search_entry, create_search
from app.utils.decorators import role_required, user_can_access_project


bibliographic_search_bp = Blueprint("bibliographic_search", __name__, url_prefix="/searches")


def _project_or_404(project_id):
    project = db.session.get(ResearchProject, project_id)
    if project is None:
        abort(404)
    if not user_can_access_project(current_user, project):
        abort(403)
    return project


def _search_or_404(search_id):
    search = db.session.get(BibliographicSearch, search_id)
    if search is None:
        abort(404)
    if not user_can_access_project(current_user, search.project):
        abort(403)
    return search


@bibliographic_search_bp.route("/project/<int:project_id>", methods=["GET", "POST"])
@login_required
def index(project_id):
    project = _project_or_404(project_id)
    if request.method == "POST":
        if current_user.role_slug not in {"student", "admin"}:
            abort(403)
        create_search(project, request.form, current_user)
        flash("Busca bibliografica registrada.", "success")
        return redirect(url_for("bibliographic_search.index", project_id=project.id))
    return render_template("bibliographic_search/index.html", project=project)


@bibliographic_search_bp.route("/<int:search_id>", methods=["GET", "POST"])
@login_required
def detail(search_id):
    search = _search_or_404(search_id)
    if request.method == "POST":
        if current_user.role_slug not in {"student", "admin"}:
            abort(403)
        add_search_entry(search, request.form, current_user)
        flash("Item adicionado a busca.", "success")
        return redirect(url_for("bibliographic_search.detail", search_id=search.id))
    return render_template("bibliographic_search/detail.html", search=search)
