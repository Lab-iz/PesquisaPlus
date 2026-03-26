from app.extensions import db
from app.models import BibliographicSearch, SearchEntry
from app.services.audit_service import log_action
from app.utils.helpers import normalize_multiline


def create_search(project, data, actor):
    search = BibliographicSearch(
        project_id=project.id,
        title=data["title"].strip(),
        keywords=data.get("keywords"),
        databases_consulted=data.get("databases_consulted"),
        inclusion_criteria=normalize_multiline(data.get("inclusion_criteria")),
        exclusion_criteria=normalize_multiline(data.get("exclusion_criteria")),
        notes=normalize_multiline(data.get("notes")),
    )
    db.session.add(search)
    db.session.commit()
    log_action(actor.id, "BibliographicSearch", search.id, "create", "Busca bibliografica registrada")
    db.session.commit()
    return search


def add_search_entry(search, data, actor):
    entry = SearchEntry(
        search_id=search.id,
        title=data["title"].strip(),
        authors=data.get("authors"),
        year=data.get("year"),
        source=data.get("source"),
        was_selected=bool(data.get("was_selected")),
        reading_notes=normalize_multiline(data.get("reading_notes")),
    )
    db.session.add(entry)
    log_action(actor.id, "SearchEntry", search.id, "create", "Item adicionado a busca")
    db.session.commit()
    return entry
