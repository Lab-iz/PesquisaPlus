from datetime import date, timedelta

from app.extensions import db
from app.models import MethodologyModule, ModuleLesson, Role, StudentProfile, TeacherProfile, User
from app.services.bibliographic_search_service import add_search_entry, create_search
from app.services.feedback_service import add_project_comment, add_section_feedback
from app.services.methodology_service import complete_lesson
from app.services.project_service import create_project, refresh_project_progress, update_section
from app.services.reference_service import create_reference


MODULE_BLUEPRINT = [
    {
        "slug": "fundamentos-pesquisa",
        "title": "Fundamentos de Pesquisa Cientifica",
        "overview": "Introduz pesquisa, problema, objetivos e relevancia academica.",
        "lessons": [
            {
                "slug": "introducao-pesquisa",
                "title": "Introducao a pesquisa cientifica",
                "summary": "Pesquisa como processo sistematico de producao de conhecimento.",
                "key_points": "Natureza da pesquisa; relevancia academica; problema como eixo.",
                "activity_prompt": "Escreva em 5 linhas por que seu tema merece investigacao.",
                "practical_example": "Exemplo: evasao em cursos hibridos e seus fatores institucionais.",
                "checklist_text": "Definiu contexto; delimitou publico; justificou relevancia.",
            },
            {
                "slug": "problema-e-hipotese",
                "title": "Tema, problema e hipotese",
                "summary": "Converte um interesse amplo em pergunta investigavel.",
                "key_points": "Recorte; clareza; viabilidade; relacao entre problema e hipotese.",
                "activity_prompt": "Formule um problema em formato de pergunta.",
                "practical_example": "Como estudantes de enfermagem utilizam bases cientificas no inicio do TCC?",
                "checklist_text": "Pergunta clara; delimitacao temporal; variaveis ou fenomeno central.",
            },
        ],
    },
    {
        "slug": "estrutura-escrita",
        "title": "Estrutura e Escrita do Trabalho",
        "overview": "Apoia a escrita cientifica por secoes e a producao de resumo.",
        "lessons": [
            {
                "slug": "estrutura-artigo-tcc",
                "title": "Estrutura de artigo e TCC",
                "summary": "Panorama das partes centrais e funcao de cada secao.",
                "key_points": "Introducao; fundamentacao; metodologia; resultados; conclusao.",
                "activity_prompt": "Mapeie qual secao do seu trabalho esta mais fragil.",
                "practical_example": "Comparacao de escopo e profundidade entre artigo e TCC.",
                "checklist_text": "Entendeu funcao de cada secao; localizou lacunas; definiu prioridade.",
            },
            {
                "slug": "resumo-e-abstract",
                "title": "Resumo e abstract",
                "summary": "Sintetiza tema, objetivo, metodo e contribuicao do estudo.",
                "key_points": "Texto unico; verbos claros; coesao; concisao.",
                "activity_prompt": "Escreva um resumo curto com 4 elementos obrigatorios.",
                "practical_example": "Resumo com tema, objetivo, metodo e resultado esperado.",
                "checklist_text": "Indicou tema; objetivo; metodo; resultado ou contribuicao.",
            },
        ],
    },
    {
        "slug": "referencias-etica",
        "title": "Citacao, Referencias e Integridade",
        "overview": "Ensina uso etico de fontes, citacao e organizacao bibliografica.",
        "lessons": [
            {
                "slug": "citacao-direta-indireta",
                "title": "Citacao direta e indireta",
                "summary": "Distingue reproducao literal e parafrase academica.",
                "key_points": "Etica; autoria; fidelidade; integracao critica da fonte.",
                "activity_prompt": "Transforme uma citacao direta em indireta mantendo o sentido.",
                "practical_example": "Parafrase com preservacao de autoria e conceito.",
                "checklist_text": "Indicou autoria; distinguiu citacao; evitou plagio textual.",
            },
            {
                "slug": "referencias-bibliograficas",
                "title": "Referencias bibliograficas",
                "summary": "Organiza dados essenciais para futura normalizacao.",
                "key_points": "Autor; titulo; ano; fonte; consistencia cadastral.",
                "activity_prompt": "Cadastre tres referencias essenciais do seu tema.",
                "practical_example": "Livro, artigo e site institucional com metadados completos.",
                "checklist_text": "Registrou autores; ano; fonte; observacoes de leitura.",
            },
        ],
    },
]


def seed_database(force=False):
    if not force and User.query.first():
        return

    _seed_roles()
    _seed_modules()
    _seed_users_and_projects()
    db.session.commit()


def _seed_roles():
    roles = {
        "student": ("Estudante", "Acessa trilhas, projeto e escrita."),
        "advisor": ("Orientador", "Acompanha orientandos, feedbacks e revisoes."),
        "admin": ("Coordenador", "Acompanha indicadores e gerencia parametros."),
    }
    for slug, values in roles.items():
        if Role.query.filter_by(slug=slug).first() is None:
            db.session.add(Role(slug=slug, name=values[0], description=values[1]))
    db.session.commit()


