# PESQUISA+

Plataforma web institucional para preparacao de TCC e pesquisa academica, com foco em metodologia cientifica, escrita estruturada, resumo, organizacao de referencias, busca bibliografica, acompanhamento por orientador e indicadores institucionais.

## Objetivo pedagogico

O sistema foi desenhado para transformar a producao academica em um fluxo guiado e formativo. Em vez de funcionar como LMS generico ou repositorio de arquivos, o PESQUISA+ organiza o trabalho do estudante por etapas, registra progresso real do projeto e oferece ao orientador visibilidade sobre pendencias, devolutivas e sinais de atraso.

## Stack

- Python 3
- Flask
- Flask-SQLAlchemy
- Flask-Login
- Jinja2
- HTML5
- CSS3
- JavaScript puro
- SQLite no desenvolvimento
- Pytest

## Arquitetura proposta

- `app/auth`: autenticacao, cadastro e sessao
- `app/main`: landing page, dashboard do estudante e erros
- `app/projects`: criacao de projeto, estrutura guiada, secoes e cronograma
- `app/methodology`: modulos, licoes, checklist e progresso formativo
- `app/references`: cadastro, filtro e associacao de referencias
- `app/bibliographic_search`: registro de busca, criterios e artigos encontrados
- `app/advisor`: painel do orientador, feedbacks e observacoes
- `app/admin`: dashboard institucional, usuarios e catalogo
- `app/reports`: relatorios e exportacao CSV
- `app/services`: regras de negocio e calculo de progresso
- `app/models`: entidades do dominio academico
- `app/static`: design system, estilos e comportamento leve

## Funcionalidades implementadas

- Cadastro, login e RBAC por perfil
- Dashboard do estudante com progresso, pendencias, trilhas, feedbacks e alertas
- Dashboard do orientador com projetos vinculados, revisoes e atrasos
- Dashboard da coordenacao com indicadores institucionais
- Criacao e edicao de projetos de TCC, artigo e iniciacao cientifica
- Estrutura guiada para problema, objetivos, justificativa, metodologia e palavras-chave
- Escrita estruturada por secao com historico basico de versoes
- Feedback do orientador por secao e observacoes gerais do projeto
- Trilhas de metodologia com conteudo curto, checklist, atividade e exemplo
- Camada mock de sugestao textual para resumo academico
- Cadastro e organizacao de referencias com tags, favoritos e associacao a secoes
- Busca bibliografica guiada com criterios, bases consultadas e entradas selecionadas
- Cronograma por etapas com checklist e alertas simples de atraso
- Relatorios com resumo consolidado e exportacao CSV
- Seed data realista para demonstracao
- Testes basicos do nucleo funcional

## Funcionalidades preparadas para expansao

- Modelos de trilhas adicionais por curso
- Templates institucionais de TCC e artigo
- Normalizacao ABNT mais completa
- Integracao real com IA na camada de sugestao textual
- Snapshots e analises historicas mais avancadas
- Parametrizacao institucional de cursos, areas e linhas de pesquisa
- Alertas mais sofisticados e regras por calendario academico

## Estrutura do projeto

```text
pesquisa+/
├── app/
│   ├── admin/
│   ├── advisor/
│   ├── auth/
│   ├── bibliographic_search/
│   ├── main/
│   ├── methodology/
│   ├── models/
│   ├── projects/
│   ├── references/
│   ├── reports/
│   ├── services/
│   ├── static/
│   ├── templates/
│   ├── utils/
│   ├── __init__.py
│   ├── cli.py
│   └── extensions.py
├── tests/
├── .env.example
├── config.py
├── requirements.txt
├── run.py
└── README.md
```

## Como instalar

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

## Como rodar

```bash
flask --app run.py init-db
flask --app run.py seed
flask --app run.py run
```

Aplicacao local: `http://127.0.0.1:5000`

## Como popular o banco

```bash
flask --app run.py seed
```

Para recriar tudo do zero:

```bash
flask --app run.py reset-db
```

## Perfis seed e credenciais de desenvolvimento

Estas credenciais existem apenas para ambiente local e demonstracao. Nao sao exibidas na interface do sistema.

- Estudante: `ana@pesquisa.local` / `student123`
- Estudante: `bruno@pesquisa.local` / `student123`
- Orientador: `helena@pesquisa.local` / `advisor123`
- Orientador: `marcos@pesquisa.local` / `advisor123`
- Coordenacao: `coordenacao@pesquisa.local` / `admin123`

## Variaveis de ambiente

- `SECRET_KEY`
- `DATABASE_URL`
- `INSTITUTION_NAME`

## Telas principais

- Landing page institucional
- Login
- Cadastro
- Dashboard do estudante
- Dashboard do orientador
- Dashboard admin
- Lista de projetos
- Criacao e edicao de projeto
- Painel detalhado do projeto
- Editor por secao
- Trilhas de metodologia
- Licoes e atividades
- Referencias
- Busca bibliografica
- Relatorios
- Gestao de usuarios

## Camada de sugestao textual

O MVP nao depende de IA externa para funcionar. A camada atual:

- analisa o resumo por elementos esperados
- identifica ausencias de tema, objetivo, metodo e resultado
- sugere ajustes de clareza e completude
- deixa a arquitetura pronta para acoplar um provedor real depois

Ela atua como apoio pedagogico e nunca como autoria final obrigatoria do estudante.

## Testes

```bash
pytest
```

Cobertura priorizada:

- login
- restricao por perfil
- criacao de projeto
- atualizacao de secao
- cadastro de referencia
- registro de feedback
- exportacao simples de relatorio

## Fluxos validados no MVP

1. Estudante faz login, cria projeto e entra no painel do trabalho.
2. Estudante acessa trilhas de metodologia e registra conclusao de licoes.
3. Estudante escreve secoes, salva rascunhos e acompanha completude.
4. Estudante cadastra referencias e organiza busca bibliografica.
5. Orientador acessa projetos vinculados e registra feedback por secao.
6. Coordenacao acompanha indicadores e exporta dados em CSV.

## Observacoes finais

- A interface nao exibe credenciais, segredos ou instrucoes operacionais.
- O banco de desenvolvimento usa SQLite.
- O projeto foi estruturado para evoluir sem virar monolito confuso nas rotas.
