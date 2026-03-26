from datetime import date

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db
from app.utils.helpers import utcnow


section_references = db.Table(
    "section_references",
    db.Column("section_id", db.Integer, db.ForeignKey("project_sections.id"), primary_key=True),
    db.Column("reference_id", db.Integer, db.ForeignKey("reference_items.id"), primary_key=True),
)


reference_tags = db.Table(
    "reference_tags_assoc",
    db.Column("reference_id", db.Integer, db.ForeignKey("reference_items.id"), primary_key=True),
    db.Column("tag_id", db.Integer, db.ForeignKey("tags.id"), primary_key=True),
)


class Role(db.Model):
    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.Text)

    users = db.relationship("User", back_populates="role")


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=False)
    course_name = db.Column(db.String(120))
    institution = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)
    last_login_at = db.Column(db.DateTime)
    is_active_user = db.Column(db.Boolean, default=True, nullable=False)

    role = db.relationship("Role", back_populates="users")
    student_profile = db.relationship("StudentProfile", back_populates="user", uselist=False)
    teacher_profile = db.relationship("TeacherProfile", back_populates="user", uselist=False)
    student_projects = db.relationship(
        "ResearchProject",
        back_populates="student",
        foreign_keys="ResearchProject.student_id",
    )
    advised_projects = db.relationship(
        "ResearchProject",
        back_populates="advisor",
        foreign_keys="ResearchProject.advisor_id",
    )
    audit_logs = db.relationship("AuditLog", back_populates="user")
    report_snapshots = db.relationship("ReportSnapshot", back_populates="generated_by")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def role_slug(self):
        return self.role.slug if self.role else None

    @property
    def active_project(self):
        if not self.student_projects:
            return None
        return sorted(self.student_projects, key=lambda item: item.updated_at or item.created_at, reverse=True)[0]

    @property
    def is_active(self):
        return self.is_active_user


class StudentProfile(db.Model):
    __tablename__ = "student_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    registration_number = db.Column(db.String(40))
    research_line = db.Column(db.String(120))
    semester = db.Column(db.String(30))

    user = db.relationship("User", back_populates="student_profile")


class TeacherProfile(db.Model):
    __tablename__ = "teacher_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    department = db.Column(db.String(120))
    title = db.Column(db.String(80))

    user = db.relationship("User", back_populates="teacher_profile")


class ResearchProject(db.Model):
    __tablename__ = "research_projects"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    advisor_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    project_type = db.Column(db.String(40), default="TCC", nullable=False)
    title = db.Column(db.String(180), nullable=False)
    thematic_area = db.Column(db.String(120))
    theme = db.Column(db.Text)
    research_problem = db.Column(db.Text)
    hypothesis = db.Column(db.Text)
    general_objective = db.Column(db.Text)
    specific_objectives = db.Column(db.Text)
    justification = db.Column(db.Text)
    methodology_summary = db.Column(db.Text)
    keywords = db.Column(db.String(255))
    course_name = db.Column(db.String(120))
    status = db.Column(db.String(40), default="planning", nullable=False)
    start_date = db.Column(db.Date, default=date.today, nullable=False)
    target_completion_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    student = db.relationship("User", back_populates="student_projects", foreign_keys=[student_id])
    advisor = db.relationship("User", back_populates="advised_projects", foreign_keys=[advisor_id])
    sections = db.relationship(
        "ProjectSection",
        back_populates="project",
        cascade="all, delete-orphan",
        order_by="ProjectSection.display_order",
    )
    stages = db.relationship(
        "ResearchStage",
        back_populates="project",
        cascade="all, delete-orphan",
        order_by="ResearchStage.stage_order",
    )
    deadlines = db.relationship(
        "Deadline",
        back_populates="project",
        cascade="all, delete-orphan",
        order_by="Deadline.due_date",
    )
    references = db.relationship("ReferenceItem", back_populates="project", cascade="all, delete-orphan")
    bibliographic_searches = db.relationship(
        "BibliographicSearch",
        back_populates="project",
        cascade="all, delete-orphan",
        order_by="BibliographicSearch.updated_at.desc()",
    )
    progress_records = db.relationship(
        "ProgressRecord",
        back_populates="project",
        cascade="all, delete-orphan",
        order_by="ProgressRecord.recorded_at.desc()",
    )
    section_feedbacks = db.relationship("SectionFeedback", back_populates="project", cascade="all, delete-orphan")
    advisor_comments = db.relationship("AdvisorComment", back_populates="project", cascade="all, delete-orphan")
    alerts = db.relationship("RiskAlert", back_populates="project", cascade="all, delete-orphan")


