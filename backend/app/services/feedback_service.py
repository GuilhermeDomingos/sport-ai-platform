import json
import statistics
from pathlib import Path

from fastapi import HTTPException, status

from app.core.config import OUTPUT_DIR
from app.services.video_service import get_video_info


DEPTH_SCORES = {
    "below_parallel": 95,
    "parallel": 80,
    "above_parallel": 50,
}


def load_json_file(path: Path, required_detail: str | None = None) -> dict | None:
    if not path.is_file():
        if required_detail:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=required_detail,
            )
        return None

    try:
        with path.open("r", encoding="utf-8") as source:
            return json.load(source)
    except (OSError, json.JSONDecodeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nao foi possivel ler os dados para gerar feedback.",
        ) from exc


def generate_summary(overall_score: int) -> str:
    if overall_score >= 85:
        return (
            "Sua execu\u00e7\u00e3o geral foi muito boa, com bom controle "
            "t\u00e9cnico e consist\u00eancia."
        )
    if overall_score >= 70:
        return (
            "Sua execu\u00e7\u00e3o foi boa, mas ainda existem pontos "
            "t\u00e9cnicos importantes para melhorar."
        )
    return (
        "Sua execu\u00e7\u00e3o apresentou limita\u00e7\u00f5es t\u00e9cnicas "
        "importantes e merece aten\u00e7\u00e3o antes de aumentar carga ou "
        "intensidade."
    )


def generate_strengths(score: dict) -> list[str]:
    strengths: list[str] = []
    if score.get("depthScore", 0) >= 85:
        strengths.append("Boa profundidade na maioria das repeti\u00e7\u00f5es.")
    if score.get("stabilityScore", 0) >= 85:
        strengths.append("Boa estabilidade dos joelhos durante o movimento.")
    if score.get("symmetryScore", 0) >= 85:
        strengths.append("Boa simetria entre os lados esquerdo e direito.")
    if score.get("consistencyScore", 0) >= 85:
        strengths.append("Boa consist\u00eancia entre as repeti\u00e7\u00f5es.")
    return strengths


def generate_improvements(score: dict) -> list[str]:
    improvements: list[str] = []
    depth = score.get("depthScore", 0)
    stability = score.get("stabilityScore", 0)
    symmetry = score.get("symmetryScore", 0)
    consistency = score.get("consistencyScore", 0)

    if 70 <= depth < 85:
        improvements.append(
            "A profundidade est\u00e1 aceit\u00e1vel, mas ainda pode ser mais "
            "consistente."
        )
    elif depth < 70:
        improvements.append(
            "A profundidade do agachamento ficou abaixo do ideal em parte "
            "das repeti\u00e7\u00f5es."
        )

    if 70 <= stability < 85:
        improvements.append(
            "Foi detectada leve instabilidade dos joelhos em algumas "
            "repeti\u00e7\u00f5es."
        )
    elif stability < 70:
        improvements.append("A estabilidade dos joelhos ficou abaixo do ideal.")

    if 70 <= symmetry < 85:
        improvements.append(
            "Existe uma pequena diferen\u00e7a entre os lados durante o movimento."
        )
    elif symmetry < 70:
        improvements.append(
            "Foi detectada assimetria relevante entre os lados."
        )

    if 70 <= consistency < 85:
        improvements.append(
            "A execu\u00e7\u00e3o perdeu consist\u00eancia em algumas "
            "repeti\u00e7\u00f5es."
        )
    elif consistency < 70:
        improvements.append(
            "Houve queda importante de qualidade ao longo da s\u00e9rie."
        )
    return improvements


def generate_recommendations(score: dict) -> list[str]:
    recommendations: list[str] = []
    if score.get("depthScore", 0) < 70:
        recommendations.append(
            "Trabalhe mobilidade de tornozelo e quadril antes das "
            "s\u00e9ries principais."
        )
    if score.get("stabilityScore", 0) < 70:
        recommendations.append(
            "Reduza a carga e priorize controle dos joelhos durante a "
            "descida e subida."
        )
    if score.get("symmetryScore", 0) < 70:
        recommendations.append(
            "Inclua exerc\u00edcios unilaterais para melhorar equil\u00edbrio "
            "entre os lados."
        )
    if score.get("consistencyScore", 0) < 70:
        recommendations.append(
            "Diminua o ritmo ou reduza a carga para manter qualidade "
            "t\u00e9cnica at\u00e9 o fim da s\u00e9rie."
        )
    return recommendations


