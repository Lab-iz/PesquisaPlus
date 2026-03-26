from datetime import date, datetime, timedelta

from app.extensions import db
from app.models import Deadline, ProgressRecord, ProjectSection, ResearchProject, ResearchStage, SectionRevision, StageChecklistItem
from app.services.audit_service import log_action
from app.utils.helpers import count_words, normalize_multiline, percentage, utcnow


SECTION_TEMPLATES = [
    ("introduction", "Introducao"),
    ("theoretical_framework", "Fundamentacao Teorica"),
    ("methodology", "Metodologia"),
    ("development_results", "Desenvolvimento e Resultados"),
    ("conclusion", "Conclusao"),
    ("abstract", "Resumo"),
    ("abstract_en", "Abstract"),
    ("references", "Referencias"),
]


STAGE_TEMPLATES = [
    (
        "Delimitacao do problema",
        "Definir recorte, problema e objetivos iniciais.",
        ["Delimitar tema", "Escrever problema", "Redigir objetivo geral"],
        7,
    ),
    (
        "Planejamento metodologico",
        "Consolidar abordagem, procedimentos e cronograma.",
        ["Escolher tipo de pesquisa", "Definir tecnicas", "Revisar viabilidade"],
        21,
    ),
    (
        "Revisao bibliografica",
        "Mapear literatura e registrar referencias centrais.",
        ["Registrar descritores", "Cadastrar referencias", "Selecionar estudos-chave"],
        35,
    ),
    (
        "Redacao orientada",
        "Produzir secoes principais do texto academico.",
        ["Escrever introducao", "Redigir fundamentacao", "Atualizar metodologia"],
        55,
    ),
    (
        "Fechamento e revisao",
        "Consolidar conclusoes, resumo e referencias.",
        ["Revisar resumo", "Fechar conclusao", "Revisar referencias"],
        75,
    ),
]


def create_project(student, data):
    advisor_id = int(data["advisor_id"]) if data.get("advisor_id") else None
    start_date = _parse_date(data.get("start_date")) or date.today()
    target_date = _parse_date(data.get("target_completion_date"))

    project = ResearchProject(
        student_id=student.id,
        advisor_id=advisor_id,
        project_type=data.get("project_type") or "TCC",
        title=data["title"].strip(),
        thematic_area=data.get("thematic_area"),
        theme=data.get("theme"),
        research_problem=data.get("research_problem"),
        hypothesis=data.get("hypothesis"),
        general_objective=data.get("general_objective"),
        specific_objectives=normalize_multiline(data.get("specific_objectives")),
        justification=data.get("justification"),
        methodology_summary=data.get("methodology_summary"),
        keywords=data.get("keywords"),
        course_name=data.get("course_name") or student.course_name,
        start_date=start_date,
        target_completion_date=target_date,
    )
    db.session.add(project)
    db.session.flush()

    for index, (key, title) in enumerate(SECTION_TEMPLATES, start=1):
        db.session.add(
            ProjectSection(
                project_id=project.id,
                key=key,
                title=title,
                display_order=index,
                content="",
            )
        )

    for index, (title, description, checklist, offset_days) in enumerate(STAGE_TEMPLATES, start=1):
        stage = ResearchStage(
            project_id=project.id,
            title=title,
            description=description,
            stage_order=index,
            due_date=start_date + timedelta(days=offset_days),
        )
        db.session.add(stage)
        db.session.flush()
        for label in checklist:
            db.session.add(StageChecklistItem(stage_id=stage.id, label=label))
        db.session.add(
            Deadline(
                project_id=project.id,
                title=title,
                due_date=start_date + timedelta(days=offset_days),
            )
        )

    log_action(student.id, "ResearchProject", project.id, "create", "Projeto iniciado")
    db.session.commit()
    refresh_project_progress(project, commit=True)
    return project


