from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.models import MethodologyModule, Role, StudentProfile, TeacherProfile, User
from app.services.dashboard_service import admin_dashboard_data
from app.services.reporting_service import build_admin_user_rows
from app.utils.decorators import role_required


admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/dashboard")
@login_required
@role_required("admin")
def dashboard():
    return render_template("admin/dashboard.html", data=admin_dashboard_data())


@admin_bp.route("/users", methods=["GET", "POST"])
@login_required
@role_required("admin")
def users():
    roles = Role.query.order_by(Role.name).all()
    if request.method == "POST":
        role = Role.query.get(int(request.form.get("role_id")))
        user = User(
            full_name=request.form.get("full_name"),
            email=request.form.get("email").strip().lower(),
            role_id=role.id,
            course_name=request.form.get("course_name"),
            institution="Instituicao Academica",
        )
        user.set_password(request.form.get("password"))
        db.session.add(user)
        db.session.flush()
        if role.slug == "student":
            db.session.add(StudentProfile(user_id=user.id, registration_number=request.form.get("registration_number")))
        if role.slug == "advisor":
            db.session.add(TeacherProfile(user_id=user.id, department=request.form.get("department"), title=request.form.get("teacher_title")))
        db.session.commit()
        flash("Usuario institucional cadastrado.", "success")
        return redirect(url_for("admin.users"))
    return render_template("admin/users.html", users=build_admin_user_rows(), roles=roles)


@admin_bp.route("/catalog")
@login_required
@role_required("admin")
def catalog():
    modules = MethodologyModule.query.order_by(MethodologyModule.order_index).all()
    return render_template("admin/catalog.html", modules=modules)