def _seed_modules():
    if MethodologyModule.query.first():
        return

    for order, module_data in enumerate(MODULE_BLUEPRINT, start=1):
        module = MethodologyModule(
            slug=module_data["slug"],
            title=module_data["title"],
            overview=module_data["overview"],
            order_index=order,
        )
        db.session.add(module)
        db.session.flush()
        for lesson_order, lesson_data in enumerate(module_data["lessons"], start=1):
            db.session.add(
                ModuleLesson(
                    module_id=module.id,
                    slug=lesson_data["slug"],
                    title=lesson_data["title"],
                    summary=lesson_data["summary"],
                    key_points=lesson_data["key_points"],
                    activity_prompt=lesson_data["activity_prompt"],
                    practical_example=lesson_data["practical_example"],
                    checklist_text=lesson_data["checklist_text"],
                    order_index=lesson_order,
                )
            )
    db.session.commit()


def _seed_users_and_projects():
    role_student = Role.query.filter_by(slug="student").first()
    role_advisor = Role.query.filter_by(slug="advisor").first()
    role_admin = Role.query.filter_by(slug="admin").first()

    helena = _create_user(
        "Prof. Helena Duarte",
        "helena@pesquisa.local",
        "advisor123",
        role_advisor,
        course_name="Metodologia da Pesquisa",
    )
    marcos = _create_user(
        "Prof. Marcos Azevedo",
        "marcos@pesquisa.local",
        "advisor123",
        role_advisor,
        course_name="Ciencias Humanas",
    )
    beatriz = _create_user(
        "Beatriz Moraes",
        "coordenacao@pesquisa.local",
        "admin123",
        role_admin,
        course_name="Coordenacao Academica",
    )
    ana = _create_user(
        "Ana Luiza Ferreira",
        "ana@pesquisa.local",
        "student123",
        role_student,
        course_name="Pedagogia",
    )
    bruno = _create_user(
        "Bruno Nascimento",
        "bruno@pesquisa.local",
        "student123",
        role_student,
        course_name="Administracao",
    )

    if ana.student_profile is None:
        db.session.add(StudentProfile(user_id=ana.id, registration_number="20240101", research_line="Tecnologias educacionais", semester="8"))
    if bruno.student_profile is None:
        db.session.add(StudentProfile(user_id=bruno.id, registration_number="20230217", research_line="Gestao e inovacao", semester="7"))
    if helena.teacher_profile is None:
        db.session.add(TeacherProfile(user_id=helena.id, department="Educacao", title="Dra."))
    if marcos.teacher_profile is None:
        db.session.add(TeacherProfile(user_id=marcos.id, department="Administracao", title="Dr."))
    db.session.commit()

    ana_project = create_project(
        ana,
        {
            "advisor_id": helena.id,
            "project_type": "TCC",
            "title": "Estrategias de escrita cientifica para estudantes ingressantes",
            "thematic_area": "Educacao",
            "theme": "Dificuldades de escrita academica em disciplinas de metodologia.",
            "research_problem": "Como uma trilha orientada pode reduzir a inseguranca de estudantes na redacao do TCC?",
            "general_objective": "Analisar como uma plataforma guiada apoia a autonomia na escrita cientifica.",
            "specific_objectives": "Mapear dificuldades recorrentes\nComparar entregas iniciais e revisadas\nDescrever percepcao dos estudantes",
            "justification": "O retrabalho em orientacoes de escrita compromete tempo pedagogico e qualidade do processo formativo.",
            "methodology_summary": "Pesquisa aplicada, abordagem qualitativa e analise documental de rascunhos.",
            "keywords": "escrita cientifica, tcc, autonomia, metodologia",
            "course_name": "Pedagogia",
            "start_date": date.today().isoformat(),
            "target_completion_date": (date.today() + timedelta(days=120)).isoformat(),
        },
    )

    bruno_project = create_project(
        bruno,
        {
            "advisor_id": marcos.id,
            "project_type": "Iniciacao Cientifica",
            "title": "Uso de dashboards academicos no acompanhamento de projetos de pesquisa",
            "thematic_area": "Administracao",
            "theme": "Gestao visual do progresso em pesquisa institucional.",
            "research_problem": "De que modo indicadores sinteticos apoiam orientadores na supervisao de projetos?",
            "general_objective": "Investigar contribuicoes de paineis de acompanhamento para a orientacao de pesquisa.",
            "specific_objectives": "Identificar indicadores uteis\nRelacionar indicadores e feedback\nObservar ganhos de acompanhamento",
            "justification": "A visibilidade fragmentada do progresso dificulta intervencoes pedagogicas oportunas.",
            "methodology_summary": "Estudo exploratorio com levantamento documental e entrevistas semiestruturadas.",
            "keywords": "dashboards, orientacao, pesquisa, acompanhamento",
            "course_name": "Administracao",
            "start_date": date.today().isoformat(),
            "target_completion_date": (date.today() + timedelta(days=150)).isoformat(),
        },
    )

    _populate_project(ana_project, ana, helena)
    _populate_project(bruno_project, bruno, marcos)

    for lesson in ModuleLesson.query.limit(3).all():
        complete_lesson(lesson, ana, "Reflexao registrada no seed.")
    for lesson in ModuleLesson.query.limit(2).all():
        complete_lesson(lesson, bruno, "Atividade concluida para acompanhamento.")

    db.session.commit()
    refresh_project_progress(ana_project, commit=True)
    refresh_project_progress(bruno_project, commit=True)
    _ = beatriz


