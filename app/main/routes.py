from flask import Blueprint, redirect, render_template, url_for
from flask_login import current_user, login_required

from app.services.dashboard_service import admin_dashboard_data, advisor_dashboard_data, student_dashboard_data


main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    return render_template("main/home.html")


@main_bp.route("/dashboard")
@login_required
def dashboard():
    if current_user.role_slug == "student":
        return render_template("main/student_dashboard.html", data=student_dashboard_data(current_user))
    if current_user.role_slug == "advisor":
        return redirect(url_for("advisor.dashboard"))
    return redirect(url_for("admin.dashboard"))


@main_bp.app_errorhandler(403)
def forbidden(_error):
    return render_template("main/error.html", title="Acesso negado", message="Voce nao tem permissao para acessar este conteudo."), 403


@main_bp.app_errorhandler(404)
def not_found(_error):
    return render_template("main/error.html", title="Pagina nao encontrada", message="O caminho solicitado nao foi localizado na plataforma."), 404