class ProjectSection(db.Model):
    __tablename__ = "project_sections"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("research_projects.id"), nullable=False)
    key = db.Column(db.String(40), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text)
    status = db.Column(db.String(30), default="not_started", nullable=False)
    word_count = db.Column(db.Integer, default=0, nullable=False)
    display_order = db.Column(db.Integer, default=0, nullable=False)
    last_submitted_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    __table_args__ = (db.UniqueConstraint("project_id", "key", name="uq_project_section_key"),)

    project = db.relationship("ResearchProject", back_populates="sections")
    revisions = db.relationship(
        "SectionRevision",
        back_populates="section",
        cascade="all, delete-orphan",
        order_by="SectionRevision.version_number.desc()",
    )
    feedbacks = db.relationship(
        "SectionFeedback",
        back_populates="section",
        cascade="all, delete-orphan",
        order_by="SectionFeedback.created_at.desc()",
    )
    references = db.relationship("ReferenceItem", secondary=section_references, back_populates="sections")


class SectionRevision(db.Model):
    __tablename__ = "section_revisions"

    id = db.Column(db.Integer, primary_key=True)
    section_id = db.Column(db.Integer, db.ForeignKey("project_sections.id"), nullable=False)
    editor_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    content_snapshot = db.Column(db.Text)
    version_number = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)

    section = db.relationship("ProjectSection", back_populates="revisions")
    editor = db.relationship("User")


class SectionFeedback(db.Model):
    __tablename__ = "section_feedbacks"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("research_projects.id"), nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey("project_sections.id"), nullable=False)
    advisor_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status_tag = db.Column(db.String(40), default="guidance", nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)

    project = db.relationship("ResearchProject", back_populates="section_feedbacks")
    section = db.relationship("ProjectSection", back_populates="feedbacks")
    advisor = db.relationship("User")


class ResearchStage(db.Model):
    __tablename__ = "research_stages"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("research_projects.id"), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    stage_order = db.Column(db.Integer, default=0, nullable=False)
    due_date = db.Column(db.Date)
    completed_at = db.Column(db.DateTime)
    status = db.Column(db.String(30), default="pending", nullable=False)

    project = db.relationship("ResearchProject", back_populates="stages")
    checklist_items = db.relationship(
        "StageChecklistItem",
        back_populates="stage",
        cascade="all, delete-orphan",
        order_by="StageChecklistItem.id",
    )


class StageChecklistItem(db.Model):
    __tablename__ = "stage_checklist_items"

    id = db.Column(db.Integer, primary_key=True)
    stage_id = db.Column(db.Integer, db.ForeignKey("research_stages.id"), nullable=False)
    label = db.Column(db.String(180), nullable=False)
    is_done = db.Column(db.Boolean, default=False, nullable=False)

    stage = db.relationship("ResearchStage", back_populates="checklist_items")


class MethodologyModule(db.Model):
    __tablename__ = "methodology_modules"

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(60), unique=True, nullable=False)
    title = db.Column(db.String(120), nullable=False)
    overview = db.Column(db.Text)
    order_index = db.Column(db.Integer, default=0, nullable=False)

    lessons = db.relationship(
        "ModuleLesson",
        back_populates="module",
        cascade="all, delete-orphan",
        order_by="ModuleLesson.order_index",
    )


class ModuleLesson(db.Model):
    __tablename__ = "module_lessons"

    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey("methodology_modules.id"), nullable=False)
    slug = db.Column(db.String(60), unique=True, nullable=False)
    title = db.Column(db.String(120), nullable=False)
    summary = db.Column(db.Text)
    key_points = db.Column(db.Text)
    activity_prompt = db.Column(db.Text)
    practical_example = db.Column(db.Text)
    checklist_text = db.Column(db.Text)
    order_index = db.Column(db.Integer, default=0, nullable=False)

    module = db.relationship("MethodologyModule", back_populates="lessons")
    progress_entries = db.relationship("LessonProgress", back_populates="lesson", cascade="all, delete-orphan")


