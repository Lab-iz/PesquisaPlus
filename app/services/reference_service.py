from app.extensions import db
from app.models import ReferenceItem, Tag
from app.services.audit_service import log_action
from app.services.project_service import refresh_project_progress
from app.utils.helpers import normalize_multiline, parse_tags


def create_reference(project, data, actor):
    reference = ReferenceItem(
        project_id=project.id,
        source_type=data["source_type"],
        authors=data["authors"].strip(),
        title=data["title"].strip(),
        year=data.get("year"),
        venue=data.get("venue"),
        url=data.get("url"),
        doi=data.get("doi"),
        notes=normalize_multiline(data.get("notes")),
        keywords=data.get("keywords"),
        reading_status=data.get("reading_status") or "to_read",
        is_favorite=bool(data.get("is_favorite")),
    )
    db.session.add(reference)
    db.session.flush()

    for tag_name in parse_tags(data.get("tags")):
        tag = Tag.query.filter_by(name=tag_name).first()
        if tag is None:
            tag = Tag(name=tag_name)
            db.session.add(tag)
        reference.tags.append(tag)

    section_ids = data.get("section_ids") or []
    for section_id in section_ids:
        section = next((item for item in project.sections if item.id == int(section_id)), None)
        if section:
            reference.sections.append(section)

    log_action(actor.id, "ReferenceItem", reference.id, "create", "Referencia cadastrada")
    db.session.commit()
    refresh_project_progress(project, commit=True)
    return reference


def toggle_favorite(reference, actor):
    reference.is_favorite = not reference.is_favorite
    log_action(actor.id, "ReferenceItem", reference.id, "favorite", "Favorito alternado")
    db.session.commit()
