from app.modules.scoring.config import MIN_CONFIDENCE_TO_SCORE


def classify_score(score: int | None, analysis_confidence: int) -> str:
    if score is None or analysis_confidence < MIN_CONFIDENCE_TO_SCORE:
        return "Analise inconclusiva"

    if score >= 85:
        return "Excelente padrao de movimento"
    if score >= 70:
        return "Bom padrao, com pequenos ajustes"
    if score >= 50:
        return "Compensacoes relevantes detectadas"
    if score >= 30:
        return "Baixa competencia de movimento"
    return "Analise critica ou muito limitada"
