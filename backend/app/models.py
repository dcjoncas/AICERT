
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Text, DateTime
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True)
    question_code = Column(String(50), unique=True, index=True, nullable=False)
    track = Column(String(100), nullable=False, index=True)
    level = Column(Integer, nullable=False, index=True)
    section = Column(String(50), nullable=False, index=True)
    difficulty = Column(Integer, nullable=False, default=1)
    weight = Column(Float, nullable=False, default=1.0)
    question_text = Column(Text, nullable=False)
    option_a = Column(Text, nullable=False)
    option_b = Column(Text, nullable=False)
    option_c = Column(Text, nullable=False)
    option_d = Column(Text, nullable=False)
    correct_option = Column(String(1), nullable=False)
    active = Column(Boolean, default=True, nullable=False)

class ExamAttempt(Base):
    __tablename__ = "exam_attempts"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    track = Column(String(100), nullable=False, index=True)
    attempted_level = Column(Integer, nullable=False)
    exam_name = Column(String(255), nullable=True)
    status = Column(String(30), default="in_progress", nullable=False)
    current_index = Column(Integer, default=0, nullable=False)
    total_questions = Column(Integer, default=0, nullable=False)
    raw_score = Column(Integer, default=0, nullable=False)
    percent_score = Column(Float, default=0.0, nullable=False)
    achieved_level = Column(Integer, default=0, nullable=False)
    passed = Column(Boolean, default=False, nullable=False)
    business_score = Column(Float, default=0.0, nullable=False)
    functional_score = Column(Float, default=0.0, nullable=False)
    technical_score = Column(Float, default=0.0, nullable=False)
    mcq_percent = Column(Float, default=0.0, nullable=False)
    essay_percent = Column(Float, default=0.0, nullable=False)
    scenario_percent = Column(Float, default=0.0, nullable=False)
    essay_prompt = Column(Text, nullable=True)
    essay_response = Column(Text, nullable=True)
    essay_feedback = Column(Text, nullable=True)
    scenario_prompt = Column(Text, nullable=True)
    scenario_response = Column(Text, nullable=True)
    scenario_feedback = Column(Text, nullable=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    submitted_at = Column(DateTime(timezone=True), nullable=True)

class ExamQuestion(Base):
    __tablename__ = "exam_questions"
    id = Column(Integer, primary_key=True, index=True)
    attempt_id = Column(Integer, ForeignKey("exam_attempts.id"), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False, index=True)
    order_index = Column(Integer, nullable=False)

class ExamAnswer(Base):
    __tablename__ = "exam_answers"
    id = Column(Integer, primary_key=True, index=True)
    attempt_id = Column(Integer, ForeignKey("exam_attempts.id"), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False, index=True)
    section = Column(String(50), nullable=False)
    selected_option = Column(String(1), nullable=False)
    is_correct = Column(Boolean, default=False, nullable=False)
    score_awarded = Column(Float, default=0.0, nullable=False)
    answered_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

class Certificate(Base):
    __tablename__ = "certificates"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    attempt_id = Column(Integer, ForeignKey("exam_attempts.id"), nullable=False, index=True)
    track = Column(String(100), nullable=False)
    certified_level = Column(Integer, nullable=False)
    certificate_code = Column(String(50), unique=True, index=True, nullable=False)
    issued_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