class LessonProgress(db.Model):
    __tablename__ = "lesson_progress"

    id = db.Column(db.Integer, primary_key=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey("module_lessons.id"), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    is_completed = db.Column(db.Boolean, default=False, nullable=False)
    reflection = db.Column(db.Text)
    checklist_done = db.Column(db.Boolean, default=False, nullable=False)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    __table_args__ = (db.UniqueConstraint("lesson_id", "student_id", name="uq_lesson_student"),)

    lesson = db.relationship("ModuleLesson", back_populates="progress_entries")
    student = db.relationship("User")


class ReferenceItem(db.Model):
    __tablename__ = "reference_items"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("research_projects.id"), nullable=False)
    source_type = db.Column(db.String(40), nullable=False)
    authors = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    year = db.Column(db.String(10))
    venue = db.Column(db.String(180))
    url = db.Column(db.String(255))
    doi = db.Column(db.String(120))
    notes = db.Column(db.Text)
    keywords = db.Column(db.String(255))
    reading_status = db.Column(db.String(30), default="to_read", nullable=False)
    is_favorite = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    project = db.relationship("ResearchProject", back_populates="references")
    tags = db.relationship("Tag", secondary=reference_tags, back_populates="references")
    sections = db.relationship("ProjectSection", secondary=section_references, back_populates="references")


class Tag(db.Model):
    __tablename__ = "tags"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), unique=True, nullable=False)

    references = db.relationship("ReferenceItem", secondary=reference_tags, back_populates="tags")


class BibliographicSearch(db.Model):
    __tablename__ = "bibliographic_searches"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("research_projects.id"), nullable=False)
    title = db.Column(db.String(160), nullable=False)
    keywords = db.Column(db.String(255))
    databases_consulted = db.Column(db.String(255))
    inclusion_criteria = db.Column(db.Text)
    exclusion_criteria = db.Column(db.Text)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    project = db.relationship("ResearchProject", back_populates="bibliographic_searches")
    entries = db.relationship(
        "SearchEntry",
        back_populates="search",
        cascade="all, delete-orphan",
        order_by="SearchEntry.created_at.desc()",
    )


class SearchEntry(db.Model):
    __tablename__ = "search_entries"

    id = db.Column(db.Integer, primary_key=True)
    search_id = db.Column(db.Integer, db.ForeignKey("bibliographic_searches.id"), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    authors = db.Column(db.String(255))
    year = db.Column(db.String(10))
    source = db.Column(db.String(180))
    was_selected = db.Column(db.Boolean, default=False, nullable=False)
    reading_notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)

    search = db.relationship("BibliographicSearch", back_populates="entries")


class ProgressRecord(db.Model):
    __tablename__ = "progress_records"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("research_projects.id"), nullable=False)
    category = db.Column(db.String(60), nullable=False)
    progress_value = db.Column(db.Integer, nullable=False)
    note = db.Column(db.String(255))
    recorded_at = db.Column(db.DateTime, default=utcnow, nullable=False)

    project = db.relationship("ResearchProject", back_populates="progress_records")


class AdvisorComment(db.Model):
    __tablename__ = "advisor_comments"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("research_projects.id"), nullable=False)
    advisor_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)

    project = db.relationship("ResearchProject", back_populates="advisor_comments")
    advisor = db.relationship("User")


class Deadline(db.Model):
    __tablename__ = "deadlines"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("research_projects.id"), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(30), default="planned", nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)

    project = db.relationship("ResearchProject", back_populates="deadlines")


class RiskAlert(db.Model):
    __tablename__ = "risk_alerts"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("research_projects.id"), nullable=False)
    alert_type = db.Column(db.String(40), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    severity = db.Column(db.String(20), default="info", nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)

    project = db.relationship("ResearchProject", back_populates="alerts")


class ReportSnapshot(db.Model):
    __tablename__ = "report_snapshots"

    id = db.Column(db.Integer, primary_key=True)
    scope = db.Column(db.String(60), nullable=False)
    summary_json = db.Column(db.Text, nullable=False)
    generated_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)

    generated_by = db.relationship("User", back_populates="report_snapshots")


class AuditLog(db.Model):
    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    entity_type = db.Column(db.String(60), nullable=False)
    entity_id = db.Column(db.Integer, nullable=False)
    action = db.Column(db.String(60), nullable=False)
    detail = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)

    user = db.relationship("User", back_populates="audit_logs")
