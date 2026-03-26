from app.extensions import db
from app.models import LessonProgress, MethodologyModule
from app.services.audit_service import log_action
from app.utils.helpers import percentage


def get_catalog_for_student(student_id):
    modules = MethodologyModule.query.order_by(MethodologyModule.order_index).all()
    progress_map = {
        entry.lesson_id: entry
        for entry in LessonProgress.query.filter_by(student_id=student_id).all()
    }

    catalog = []
    for module in modules:
        completed = sum(
            1
            for lesson in module.lessons
            if progress_map.get(lesson.id) and progress_map[lesson.id].is_completed
        )
        total = len(module.lessons)
        catalog.append(
            {
                "module": module,
                "completed": completed,
                "total": total,
                "progress": percentage(completed, total),
            }
        )
    return catalog


def get_global_progress(student_id):
    catalog = get_catalog_for_student(student_id)
    total_lessons = sum(item["total"] for item in catalog)
    completed_lessons = sum(item["completed"] for item in catalog)
    return percentage(completed_lessons, total_lessons)


def complete_lesson(lesson, student, reflection, checklist_done=True):
    progress = LessonProgress.query.filter_by(lesson_id=lesson.id, student_id=student.id).first()
    if progress is None:
        progress = LessonProgress(lesson_id=lesson.id, student_id=student.id)
        db.session.add(progress)

    progress.is_completed = True
    progress.checklist_done = checklist_done
    progress.reflection = reflection
    log_action(student.id, "ModuleLesson", lesson.id, "complete", "Licao concluida")
    db.session.commit()
    return progress
