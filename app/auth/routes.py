from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.extensions import db
from app.models import Role, StudentProfile, TeacherProfile, User
from app.utils.helpers import utcnow


auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            user.last_login_at = utcnow()
            db.session.commit()
            login_user(user)
            flash("Acesso realizado com sucesso.", "success")
            return redirect(url_for("main.dashboard"))
        flash("Credenciais invalidas.", "error")

    return render_template("auth/login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    roles = Role.query.filter(Role.slug.in_(["student", "advisor"])).order_by(Role.name).all()
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        role_slug = request.form.get("role")

        if not full_name or not email or not password:
            flash("Preencha nome, e-mail e senha.", "warning")
        elif User.query.filter_by(email=email).first():
            flash("Ja existe uma conta com este e-mail.", "error")
        else:
            role = Role.query.filter_by(slug=role_slug).first() or Role.query.filter_by(slug="student").first()
            user = User(
                full_name=full_name,
                email=email,
                role_id=role.id,
                course_name=request.form.get("course_name"),
                institution="Instituicao Academica",
            )
            user.set_password(password)
            db.session.add(user)
            db.session.flush()
            if role.slug == "student":
                db.session.add(
                    StudentProfile(
                        user_id=user.id,
                        registration_number=request.form.get("registration_number"),
                        research_line=request.form.get("research_line"),
                        semester=request.form.get("semester"),
                    )
                )
            if role.slug == "advisor":
                db.session.add(
                    TeacherProfile(
                        user_id=user.id,
                        department=request.form.get("department"),
                        title=request.form.get("teacher_title"),
                    )
                )
            db.session.commit()
            login_user(user)
            flash("Conta criada com sucesso.", "success")
            return redirect(url_for("main.dashboard"))

    return render_template("auth/register.html", roles=roles)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Sessao encerrada.", "success")
    return redirect(url_for("auth.login"))
