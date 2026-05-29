from app.modules.scoring.exercises.squat import calculate_squat_score
from app.modules.scoring.exercises.squat_side import calculate_squat_side_score
from app.modules.scoring.schemas import ScoreResult, ScoringInput


SCORING_REGISTRY = {
    ("squat", "front"): calculate_squat_score,
    ("squat", "side"): calculate_squat_side_score,
}


def calculate_score(scoring_input: ScoringInput) -> ScoreResult:
    exercise_type = scoring_input.exercise_type.lower()
    camera_view = scoring_input.camera_view.value
    scoring_function = SCORING_REGISTRY.get((exercise_type, camera_view))

    if not scoring_function:
        raise ValueError(
            f"Unsupported scoring configuration: {(exercise_type, camera_view)}"
        )

    return scoring_function(scoring_input)
