import json
import os
import random
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from .auth import hash_password, verify_password
from .database import Base, SessionLocal, engine
from .models import Certificate, ExamAnswer, ExamAttempt, Question, User
from .schemas import (
    AnswerSubmission,
    LoginRequest,
    RegisterRequest,
    StartExamRequest,
    SubmitExamRequest,
)
from .seed import build_questions

app = FastAPI(title="AICERT API", version="3.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

BACKEND_DIR = Path(__file__).resolve().parent.parent
PROJECT_DIR = BACKEND_DIR.parent
FRONTEND_DIR = PROJECT_DIR / "frontend"
RESULTS_DIR = BACKEND_DIR / "results"

RESULTS_DIR.mkdir(parents=True, exist_ok=True)

if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")


def get_db() -> Session:
    return SessionLocal()


def admin_emails() -> set[str]:
    raw = os.getenv("AICERT_ADMIN_EMAILS", "")
    return {email.strip().lower() for email in raw.split(",") if email.strip()}


def is_admin_user(user: User) -> bool:
    if getattr(user, "is_admin", False):
        return True
    return user.email.lower() in admin_emails()


def generate_exam_name(track: str, level: int) -> str:
    first_words = [
        "Running",
        "Charging",
        "Flying",
        "Roaring",
        "Leaping",
        "Blazing",
        "Hunting",
        "Shadow",
        "Iron",
        "Silver",
        "Crimson",
        "Storm",
    ]
    animals = [
        "Bear",
        "Wolf",
        "Falcon",
        "Panther",
        "Fox",
        "Raven",
        "Tiger",
        "Stallion",
        "Viper",
        "Hawk",
        "Bison",
        "Jaguar",
    ]
    suffixes = [
        "Challenge",
        "Launch",
        "Sprint",
        "Run",
        "Trial",
        "Quest",
        "Drill",
        "Circuit",
    ]
    return f"{random.choice(first_words)} {random.choice(animals)} {random.choice(suffixes)} - {track} L{level}"


def section_sort_key(section_name: str) -> int:
    order = {"business": 1, "functional": 2, "technical": 3}
    return order.get((section_name or "").lower(), 99)


def write_result_file(payload: dict) -> None:
    attempt_id = payload.get("attempt_id", "unknown")
    file_path = RESULTS_DIR / f"attempt_{attempt_id}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)


@app.on_event("startup")
def startup_seed():
    db = get_db()
    try:
        existing = db.query(Question).count()
        if existing == 0:
            for q in build_questions():
                db.add(q)
            db.commit()
    finally:
        db.close()


@app.get("/", include_in_schema=False)
def candidate_root():
    index_file = FRONTEND_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return JSONResponse({"message": "Candidate app not found"}, status_code=404)


@app.get("/admin", include_in_schema=False)
def admin_root():
    admin_file = FRONTEND_DIR / "admin.html"
    if admin_file.exists():
        return FileResponse(str(admin_file))
    return JSONResponse({"message": "Admin app not found"}, status_code=404)


@app.post("/api/register")
def register(payload: RegisterRequest):
    db = get_db()
    try:
        existing = db.query(User).filter(User.email == payload.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")

        user = User(
            full_name=payload.full_name,
            email=payload.email,
            password_hash=hash_password(payload.password),
            is_admin=payload.email.lower() in admin_emails(),
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        return {
            "message": "User registered successfully",
            "user": {
                "id": user.id,
                "full_name": user.full_name,
                "email": user.email,
                "is_admin": is_admin_user(user),
            },
        }
    finally:
        db.close()


@app.post("/api/login")
def login(payload: LoginRequest):
    db = get_db()
    try:
        user = db.query(User).filter(User.email == payload.email).first()
        if not user or not verify_password(payload.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        return {
            "message": "Login successful",
            "user": {
                "id": user.id,
                "full_name": user.full_name,
                "email": user.email,
                "is_admin": is_admin_user(user),
            },
        }
    finally:
        db.close()


@app.get("/api/tracks")
def get_tracks():
    return {
        "tracks": [
            {"id": "AI Engineer", "name": "AI Engineer"},
            {"id": "AI Solution Architect", "name": "AI Solution Architect"},
        ]
    }


@app.get("/api/levels")
def get_levels():
    return {"levels": [{"level": i, "label": f"Test Level {i}"} for i in range(1, 11)]}


@app.get("/api/my-attempts")
def my_attempts(user_id: int = Query(...)):
    db = get_db()
    try:
        attempts = (
            db.query(ExamAttempt)
            .filter(ExamAttempt.user_id == user_id)
            .order_by(ExamAttempt.id.desc())
            .all()
        )

        return {
            "attempts": [
                {
                    "id": a.id,
                    "exam_name": a.exam_name,
                    "track": a.track,
                    "attempted_level": a.attempted_level,
                    "status": a.status,
                    "current_index": a.current_index,
                    "total_questions": a.total_questions,
                    "percent_score": a.percent_score,
                    "achieved_level": a.achieved_level,
                    "passed": a.passed,
                    "started_at": a.started_at.isoformat() if a.started_at else None,
                    "submitted_at": a.submitted_at.isoformat() if a.submitted_at else None,
                }
                for a in attempts
            ]
        }
    finally:
        db.close()


@app.post("/api/start-exam")
@app.post("/api/exams/start")
def start_exam(payload: StartExamRequest):
    db = get_db()
    try:
        user = db.query(User).filter(User.id == payload.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        questions = (
            db.query(Question)
            .filter(
                Question.track == payload.track,
                Question.level == payload.level,
                Question.active == True,  # noqa: E712
            )
            .all()
        )

        if not questions:
            raise HTTPException(status_code=404, detail="No questions found for the selected track and level")

        questions = sorted(questions, key=lambda q: (section_sort_key(q.section), q.id))
        selected_questions = questions[:20]
        exam_name = generate_exam_name(payload.track, payload.level)

        essay_prompts = [
            "Explain how an enterprise should evaluate adopting generative AI for a regulated business process. Cover business value, governance, architecture, risk, delivery execution, and optionally pseudocode.",
            "Design an AI operating model for a company trying to scale copilots and automation across multiple departments. Cover business priorities, functional workflow impact, technical controls, and optionally implementation sketches.",
            "Propose an AI-enabled modernization approach for a legacy application estate. Cover business case, functional process change, architecture, cloud, engineering execution, and optional code examples.",
        ]
        scenario_prompts = [
            "A recruiting function wants to reduce time-to-shortlist while maintaining governance and fairness. Explain how AI can support the process across business, functional, and technical dimensions.",
            "A field service team has inconsistent resolution times and weak knowledge reuse. Design an AI-enabled solution that improves operations while keeping controls and observability in place.",
            "A finance organization wants to automate document-heavy review while maintaining auditability. Propose an AI solution covering workflow, controls, architecture, and operational ownership.",
        ]

        attempt = ExamAttempt(
            user_id=payload.user_id,
            track=payload.track,
            attempted_level=payload.level,
            exam_name=exam_name,
            status="mcq_in_progress",
            current_index=0,
            total_questions=len(selected_questions),
            raw_score=0,
            percent_score=0.0,
            achieved_level=0,
            passed=False,
            business_score=0.0,
            functional_score=0.0,
            technical_score=0.0,
            mcq_percent=0.0,
            essay_percent=0.0,
            scenario_percent=0.0,
            essay_prompt=random.choice(essay_prompts),
            scenario_prompt=random.choice(scenario_prompts),
        )
        db.add(attempt)
        db.commit()
        db.refresh(attempt)

        result_questions = []
        for q in selected_questions:
            result_questions.append(
                {
                    "id": q.id,
                    "question_code": q.question_code,
                    "section": q.section,
                    "question_text": q.question_text,
                    "option_a": q.option_a,
                    "option_b": q.option_b,
                    "option_c": q.option_c,
                    "option_d": q.option_d,
                }
            )

        return {
            "attempt_id": attempt.id,
            "exam_name": attempt.exam_name,
            "track": attempt.track,
            "attempted_level": attempt.attempted_level,
            "duration_minutes": 60,
            "status": attempt.status,
            "questions": result_questions,
            "essay_prompt": attempt.essay_prompt,
            "scenario_prompt": attempt.scenario_prompt,
        }
    finally:
        db.close()


@app.post("/api/attempts/{attempt_id}/progress")
def update_attempt_progress(attempt_id: int, current_index: int = Query(...), user_id: int = Query(...)):
    db = get_db()
    try:
        attempt = db.query(ExamAttempt).filter(ExamAttempt.id == attempt_id).first()
        if not attempt:
            raise HTTPException(status_code=404, detail="Attempt not found")

        if attempt.user_id != user_id:
            raise HTTPException(status_code=403, detail="Not allowed")

        attempt.current_index = max(0, current_index)
        db.commit()

        return {
            "message": "Progress updated",
            "attempt_id": attempt.id,
            "current_index": attempt.current_index,
            "total_questions": attempt.total_questions,
        }
    finally:
        db.close()


@app.post("/api/submit-exam")
@app.post("/api/exams/submit")
def submit_exam(payload: SubmitExamRequest):
    db = get_db()
    try:
        attempt = db.query(ExamAttempt).filter(ExamAttempt.id == payload.attempt_id).first()
        if not attempt:
            raise HTTPException(status_code=404, detail="Exam attempt not found")

        questions = (
            db.query(Question)
            .filter(
                Question.track == attempt.track,
                Question.level == attempt.attempted_level,
                Question.active == True,  # noqa: E712
            )
            .all()
        )
        questions = sorted(questions, key=lambda q: (section_sort_key(q.section), q.id))[: attempt.total_questions]

        if not questions:
            raise HTTPException(status_code=404, detail="No questions found for scoring")

        db.query(ExamAnswer).filter(ExamAnswer.attempt_id == attempt.id).delete()

        answer_map = {int(a.question_id): a.selected_option.upper() for a in payload.answers}
        correct_count = 0

        business_total = business_correct = 0
        functional_total = functional_correct = 0
        technical_total = technical_correct = 0

        for q in questions:
            selected = answer_map.get(q.id, "")
            is_correct = selected == (q.correct_option or "").upper()

            if is_correct:
                correct_count += 1

            section = (q.section or "").lower()
            if section == "business":
                business_total += 1
                if is_correct:
                    business_correct += 1
            elif section == "functional":
                functional_total += 1
                if is_correct:
                    functional_correct += 1
            elif section == "technical":
                technical_total += 1
                if is_correct:
                    technical_correct += 1

            db.add(
                ExamAnswer(
                    attempt_id=attempt.id,
                    question_id=q.id,
                    selected_option=selected if selected else "",
                    is_correct=is_correct,
                    section=q.section,
                    score_awarded=1.0 if is_correct else 0.0,
                )
            )

        mcq_percent = round((correct_count / len(questions)) * 100, 2) if questions else 0.0
        business_score = round((business_correct / business_total) * 100, 2) if business_total else 0.0
        functional_score = round((functional_correct / functional_total) * 100, 2) if functional_total else 0.0
        technical_score = round((technical_correct / technical_total) * 100, 2) if technical_total else 0.0

        essay_percent = float(payload.essay_percent or 0.0)
        scenario_percent = float(payload.scenario_percent or 0.0)
        final_percent = round((mcq_percent * 0.40) + (essay_percent * 0.30) + (scenario_percent * 0.30), 2)

        attempted_level = attempt.attempted_level
        if final_percent >= 90:
            achieved_level = attempted_level
            passed = True
        elif final_percent >= 82:
            achieved_level = max(1, attempted_level - 1)
            passed = True
        elif final_percent >= 74:
            achieved_level = max(1, attempted_level - 2)
            passed = True
        elif final_percent >= 66:
            achieved_level = max(1, attempted_level - 3)
            passed = True
        else:
            achieved_level = 0
            passed = False

        attempt.raw_score = correct_count
        attempt.mcq_percent = mcq_percent
        attempt.essay_percent = essay_percent
        attempt.scenario_percent = scenario_percent
        attempt.percent_score = final_percent
        attempt.business_score = business_score
        attempt.functional_score = functional_score
        attempt.technical_score = technical_score
        attempt.achieved_level = achieved_level
        attempt.passed = passed
        attempt.essay_response = payload.essay_response
        attempt.essay_feedback = payload.essay_feedback
        attempt.scenario_response = payload.scenario_response
        attempt.scenario_feedback = payload.scenario_feedback
        attempt.status = "submitted"
        attempt.submitted_at = datetime.utcnow()
        attempt.current_index = attempt.total_questions

        db.commit()
        db.refresh(attempt)

        certificate_url = None
        if passed and achieved_level > 0:
            certificate_code = f"AICERT-{attempt.id:06d}"
            existing_cert = db.query(Certificate).filter(Certificate.attempt_id == attempt.id).first()
            if not existing_cert:
                db.add(
                    Certificate(
                        user_id=attempt.user_id,
                        attempt_id=attempt.id,
                        track=attempt.track,
                        certified_level=achieved_level,
                        certificate_code=certificate_code,
                    )
                )
                db.commit()
            certificate_url = f"/api/certificate/{attempt.id}"

        user = db.query(User).filter(User.id == attempt.user_id).first()

        result_payload = {
            "attempt_id": attempt.id,
            "exam_name": attempt.exam_name,
            "candidate_name": user.full_name if user else "",
            "candidate_email": user.email if user else "",
            "track": attempt.track,
            "attempted_level": attempt.attempted_level,
            "raw_score": attempt.raw_score,
            "mcq_percent": attempt.mcq_percent,
            "essay_percent": attempt.essay_percent,
            "scenario_percent": attempt.scenario_percent,
            "percent_score": attempt.percent_score,
            "business_score": attempt.business_score,
            "functional_score": attempt.functional_score,
            "technical_score": attempt.technical_score,
            "achieved_level": attempt.achieved_level,
            "passed": attempt.passed,
            "essay_prompt": attempt.essay_prompt,
            "essay_response": attempt.essay_response,
            "essay_feedback": attempt.essay_feedback,
            "scenario_prompt": attempt.scenario_prompt,
            "scenario_response": attempt.scenario_response,
            "scenario_feedback": attempt.scenario_feedback,
            "submitted_at": attempt.submitted_at.isoformat() if attempt.submitted_at else None,
        }
        write_result_file(result_payload)

        if passed and achieved_level == attempted_level:
            message = f"You passed Test Level {attempted_level} and earned Level {achieved_level} certification."
        elif passed and achieved_level > 0:
            message = f"You did not quite reach Level {attempted_level}, but you demonstrated Level {achieved_level} capability and earned Level {achieved_level} certification."
        else:
            message = "You did not achieve a certification level on this attempt."

        return {
            "attempt_id": attempt.id,
            "exam_name": attempt.exam_name,
            "track": attempt.track,
            "attempted_level": attempt.attempted_level,
            "raw_score": attempt.raw_score,
            "mcq_percent": attempt.mcq_percent,
            "essay_percent": attempt.essay_percent,
            "scenario_percent": attempt.scenario_percent,
            "percent_score": attempt.percent_score,
            "business_score": attempt.business_score,
            "functional_score": attempt.functional_score,
            "technical_score": attempt.technical_score,
            "achieved_level": attempt.achieved_level,
            "passed": attempt.passed,
            "message": message,
            "certificate_url": certificate_url,
        }
    finally:
        db.close()


@app.get("/api/results/{attempt_id}")
def get_results(attempt_id: int):
    db = get_db()
    try:
        attempt = db.query(ExamAttempt).filter(ExamAttempt.id == attempt_id).first()
        if not attempt:
            raise HTTPException(status_code=404, detail="Result not found")

        return {
            "attempt_id": attempt.id,
            "exam_name": attempt.exam_name,
            "track": attempt.track,
            "attempted_level": attempt.attempted_level,
            "mcq_percent": attempt.mcq_percent,
            "essay_percent": attempt.essay_percent,
            "scenario_percent": attempt.scenario_percent,
            "percent_score": attempt.percent_score,
            "business_score": attempt.business_score,
            "functional_score": attempt.functional_score,
            "technical_score": attempt.technical_score,
            "achieved_level": attempt.achieved_level,
            "passed": attempt.passed,
            "certificate_url": f"/api/certificate/{attempt.id}" if attempt.passed and attempt.achieved_level > 0 else None,
        }
    finally:
        db.close()


@app.get("/api/admin/live")
def admin_live(user_id: int = Query(...)):
    db = get_db()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not is_admin_user(user):
            raise HTTPException(status_code=403, detail="This account is not marked as admin. Add its email to AICERT_ADMIN_EMAILS and restart the app.")

        attempts = db.query(ExamAttempt).order_by(ExamAttempt.id.desc()).all()
        payload = []

        for a in attempts:
            candidate = db.query(User).filter(User.id == a.user_id).first()
            questions = (
                db.query(Question)
                .filter(
                    Question.track == a.track,
                    Question.level == a.attempted_level,
                    Question.active == True,  # noqa: E712
                )
                .all()
            )
            questions = sorted(questions, key=lambda q: (section_sort_key(q.section), q.id))[: a.total_questions]

            payload.append(
                {
                    "attempt_id": a.id,
                    "exam_name": a.exam_name,
                    "candidate_name": candidate.full_name if candidate else "",
                    "candidate_email": candidate.email if candidate else "",
                    "track": a.track,
                    "attempted_level": a.attempted_level,
                    "status": a.status,
                    "current_index": a.current_index,
                    "total_questions": a.total_questions,
                    "percent_score": a.percent_score,
                    "achieved_level": a.achieved_level,
                    "started_at": a.started_at.isoformat() if a.started_at else None,
                    "submitted_at": a.submitted_at.isoformat() if a.submitted_at else None,
                    "questions": [
                        {
                            "question_id": q.id,
                            "question_code": q.question_code,
                            "section": q.section,
                            "question_text": q.question_text,
                            "correct_option": q.correct_option,
                        }
                        for q in questions
                    ],
                }
            )

        return {"attempts": payload}
    finally:
        db.close()


@app.post("/api/admin/retake/{attempt_id}")
def admin_retake(attempt_id: int, user_id: int = Query(...)):
    db = get_db()
    try:
        admin_user = db.query(User).filter(User.id == user_id).first()
        if not admin_user or not is_admin_user(admin_user):
            raise HTTPException(status_code=403, detail="Admin access required")

        attempt = db.query(ExamAttempt).filter(ExamAttempt.id == attempt_id).first()
        if not attempt:
            raise HTTPException(status_code=404, detail="Attempt not found")

        attempt.status = "retake_requested"
        db.commit()

        return {"message": "Retake requested", "attempt_id": attempt.id}
    finally:
        db.close()


@app.get("/api/certificate/{attempt_id}", response_class=HTMLResponse)
def certificate(attempt_id: int):
    db = get_db()
    try:
        attempt = db.query(ExamAttempt).filter(ExamAttempt.id == attempt_id).first()
        if not attempt or attempt.achieved_level <= 0:
            raise HTTPException(status_code=404, detail="Certificate not found")

        user = db.query(User).filter(User.id == attempt.user_id).first()
        cert = db.query(Certificate).filter(Certificate.attempt_id == attempt.id).first()

        if not user or not cert:
            raise HTTPException(status_code=404, detail="Certificate record not found")

        html = f"""
        <html>
        <head>
            <title>AICERT Certificate</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background: #07140d;
                    color: #ffffff;
                    padding: 40px;
                    margin: 0;
                }}
                .card {{
                    max-width: 960px;
                    margin: 0 auto;
                    border: 3px solid #34c759;
                    padding: 48px;
                    background: #0f1e16;
                    border-radius: 20px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.35);
                }}
                .pill {{
                    display: inline-block;
                    padding: 8px 14px;
                    border-radius: 999px;
                    background: rgba(52, 199, 89, 0.14);
                    color: #7df09a;
                    margin-bottom: 18px;
                    font-size: 13px;
                }}
                h1 {{
                    font-size: 44px;
                    margin-bottom: 8px;
                }}
                h2 {{
                    font-size: 28px;
                    color: #9feab1;
                    margin-top: 0;
                }}
                .name {{
                    font-size: 42px;
                    font-weight: 700;
                    margin: 24px 0 8px 0;
                }}
                .level {{
                    font-size: 56px;
                    font-weight: 700;
                    margin: 24px 0;
                }}
                .meta {{
                    color: #d2ead9;
                    font-size: 18px;
                    line-height: 1.7;
                    margin-top: 30px;
                }}
            </style>
        </head>
        <body>
            <div class="card">
                <div class="pill">AICERT by DevReady</div>
                <h1>Certification of Achievement</h1>
                <h2>Professional AI Capability Certification</h2>
                <p>This certifies that</p>
                <div class="name">{user.full_name}</div>
                <p>has demonstrated competency in the <b>{attempt.track}</b> track and has earned</p>
                <div class="level">Level {attempt.achieved_level}</div>
                <div class="meta">
                    Exam: {attempt.exam_name}<br/>
                    Attempted Level: {attempt.attempted_level}<br/>
                    Final Score: {attempt.percent_score}%<br/>
                    Certificate ID: {cert.certificate_code}
                </div>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=html)
    finally:
        db.close()