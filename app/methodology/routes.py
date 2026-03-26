from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.models import MethodologyModule, ModuleLesson
from app.services.methodology_service import complete_lesson, get_catalog_for_student
from app.utils.decorators import role_required


methodology_bp = Blueprint("methodology", __name__, url_prefix="/methodology")


@methodology_bp.route("/")
@login_required
def index():
    catalog = get_catalog_for_student(current_user.id) if current_user.role_slug == "student" else None
    modules = MethodologyModule.query.order_by(MethodologyModule.order_index).all()
    return render_template("methodology/index.html", modules=modules, catalog=catalog)


@methodology_bp.route("/<string:slug>")
@login_required
def module_detail(slug):
    module = MethodologyModule.query.filter_by(slug=slug).first_or_404()
    catalog = get_catalog_for_student(current_user.id) if current_user.role_slug == "student" else None
    module_progress = None
    if catalog:
        module_progress = next((item for item in catalog if item["module"].id == module.id), None)
    return render_template("methodology/module_detail.html", module=module, module_progress=module_progress)


@methodology_bp.route("/lesson/<int:lesson_id>", methods=["GET", "POST"])
@login_required
def lesson_detail(lesson_id):
    lesson = ModuleLesson.query.get_or_404(lesson_id)
    if request.method == "POST":
        if current_user.role_slug != "student":
            abort(403)
        complete_lesson(lesson, current_user, request.form.get("reflection", ""), checklist_done=bool(request.form.get("checklist_done")))
        flash("Licao concluida e registrada no seu progresso.", "success")
        return redirect(url_for("methodology.module_detail", slug=lesson.module.slug))
    return render_template("methodology/lesson_detail.html", lesson=lesson)