def _rep_quality(rep: dict) -> float:
    return statistics.mean(
        [
            DEPTH_SCORES.get(rep.get("depth"), 0),
            rep.get("stabilityScore", 0),
            rep.get("symmetryScore", rep.get("stabilityScore", 0)),
        ]
    )


def detect_fatigue_pattern(movement_analysis: dict | None) -> bool:
    if not movement_analysis:
        return False

    reps = movement_analysis.get("reps", [])
    if len(reps) < 2:
        return False

    sample_size = len(reps) // 2
    initial_quality = statistics.mean(
        _rep_quality(rep) for rep in reps[:sample_size]
    )
    final_quality = statistics.mean(
        _rep_quality(rep) for rep in reps[-sample_size:]
    )
    return final_quality < initial_quality


def _unique(messages: list[str]) -> list[str]:
    return list(dict.fromkeys(messages))


COMPONENT_LABELS = {
    "mobility": "Mobilidade",
    "stability": "Estabilidade",
    "symmetry": "Simetria",
    "amplitude_depth": "Amplitude e profundidade",
    "joint_kinematics": "Cinematica de joelho e quadril",
    "trunk_posture": "Postura de tronco",
    "motor_control": "Controle motor",
    "analysis_confidence": "Confiabilidade da analise",
}


def _axon_components(score: dict) -> list[dict]:
    components = score.get("components", [])
    return components if isinstance(components, list) else []


def generate_axon_strengths(score: dict) -> list[str]:
    strengths: list[str] = []
    for component in _axon_components(score):
        if component.get("name") == "analysis_confidence":
            continue
        if component.get("score", 0) >= 85:
            label = COMPONENT_LABELS.get(component.get("name"), component.get("name"))
            strengths.append(f"{label} em bom nivel tecnico.")
    return strengths


def generate_axon_improvements(score: dict) -> list[str]:
    improvements: list[str] = []
    for component in _axon_components(score):
        name = component.get("name")
        value = component.get("score", 0)
        if name == "analysis_confidence":
            if value < 60:
                improvements.append(
                    "A confiabilidade da analise ficou limitada pelo enquadramento ou pela deteccao corporal."
                )
            continue
        if value < 70:
            label = COMPONENT_LABELS.get(name, name)
            improvements.append(f"{label} foi o principal ponto de atencao.")
    return improvements


def generate_axon_recommendations(score: dict) -> list[str]:
    recommendations = score.get("recommendations", [])
    return recommendations if isinstance(recommendations, list) else []


def save_feedback(video_id: str, result: dict) -> None:
    output_dir = OUTPUT_DIR / video_id / "feedback"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "feedback.json"
    with output_file.open("w", encoding="utf-8") as output:
        json.dump(result, output, ensure_ascii=False, indent=2)


def generate_feedback(video_id: str) -> dict:
    video_info = get_video_info(video_id)
    normalized_id = video_info["videoId"]
    base_dir = OUTPUT_DIR / normalized_id
    scoring = load_json_file(
        base_dir / "score" / "scoring.json",
        "Scoring n\u00e3o encontrado. Execute score calculation antes.",
    )
    movement_analysis = load_json_file(
        base_dir / "movement" / "movement_analysis.json"
    )
    load_json_file(base_dir / "metrics" / "metrics.json")

    score = scoring.get("score", {}) if scoring else {}
    uses_axon_score = bool(score.get("score_method") and score.get("components"))
    if uses_axon_score:
        strengths = generate_axon_strengths(score)
        improvements = generate_axon_improvements(score)
        recommendations = generate_axon_recommendations(score)
        summary = score.get("summary") or generate_summary(score.get("overallScore") or 0)
    else:
        strengths = generate_strengths(score)
        improvements = generate_improvements(score)
        recommendations = generate_recommendations(score)
        summary = generate_summary(score.get("overallScore", 0))

    if detect_fatigue_pattern(movement_analysis):
        improvements.append(
            "Foi detectada perda t\u00e9cnica nas \u00faltimas "
            "repeti\u00e7\u00f5es, possivelmente relacionada \u00e0 fadiga."
        )
        recommendations.append(
            "Fa\u00e7a s\u00e9ries menores ou aumente o tempo de descanso "
            "para preservar a t\u00e9cnica."
        )

    result = {
        "videoId": normalized_id,
        "status": "feedback_generated",
        "movement": scoring.get("movement", "squat") if scoring else "squat",
        "summary": summary,
        "strengths": _unique(strengths),
        "improvements": _unique(improvements),
        "recommendations": _unique(recommendations),
        "warnings": score.get("warnings", []) if uses_axon_score else [],
    }
    save_feedback(normalized_id, result)
    return result
