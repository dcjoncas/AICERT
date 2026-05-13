import json, os, random, urllib.request
from datetime import datetime
from html import escape
from math import cos, pi, sin
from pathlib import Path
from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from .database import Base, SessionLocal, engine
from .models import User, Question, ExamAttempt, ExamAnswer, Certificate
from .auth import hash_password, verify_password
from .schemas import RegisterRequest, LoginRequest, DevReadyLaunchRequest, StartExamRequest, SubmitExamRequest, RetakeRequest
from .seed import build_questions

app = FastAPI(title="AICERT API", version="1.3.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
Base.metadata.create_all(bind=engine)
BACKEND_DIR = Path(__file__).resolve().parent.parent
PROJECT_DIR = BACKEND_DIR.parent
FRONTEND_DIR = PROJECT_DIR / "frontend"
RESULTS_DIR = BACKEND_DIR / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
if FRONTEND_DIR.exists(): app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")
def dbs(): return SessionLocal()
def admin_emails():
    raw = os.getenv("AICERT_ADMIN_EMAILS","")
    return {x.strip().lower() for x in raw.split(",") if x.strip()}
def is_admin(user): return bool(getattr(user, "is_admin", False) or user.email.lower() in admin_emails())
def section_sort_key(s): return {"business":1,"functional":2,"technical":3}.get((s or "").lower(),99)
def exam_name(track, level): return f"AICERT Level {level} Validation - {track}"
def result_file(payload): (RESULTS_DIR / f"attempt_{payload.get('attempt_id','unknown')}.json").write_text(json.dumps(payload, indent=2), encoding='utf-8')
def public_user(user): return {"id":user.id,"full_name":user.full_name,"email":user.email,"is_admin":is_admin(user)}
def devready_email(profile_id, email):
    clean = (email or "").strip().lower()
    if clean and "@" in clean: return clean
    safe_profile = "".join(ch.lower() if ch.isalnum() else "-" for ch in str(profile_id or "candidate")).strip("-") or "candidate"
    return f"devready+{safe_profile}@devready.local"
def devready_track(payload):
    value = " ".join([payload.badge_role_key or "", payload.badge_role or "", payload.badge_title or ""]).lower()
    if "architect" in value or "principal" in value: return "AI Solution Architect"
    return "AI Engineer"
def devready_level(payload):
    raw = (payload.badge_level or payload.certificate_id or payload.exam_id or "").upper()
    digits = "".join(ch for ch in raw if ch.isdigit())
    if not digits: return 1
    return max(1, min(10, int(digits)))
def parse_json(v):
    if not v: return None
    try: return json.loads(v)
    except: return {"summary": v}
def ai_grade(kind, track, level, prompt_text, response_text):
    key = os.getenv("OPENAI_API_KEY","").strip()
    if key:
        prompt = f"Return ONLY JSON with keys: percent, summary, why, strengths, weaknesses, business_assessment, functional_assessment, technical_assessment, creativity, clarity. Kind:{kind} Track:{track} Level:{level} Prompt:{prompt_text} Response:{response_text}"
        body = {"model":"gpt-4.1-mini","input":prompt}
        req = urllib.request.Request("https://api.openai.com/v1/responses", data=json.dumps(body).encode(), headers={"Content-Type":"application/json","Authorization":f"Bearer {key}"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                payload = json.loads(resp.read().decode())
            txt = ""
            for item in payload.get("output",[]):
                for c in item.get("content",[]):
                    if c.get("type")=="output_text": txt += c.get("text","")
            if txt.strip(): return json.loads(txt.strip())
        except Exception:
            pass
    txt = (response_text or "").lower(); words = len(txt.split()); score = 20 + (20 if words>150 else 0) + (15 if words>300 else 0) + (10 if words>500 else 0)
    for kw in ["business","functional","technical","architecture","security","governance","api","cloud","model","workflow","integration","testing"]:
        if kw in txt: score += 2
    score = min(92, score)
    return {"percent":score,"summary":f"{kind.title()} response scored with fallback analysis.","why":"Based on depth, coverage, and breadth across business, functional, and technical dimensions.","strengths":["Response length and detail were considered.","Relevant AI and delivery concepts were identified where present."],"weaknesses":["Fallback scoring is less precise than AI-assisted evaluation.","The response may need stronger evidence, structure, and implementation detail."],"business_assessment":"Business framing was evaluated based on value, governance, and organizational impact signals.","functional_assessment":"Functional assessment looked for workflow thinking, users, handoffs, and exception handling.","technical_assessment":"Technical assessment looked for architecture, security, APIs, models, and implementation ideas.","creativity":"Creativity was inferred from originality and solution framing.","clarity":"Clarity was inferred from structure, readability, and completeness."}
def attempt_questions(db, a):
    qs = db.query(Question).filter(Question.track==a.track, Question.level==a.attempted_level, Question.active==True).all()
    return sorted(qs, key=lambda q:(section_sort_key(q.section), q.id))[:a.total_questions]
def review_rows(db, a):
    qs = attempt_questions(db,a); ans = {x.question_id:x for x in db.query(ExamAnswer).filter(ExamAnswer.attempt_id==a.id).all()}; rows=[]
    for idx,q in enumerate(qs,1):
        sel = ans.get(q.id)
        rows.append({"index":idx,"question_id":q.id,"question_code":q.question_code,"section":q.section,"question_text":q.question_text,"option_a":q.option_a,"option_b":q.option_b,"option_c":q.option_c,"option_d":q.option_d,"selected_option":sel.selected_option if sel else "","correct_option":q.correct_option,"is_correct":sel.is_correct if sel else False})
    return rows
@app.on_event("startup")
def startup():
    db = dbs()
    try:
        existing = {q.question_code: q for q in db.query(Question).all()}
        for seeded in build_questions():
            q = existing.get(seeded.question_code)
            if not q:
                db.add(seeded)
                continue
            q.track = seeded.track
            q.level = seeded.level
            q.section = seeded.section
            q.difficulty = seeded.difficulty
            q.weight = seeded.weight
            q.question_text = seeded.question_text
            q.option_a = seeded.option_a
            q.option_b = seeded.option_b
            q.option_c = seeded.option_c
            q.option_d = seeded.option_d
            q.correct_option = seeded.correct_option
            q.active = seeded.active
        db.commit()
    finally: db.close()
@app.get("/", include_in_schema=False)
def root():
    f = FRONTEND_DIR / "index.html"
    return FileResponse(str(f)) if f.exists() else JSONResponse({"message":"Candidate app not found"}, status_code=404)
@app.get("/admin", include_in_schema=False)
def admin_page():
    f = FRONTEND_DIR / "admin.html"
    return FileResponse(str(f)) if f.exists() else JSONResponse({"message":"Admin app not found"}, status_code=404)
@app.get("/results", include_in_schema=False)
def results_page():
    f = FRONTEND_DIR / "results.html"
    return FileResponse(str(f)) if f.exists() else JSONResponse({"message":"Results page not found"}, status_code=404)
@app.post("/api/register")
def register(payload: RegisterRequest):
    db = dbs()
    try:
        if db.query(User).filter(User.email==payload.email).first(): raise HTTPException(status_code=400, detail="Email already registered")
        u = User(full_name=payload.full_name, email=payload.email, password_hash=hash_password(payload.password), is_admin=payload.email.lower() in admin_emails())
        db.add(u); db.commit(); db.refresh(u)
        return {"message":"User registered successfully","user":{"id":u.id,"full_name":u.full_name,"email":u.email,"is_admin":is_admin(u)}}
    finally: db.close()
@app.post("/api/login")
def login(payload: LoginRequest):
    db = dbs()
    try:
        u = db.query(User).filter(User.email==payload.email).first()
        if not u or not verify_password(payload.password, u.password_hash): raise HTTPException(status_code=401, detail="Invalid email or password")
        return {"message":"Login successful","user":{"id":u.id,"full_name":u.full_name,"email":u.email,"is_admin":is_admin(u)}}
    finally: db.close()
@app.post("/api/devready-launch")
def devready_launch(payload: DevReadyLaunchRequest):
    if not (payload.profile_id or "").strip():
        raise HTTPException(status_code=400, detail="DevReady profile id is required")
    db = dbs()
    try:
        email = devready_email(payload.profile_id, payload.email)
        name = (payload.full_name or "").strip() or f"DevReady Candidate {payload.profile_id}"
        u = db.query(User).filter(User.email==email).first()
        created = False
        if not u:
            seed_password = f"devready:{email}:{payload.profile_id or ''}"
            u = User(full_name=name, email=email, password_hash=hash_password(seed_password), is_admin=email in admin_emails())
            db.add(u); db.commit(); db.refresh(u)
            created = True
        elif name and u.full_name != name:
            u.full_name = name
            db.commit(); db.refresh(u)
        return {
            "message": "DevReady launch accepted",
            "created": created,
            "user": {"id": u.id, "full_name": u.full_name, "email": u.email, "is_admin": is_admin(u)},
            "exam": {
                "profile_id": payload.profile_id or "",
                "badge_role": payload.badge_role or "",
                "badge_role_key": payload.badge_role_key or "",
                "badge_level": payload.badge_level or "",
                "badge_title": payload.badge_title or "",
                "exam_id": payload.exam_id or "",
                "exam_version": payload.exam_version or "",
                "certificate_id": payload.certificate_id or "",
            },
            "track": devready_track(payload),
            "level": devready_level(payload),
        }
    finally: db.close()
@app.get("/api/tracks")
def tracks(): return {"tracks":[{"id":"AI Engineer","name":"AI Engineer"},{"id":"AI Solution Architect","name":"AI Solution Architect"}]}
@app.get("/api/levels")
def levels():
    labels = {
        1:"Level 1 - Foundations",
        2:"Level 2 - Applied Basics",
        3:"Level 3 - Practitioner",
        4:"Level 4 - Delivery Ready",
        5:"Level 5 - Production Builder",
        6:"Level 6 - Advanced Operator",
        7:"Level 7 - Lead Implementer",
        8:"Level 8 - Enterprise Designer",
        9:"Level 9 - Principal Strategist",
        10:"Level 10 - Executive Architect",
    }
    return {"levels":[{"level":i,"label":labels[i]} for i in range(1,11)]}
@app.get("/api/my-attempts")
def my_attempts(user_id:int=Query(...)):
    db = dbs()
    try:
        arr = db.query(ExamAttempt).filter(ExamAttempt.user_id==user_id).order_by(ExamAttempt.id.desc()).all()
        return {"attempts":[{"id":a.id,"exam_name":a.exam_name,"track":a.track,"attempted_level":a.attempted_level,"status":a.status,"current_index":a.current_index,"total_questions":a.total_questions,"percent_score":a.percent_score,"achieved_level":a.achieved_level,"passed":a.passed,"started_at":a.started_at.isoformat() if a.started_at else None,"submitted_at":a.submitted_at.isoformat() if a.submitted_at else None} for a in arr]}
    finally: db.close()
@app.post("/api/start-exam")
@app.post("/api/exams/start")
def start_exam(payload: StartExamRequest):
    db = dbs()
    try:
        if not db.query(User).filter(User.id==payload.user_id).first(): raise HTTPException(status_code=404, detail="User not found")
        qs = db.query(Question).filter(Question.track==payload.track, Question.level==payload.level, Question.active==True).all()
        if not qs: raise HTTPException(status_code=404, detail="No questions found for the selected track and level")
        qs = sorted(qs, key=lambda q:(section_sort_key(q.section), q.id))[:20]
        a = ExamAttempt(user_id=payload.user_id, track=payload.track, attempted_level=payload.level, exam_name=exam_name(payload.track,payload.level), status="mcq_in_progress", current_index=0, total_questions=len(qs))
        db.add(a); db.commit(); db.refresh(a)
        return {"attempt_id":a.id,"exam_name":a.exam_name,"track":a.track,"attempted_level":a.attempted_level,"duration_minutes":60,"status":a.status,"questions":[{"id":q.id,"question_code":q.question_code,"section":q.section,"question_text":q.question_text,"option_a":q.option_a,"option_b":q.option_b,"option_c":q.option_c,"option_d":q.option_d} for q in qs]}
    finally: db.close()
@app.post("/api/attempts/{attempt_id}/progress")
def progress(attempt_id:int, current_index:int=Query(...), user_id:int=Query(...)):
    db = dbs()
    try:
        a = db.query(ExamAttempt).filter(ExamAttempt.id==attempt_id).first()
        if not a: raise HTTPException(status_code=404, detail="Attempt not found")
        if a.user_id != user_id: raise HTTPException(status_code=403, detail="Not allowed")
        a.current_index = max(0,current_index); db.commit()
        return {"message":"Progress updated","attempt_id":a.id,"current_index":a.current_index,"total_questions":a.total_questions}
    finally: db.close()
@app.post("/api/submit-exam")
@app.post("/api/exams/submit")
def submit_exam(payload: SubmitExamRequest):
    db = dbs()
    try:
        a = db.query(ExamAttempt).filter(ExamAttempt.id==payload.attempt_id).first()
        if not a: raise HTTPException(status_code=404, detail="Exam attempt not found")
        qs = attempt_questions(db,a)
        if not qs: raise HTTPException(status_code=404, detail="No questions found for scoring")
        db.query(ExamAnswer).filter(ExamAnswer.attempt_id==a.id).delete()
        amap = {int(x.question_id):x.selected_option.upper() for x in payload.answers}
        correct = bt = bc = ft = fc = tt = tc = 0
        for q in qs:
            sel = amap.get(q.id,""); ok = sel == (q.correct_option or "").upper(); correct += 1 if ok else 0
            sec = (q.section or "").lower()
            if sec=="business": bt += 1; bc += 1 if ok else 0
            elif sec=="functional": ft += 1; fc += 1 if ok else 0
            elif sec=="technical": tt += 1; tc += 1 if ok else 0
            db.add(ExamAnswer(attempt_id=a.id, question_id=q.id, selected_option=sel if sel else "", is_correct=ok, section=q.section, score_awarded=1.0 if ok else 0.0))
        mcq = round((correct/len(qs))*100,2) if qs else 0.0; bus = round((bc/bt)*100,2) if bt else 0.0; fun = round((fc/ft)*100,2) if ft else 0.0; tech = round((tc/tt)*100,2) if tt else 0.0
        final = round(mcq, 2)
        lvl = a.attempted_level
        if final >= 90: ach, passed = lvl, True
        elif final >= 82: ach, passed = max(1,lvl-1), True
        elif final >= 74: ach, passed = max(1,lvl-2), True
        elif final >= 66: ach, passed = max(1,lvl-3), True
        else: ach, passed = 0, False
        a.raw_score=correct; a.mcq_percent=mcq; a.essay_percent=0.0; a.scenario_percent=0.0; a.percent_score=final; a.business_score=bus; a.functional_score=fun; a.technical_score=tech; a.achieved_level=ach; a.passed=passed; a.essay_response=None; a.essay_feedback=None; a.scenario_response=None; a.scenario_feedback=None; a.status="submitted"; a.submitted_at=datetime.utcnow(); a.current_index=a.total_questions
        db.commit(); db.refresh(a)
        cert_url = None
        if passed and ach > 0:
            code = f"AICERT-{a.id:06d}"
            if not db.query(Certificate).filter(Certificate.attempt_id==a.id).first(): db.add(Certificate(user_id=a.user_id, attempt_id=a.id, track=a.track, certified_level=ach, certificate_code=code)); db.commit()
            cert_url = f"/api/certificate/{a.id}"
        u = db.query(User).filter(User.id==a.user_id).first()
        result_file({"attempt_id":a.id,"exam_name":a.exam_name,"candidate_name":u.full_name if u else "","candidate_email":u.email if u else "","track":a.track,"attempted_level":a.attempted_level,"raw_score":a.raw_score,"total_questions":len(qs),"mcq_percent":a.mcq_percent,"percent_score":a.percent_score,"business_score":a.business_score,"functional_score":a.functional_score,"technical_score":a.technical_score,"achieved_level":a.achieved_level,"passed":a.passed,"submitted_at":a.submitted_at.isoformat() if a.submitted_at else None})
        msg = f"You passed Test Level {lvl} and earned Level {ach} certification." if passed and ach==lvl else (f"You did not quite reach Level {lvl}, but you demonstrated Level {ach} capability and earned Level {ach} certification." if passed and ach>0 else "You did not achieve a certification level on this attempt.")
        answer_key = [
            {
                "index": idx,
                "question_code": q.question_code,
                "section": q.section,
                "correct_option": q.correct_option,
                "correct_text": getattr(q, f"option_{(q.correct_option or '').lower()}", ""),
            }
            for idx, q in enumerate(qs, 1)
        ]
        return {"attempt_id":a.id,"exam_name":a.exam_name,"track":a.track,"attempted_level":a.attempted_level,"raw_score":a.raw_score,"total_questions":len(qs),"mcq_percent":a.mcq_percent,"percent_score":a.percent_score,"business_score":a.business_score,"functional_score":a.functional_score,"technical_score":a.technical_score,"achieved_level":a.achieved_level,"passed":a.passed,"message":msg,"certificate_url":cert_url,"results_url":f"/results?attempt_id={a.id}","answer_key":answer_key}
    finally: db.close()
@app.get("/api/attempt-review/{attempt_id}")
def attempt_review(attempt_id:int, user_id:int=Query(...)):
    db = dbs()
    try:
        a = db.query(ExamAttempt).filter(ExamAttempt.id==attempt_id).first()
        if not a: raise HTTPException(status_code=404, detail="Attempt not found")
        u = db.query(User).filter(User.id==user_id).first()
        if not u: raise HTTPException(status_code=404, detail="User not found")
        if a.user_id != u.id and not is_admin(u): raise HTTPException(status_code=403, detail="Not allowed")
        rows = review_rows(db,a)
        return {"attempt_id":a.id,"exam_name":a.exam_name,"track":a.track,"attempted_level":a.attempted_level,"percent_score":a.percent_score,"mcq_percent":a.mcq_percent,"business_score":a.business_score,"functional_score":a.functional_score,"technical_score":a.technical_score,"achieved_level":a.achieved_level,"passed":a.passed,"total_questions":len(rows),"questions":rows,"badge_url":f"/api/badge/{a.achieved_level}.svg" if a.achieved_level>0 else None,"certificate_url":f"/api/certificate/{a.id}" if a.passed and a.achieved_level>0 else None}
    finally: db.close()
@app.post("/api/retake")
def retake(payload: RetakeRequest):
    db = dbs()
    try:
        src = db.query(ExamAttempt).filter(ExamAttempt.id==payload.source_attempt_id).first()
        if not src: raise HTTPException(status_code=404, detail="Source attempt not found")
        if src.user_id != payload.user_id: raise HTTPException(status_code=403, detail="Not allowed")
        req = StartExamRequest(user_id=payload.user_id, track=src.track, level=src.attempted_level)
    finally: db.close()
    return start_exam(req)
@app.get("/api/admin/live")
def admin_live(user_id:int=Query(...)):
    db = dbs()
    try:
        u = db.query(User).filter(User.id==user_id).first()
        if not u or not is_admin(u): raise HTTPException(status_code=403, detail="This account is not marked as admin. Add its email to AICERT_ADMIN_EMAILS and restart the app.")
        arr = db.query(ExamAttempt).order_by(ExamAttempt.id.desc()).all(); payload=[]
        for a in arr:
            candidate = db.query(User).filter(User.id==a.user_id).first(); qs = attempt_questions(db,a)
            payload.append({"attempt_id":a.id,"exam_name":a.exam_name,"candidate_name":candidate.full_name if candidate else "","candidate_email":candidate.email if candidate else "","track":a.track,"attempted_level":a.attempted_level,"status":a.status,"current_index":a.current_index,"total_questions":a.total_questions,"percent_score":a.percent_score,"achieved_level":a.achieved_level,"started_at":a.started_at.isoformat() if a.started_at else None,"submitted_at":a.submitted_at.isoformat() if a.submitted_at else None,"questions":[{"question_id":q.id,"question_code":q.question_code,"section":q.section,"question_text":q.question_text,"correct_option":q.correct_option} for q in qs]})
        return {"attempts":payload}
    finally: db.close()
@app.post("/api/admin/retake/{attempt_id}")
def admin_retake(attempt_id:int, user_id:int=Query(...)):
    db = dbs()
    try:
        admin = db.query(User).filter(User.id==user_id).first()
        if not admin or not is_admin(admin): raise HTTPException(status_code=403, detail="Admin access required")
        a = db.query(ExamAttempt).filter(ExamAttempt.id==attempt_id).first()
        if not a: raise HTTPException(status_code=404, detail="Attempt not found")
        a.status="retake_requested"; db.commit(); return {"message":"Retake requested","attempt_id":a.id}
    finally: db.close()
@app.get("/api/badge/{level}.svg")
def badge(level:int):
    level = max(1, min(10, level)); ticks=""
    for i in range(10):
        angle = (-90 + i * 36) * pi / 180
        x1, y1 = 128 + cos(angle) * 87, 128 + sin(angle) * 87
        x2, y2 = 128 + cos(angle) * 108, 128 + sin(angle) * 108
        color = "#18b45b" if i < level else "#b22a36"
        ticks += f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="8" stroke-linecap="round"/>'
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="256" height="256" viewBox="0 0 256 256"><defs><radialGradient id="bg" cx="50%" cy="42%" r="74%"><stop offset="0%" stop-color="#25200f"/><stop offset="52%" stop-color="#111412"/><stop offset="100%" stop-color="#070807"/></radialGradient><linearGradient id="gold" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#f2d895"/><stop offset="100%" stop-color="#b98d3e"/></linearGradient></defs><rect width="256" height="256" rx="20" fill="url(#bg)"/><circle cx="128" cy="128" r="116" fill="none" stroke="#d7b56d" stroke-opacity=".36" stroke-width="2"/>{ticks}<circle cx="128" cy="128" r="68" fill="#0c0e0d" stroke="url(#gold)" stroke-width="3"/><text x="128" y="104" text-anchor="middle" font-family="Arial, sans-serif" font-size="18" font-weight="900" fill="#f2d895">AI</text><text x="128" y="150" text-anchor="middle" font-family="Arial, sans-serif" font-size="48" font-weight="900" fill="#ffffff">{level}</text><text x="128" y="181" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" font-weight="800" fill="#d7b56d">AICERT LEVEL</text></svg>'
    return Response(content=svg, media_type="image/svg+xml")
@app.get("/api/certificate/{attempt_id}", response_class=HTMLResponse)
def certificate(attempt_id:int):
    db = dbs()
    try:
        a = db.query(ExamAttempt).filter(ExamAttempt.id==attempt_id).first()
        if not a or a.achieved_level <= 0: raise HTTPException(status_code=404, detail="Certificate not found")
        u = db.query(User).filter(User.id==a.user_id).first(); c = db.query(Certificate).filter(Certificate.attempt_id==a.id).first()
        if not u or not c: raise HTTPException(status_code=404, detail="Certificate record not found")
        badge_url = f"/api/badge/{a.achieved_level}.svg"
        candidate_name = escape(u.full_name)
        track = escape(a.track)
        exam = escape(a.exam_name or "AICERT Certification Exam")
        code = escape(c.certificate_code)
        html = f"""<html><head><title>AICERT Certificate</title><style>
body{{font-family:Inter,Segoe UI,Arial,sans-serif;background:#080908;color:#111412;padding:36px;margin:0}}
.wrap{{max-width:1180px;margin:0 auto}}
.card{{position:relative;overflow:hidden;min-height:690px;border:1px solid #d7b56d;background:linear-gradient(135deg,#ffffff,#f8f4e9);box-shadow:0 32px 90px rgba(0,0,0,.42);display:grid;grid-template-columns:1.28fr .72fr;gap:32px;padding:56px}}
.card:before{{content:"";position:absolute;inset:22px;border:1px solid rgba(17,20,18,.16);pointer-events:none}}
.card:after{{content:"";position:absolute;right:-120px;bottom:-145px;width:420px;height:420px;border:54px solid rgba(215,181,109,.16);border-radius:50%}}
.content,.side{{position:relative;z-index:1}}
.topline{{display:flex;justify-content:space-between;gap:20px;color:#3f433d;font-size:12px;font-weight:900;letter-spacing:.12em;text-transform:uppercase}}
h1{{font-size:54px;line-height:1.03;margin:72px 0 10px;color:#111412}}
h2{{font-size:22px;margin:0 0 38px;color:#576051;font-weight:800;letter-spacing:.08em;text-transform:uppercase}}
p{{color:#5f665b;font-size:17px;line-height:1.65;margin:0}}
.name{{margin:16px 0;color:#111412;font-family:Georgia,Times New Roman,serif;font-size:58px;line-height:1.05}}
.track{{margin-top:14px;color:#17251d;font-size:26px;font-weight:900}}
.level{{display:inline-flex;align-items:center;min-height:58px;margin-top:24px;padding:0 24px;background:#111412;color:#f2d895;border:1px solid #d7b56d;font-size:30px;font-weight:900}}
.meta{{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:46px;color:#384037;font-size:15px;line-height:1.55}}
.meta div{{border-top:1px solid rgba(17,20,18,.16);padding-top:12px}}
.meta strong{{display:block;color:#111412;font-size:12px;letter-spacing:.1em;text-transform:uppercase;margin-bottom:4px}}
.side{{display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;border-left:1px solid rgba(17,20,18,.12);padding-left:30px}}
.badge img{{width:260px;height:260px;display:block}}
.seal{{margin-top:26px;color:#3f433d;font-size:13px;font-weight:900;letter-spacing:.12em;text-transform:uppercase}}
@media(max-width:820px){{body{{padding:18px}}.card{{grid-template-columns:1fr;padding:32px}}.side{{border-left:0;border-top:1px solid rgba(17,20,18,.12);padding:28px 0 0}}h1{{font-size:40px;margin-top:44px}}.name{{font-size:42px}}.meta{{grid-template-columns:1fr}}}}
</style></head><body><div class="wrap"><div class="card"><div class="content"><div class="topline"><span>AICERT</span><span>DevReady Credentialing</span></div><h1>Certificate of Achievement</h1><h2>Professional AI Capability Certification</h2><p>This certifies that</p><div class="name">{candidate_name}</div><p>has demonstrated competency in the</p><div class="track">{track}</div><div class="level">Level {a.achieved_level}</div><div class="meta"><div><strong>Exam</strong>{exam}</div><div><strong>Attempted Level</strong>{a.attempted_level}</div><div><strong>Final Score</strong>{a.percent_score}%</div><div><strong>Certificate ID</strong>{code}</div></div></div><div class="side"><div class="badge"><img src="{badge_url}" alt="Level badge" /></div><div class="seal">Verified 10-Level AI Credential</div></div></div></div></body></html>"""
        return HTMLResponse(content=html)
    finally: db.close()
