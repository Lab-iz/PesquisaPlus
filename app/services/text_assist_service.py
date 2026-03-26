from app.utils.helpers import count_words


EXPECTED_ABSTRACT_PARTS = {
    "tema": ["tema", "contexto", "assunto"],
    "objetivo": ["objetivo", "prop", "investiga"],
    "metodo": ["metod", "procedimento", "abordagem"],
    "resultado": ["resultado", "espera-se", "contribui", "conclus"],
}


def analyze_abstract(text):
    lowered = (text or "").lower()
    presence = {
        key: any(token in lowered for token in tokens)
        for key, tokens in EXPECTED_ABSTRACT_PARTS.items()
    }
    missing = [label for label, found in presence.items() if not found]
    suggestions = []
    if "tema" in missing:
        suggestions.append("Explicite com mais nitidez o tema e o recorte do estudo.")
    if "objetivo" in missing:
        suggestions.append("Indique o objetivo central com verbo no infinitivo.")
    if "metodo" in missing:
        suggestions.append("Inclua como a pesquisa foi ou sera conduzida.")
    if "resultado" in missing:
        suggestions.append("Sinalize resultados esperados, contribuicoes ou conclusao parcial.")
    if count_words(text) < 110:
        suggestions.append("O resumo ainda esta curto para um texto academico robusto.")
    return {
        "word_count": count_words(text),
        "presence": presence,
        "missing": missing,
        "suggestions": suggestions,
    }


def section_guidance(section_key):
    guides = {
        "introduction": "Contextualize o tema, apresente o problema e anuncie a relevancia do estudo.",
        "theoretical_framework": "Organize autores, conceitos centrais e lacunas da literatura em blocos coesos.",
        "methodology": "Descreva tipo de pesquisa, procedimentos, participantes, instrumentos e criterios de analise.",
        "development_results": "Integre achados, analise critica e dialogo com a literatura.",
        "conclusion": "Retome objetivo, sintetize respostas e indique limites e desdobramentos.",
        "abstract": "Redija em bloco unico, com tema, objetivo, metodo e principais resultados ou expectativas.",
        "references": "Mantenha consistencia de autoria, ano, titulo e fonte para futura normalizacao.",
    }
    return guides.get(section_key, "Organize a secao com foco em clareza, coesao e consistencia academica.")
