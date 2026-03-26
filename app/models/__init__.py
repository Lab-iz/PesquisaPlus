from app.extensions import db, login_manager

from .domain import AdvisorComment
from .domain import AuditLog
from .domain import BibliographicSearch
from .domain import Deadline
from .domain import LessonProgress
from .domain import MethodologyModule
from .domain import ModuleLesson
from .domain import ProgressRecord
from .domain import ProjectSection
from .domain import ReferenceItem
from .domain import ReportSnapshot
from .domain import ResearchProject
from .domain import ResearchStage
from .domain import RiskAlert
from .domain import Role
from .domain import SearchEntry
from .domain import SectionFeedback
from .domain import SectionRevision
from .domain import StageChecklistItem
from .domain import StudentProfile
from .domain import Tag
from .domain import TeacherProfile
from .domain import User


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))
