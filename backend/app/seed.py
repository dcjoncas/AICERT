import json
from pathlib import Path

from .models import Question


def _default_questions():
    questions = []

    tracks = ["AI Engineer", "AI Solution Architect"]
    sections = [
        ("business", 1),
        ("functional", 2),
        ("technical", 3),
    ]

    for track in tracks:
        for level in range(1, 11):
            for section, difficulty in sections:
                for i in range(1, 9):
                    if track == "AI Engineer":
                        if section == "business":
                            question_text = (
                                f"[{track} L{level}] Business Question {i}: "
                                "Which option best reflects a sound business decision when introducing AI into an operating model?"
                            )
                            option_a = "Adopt AI everywhere immediately without prioritization"
                            option_b = "Tie AI use cases to measurable business outcomes, operating impact, and governance needs"
                            option_c = "Ignore adoption planning and change management"
                            option_d = "Choose tools first and define the business case later"
                        elif section == "functional":
                            question_text = (
                                f"[{track} L{level}] Functional Question {i}: "
                                "Which option best reflects a strong functional workflow design for an AI-enabled process?"
                            )
                            option_a = "Remove human review from all exception paths"
                            option_b = "Design clear workflow steps, handoffs, exception handling, and user responsibilities"
                            option_c = "Assume users will adapt without process design"
                            option_d = "Skip functional requirements if the model is strong"
                        else:
                            question_text = (
                                f"[{track} L{level}] Technical Question {i}: "
                                "Which option best reflects a strong technical approach for building an AI capability?"
                            )
                            option_a = "Deploy without observability, testing, or access controls"
                            option_b = "Use APIs, monitoring, security, and evaluation patterns suitable for production"
                            option_c = "Avoid architecture decisions until after go-live"
                            option_d = "Ignore model and infrastructure tradeoffs"

                    else:
                        if section == "business":
                            question_text = (
                                f"[{track} L{level}] Business Question {i}: "
                                "Which option best reflects strong architecture leadership in an AI business case?"
                            )
                            option_a = "Focus only on technology and ignore business value"
                            option_b = "Connect business priorities, risk, governance, and platform decisions"
                            option_c = "Avoid executive alignment and process ownership"
                            option_d = "Treat AI as a standalone experiment with no operating model"
                        elif section == "functional":
                            question_text = (
                                f"[{track} L{level}] Functional Question {i}: "
                                "Which option best reflects good solution architecture across user workflows?"
                            )
                            option_a = "Skip functional process mapping"
                            option_b = "Align workflows, exception paths, roles, and target-state behavior"
                            option_c = "Let the model define the process by itself"
                            option_d = "Remove control points from sensitive workflows"
                        else:
                            question_text = (
                                f"[{track} L{level}] Technical Question {i}: "
                                "Which option best reflects strong AI solution architecture?"
                            )
                            option_a = "Choose tools without considering integration, security, and scale"
                            option_b = "Design for architecture fit, controls, extensibility, and operational support"
                            option_c = "Ignore platform constraints and data boundaries"
                            option_d = "Skip environment strategy and deployment planning"

                    question_code = (
                        f"{'AIE' if track == 'AI Engineer' else 'AISA'}-"
                        f"L{level}-"
                        f"{section[:3].upper()}-"
                        f"Q{i:03d}"
                    )

                    questions.append(
                        {
                            "question_code": question_code,
                            "track": track,
                            "level": level,
                            "section": section,
                            "difficulty": difficulty,
                            "weight": 1.0,
                            "question_text": question_text,
                            "option_a": option_a,
                            "option_b": option_b,
                            "option_c": option_c,
                            "option_d": option_d,
                            "correct_option": "B",
                            "active": True,
                        }
                    )

    return questions


def _load_questions_from_json():
    backend_dir = Path(__file__).resolve().parent.parent
    data_dir = backend_dir / "data"
    json_file = data_dir / "questions.json"

    if not json_file.exists():
        return _default_questions()

    try:
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, list) and len(data) > 0:
            return data

        return _default_questions()
    except Exception:
        return _default_questions()


def build_questions():
    raw_questions = _load_questions_from_json()
    result = []

    for item in raw_questions:
        result.append(
            Question(
                question_code=item["question_code"],
                track=item["track"],
                level=item["level"],
                section=item["section"],
                difficulty=item.get("difficulty", 1),
                weight=item.get("weight", 1.0),
                question_text=item["question_text"],
                option_a=item["option_a"],
                option_b=item["option_b"],
                option_c=item["option_c"],
                option_d=item["option_d"],
                correct_option=item["correct_option"],
                active=item.get("active", True),
            )
        )

    return result