def _populate_project(project, student, advisor):
    sections = {section.key: section for section in project.sections}
    update_section(
        sections["introduction"],
        "Este estudo discute os desafios recorrentes da escrita cientifica entre estudantes em fase inicial de TCC, destacando a necessidade de suporte institucional orientado por etapas.",
        "submitted",
        student,
    )
    update_section(
        sections["theoretical_framework"],
        "Autores sobre letramento academico, formacao para pesquisa e autoria estudantil orientam a fundamentacao teorica inicial do projeto.",
        "draft",
        student,
    )
    update_section(
        sections["methodology"],
        "A pesquisa adota abordagem qualitativa, com analise de producoes textuais e registros de orientacao.",
        "draft",
        student,
    )
    update_section(
        sections["abstract"],
        "O trabalho aborda dificuldades de escrita cientifica em estudantes ingressantes, com objetivo de analisar como uma plataforma guiada pode apoiar autonomia e clareza metodologica. O estudo utiliza abordagem qualitativa e espera contribuir para uma orientacao mais estruturada.",
        "draft",
        student,
    )

    add_section_feedback(
        sections["introduction"],
        advisor,
        "A introducao esta clara, mas vale explicitar melhor o recorte institucional e o publico pesquisado.",
        "review",
    )
    add_project_comment(project, advisor, "Priorize o alinhamento entre problema, objetivo e justificativa antes de ampliar a revisao.")

    create_reference(
        project,
        {
            "source_type": "artigo",
            "authors": "Silva, Joana; Pereira, Livia",
            "title": "Escrita academica e permanencia estudantil",
            "year": "2022",
            "venue": "Revista Brasileira de Educacao",
            "url": "https://example.org/artigo-escrita",
            "doi": "10.0000/exemplo.2022.01",
            "notes": "Dialoga com autonomia discente e mediacao pedagogica.",
            "keywords": "escrita academica, permanencia",
            "reading_status": "reading",
            "tags": "escrita, revisao",
            "section_ids": [sections["theoretical_framework"].id],
        },
        student,
    )
    create_reference(
        project,
        {
            "source_type": "livro",
            "authors": "Demo, Pedro",
            "title": "Pesquisa e construcao do conhecimento",
            "year": "2015",
            "venue": "Atlas",
            "notes": "Base para discussao metodologica.",
            "keywords": "metodologia, pesquisa",
            "reading_status": "done",
            "tags": "metodologia",
            "section_ids": [sections["methodology"].id],
        },
        student,
    )

    search = create_search(
        project,
        {
            "title": "Busca inicial em escrita cientifica",
            "keywords": "escrita cientifica AND estudantes AND metodologia",
            "databases_consulted": "Google Scholar; Scielo; ERIC",
            "inclusion_criteria": "Textos entre 2019 e 2025; foco em ensino superior.",
            "exclusion_criteria": "Textos sem relacao com producao academica de graduandos.",
            "notes": "Busca inicial para consolidar marco teorico.",
        },
        student,
    )
    add_search_entry(
        search,
        {
            "title": "Academic writing support systems in undergraduate programs",
            "authors": "Lee, Carter",
            "year": "2023",
            "source": "Journal of Higher Education Support",
            "was_selected": True,
            "reading_notes": "Selecionado por discutir fluxos guiados de orientacao.",
        },
        student,
    )
    add_search_entry(
        search,
        {
            "title": "Feedback cycles for capstone projects",
            "authors": "Santos, Helena",
            "year": "2021",
            "source": "Revista Educacao em Foco",
            "was_selected": False,
            "reading_notes": "Mantido como contexto, mas sem foco em escrita.",
        },
        student,
    )

    if project.stages:
        for checklist_item in project.stages[0].checklist_items:
            checklist_item.is_done = True
        project.stages[0].status = "completed"
        project.stages[0].completed_at = project.created_at
        if len(project.stages) > 1:
            project.stages[1].checklist_items[0].is_done = True
            project.stages[1].status = "in_progress"
            project.stages[1].due_date = date.today() + timedelta(days=8)
        if len(project.stages) > 2:
            project.stages[2].due_date = date.today() - timedelta(days=2)

    for deadline in project.deadlines[:2]:
        deadline.status = "done"

    db.session.commit()


def _create_user(full_name, email, password, role, course_name=None):
    user = User.query.filter_by(email=email).first()
    if user is None:
        user = User(
            full_name=full_name,
            email=email,
            role_id=role.id,
            course_name=course_name,
            institution="Instituicao Academica",
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
    return user
