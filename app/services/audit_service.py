from app.extensions import db
from app.models import AuditLog


def log_action(user_id, entity_type, entity_id, action, detail=None):
    db.session.add(
        AuditLog(
            user_id=user_id,
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            detail=detail,
        )
    )