def update_project_core(project, data, actor):
    project.title = data.get("title", project.title).strip()
    project.project_type = data.get("project_type", project.project_type)
    project.thematic_area = data.get("thematic_area", project.thematic_area)
    project.theme = data.get("theme", project.theme)
    project.research_problem = data.get("research_problem", project.research_problem)
    project.hypothesis = data.get("hypothesis", project.hypothesis)
    project.general_objective = data.get("general_objective", project.general_objective)
    project.specific_objectives = normalize_multiline(data.get("specific_objectives", project.specific_objectives))
    project.justification = data.get("justification", project.justification)
    project.methodology_summary = data.get("methodology_summary", project.methodology_summary)
    project.keywords = data.get("keywords", project.keywords)
    project.course_name = data.get("course_name", project.course_name)
    project.target_completion_date = _parse_date(data.get("target_completion_date")) or project.target_completion_date
    log_action(actor.id, "ResearchProject", project.id, "update", "Atualizacao da estrutura guiada")
    db.session.commit()
    refresh_project_progress(project, commit=True)
    return project


def update_section(section, content, status, actor):
    previous_content = section.content or ""
    normalized = normalize_multiline(content)
    if previous_content != normalized and previous_content.strip():
        next_version = (section.revisions[0].version_number + 1) if section.revisions else 1
        db.session.add(
            SectionRevision(
                section_id=section.id,
                editor_id=actor.id,
                content_snapshot=previous_content,
                version_number=next_version,
            )
        )

    section.content = normalized
    section.word_count = count_words(normalized)
    section.status = status
    if status == "submitted":
        section.last_submitted_at = utcnow()

    log_action(actor.id, "ProjectSection", section.id, "update", f"Secao {section.key} atualizada")
    db.session.commit()
    refresh_project_progress(section.project, commit=True)
    return section


def calculate_project_completion(project):
    core_values = [
        project.title,
        project.thematic_area,
        project.theme,
        project.research_problem,
        project.general_objective,
        project.specific_objectives,
        project.justification,
        project.methodology_summary,
        project.keywords,
    ]
    core_completion = percentage(sum(bool((value or "").strip()) for value in core_values), len(core_values))

    section_weights = {
        "not_started": 0,
        "draft": 0.35,
        "submitted": 0.7,
        "reviewed": 0.85,
        "approved": 1,
    }
    if project.sections:
        section_ratio = sum(section_weights.get(section.status, 0.2) for section in project.sections) / len(project.sections)
    else:
        section_ratio = 0
    section_completion = round(section_ratio * 100)

    if project.stages:
        stage_completion = percentage(
            sum(1 for stage in project.stages if stage.status == "completed"),
            len(project.stages),
        )
    else:
        stage_completion = 0

    reference_completion = min(len(project.references) * 12, 100)
    overall = round((core_completion * 0.35) + (section_completion * 0.35) + (stage_completion * 0.2) + (reference_completion * 0.1))
    return overall


def refresh_project_progress(project, commit=True):
    progress = calculate_project_completion(project)
    latest = (
        ProgressRecord.query.filter_by(project_id=project.id, category="overall")
        .order_by(ProgressRecord.recorded_at.desc())
        .first()
    )
    if latest is None or latest.progress_value != progress:
        db.session.add(
            ProgressRecord(
                project_id=project.id,
                category="overall",
                progress_value=progress,
                note="Atualizacao automatica do progresso global",
            )
        )

    if progress >= 85:
        project.status = "advanced"
    elif progress >= 55:
        project.status = "developing"
    else:
        project.status = "planning"

    from app.services.alert_service import refresh_project_alerts

    refresh_project_alerts(project, commit=False)
    if commit:
        db.session.commit()
    return progress


def sync_stage_status(stage):
    all_done = all(item.is_done for item in stage.checklist_items) if stage.checklist_items else False
    if all_done:
        stage.status = "completed"
        stage.completed_at = stage.completed_at or utcnow()
    elif any(item.is_done for item in stage.checklist_items):
        stage.status = "in_progress"
        stage.completed_at = None
    else:
        stage.status = "pending"
        stage.completed_at = None


def _parse_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None
