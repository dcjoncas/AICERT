

git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/dcjoncas/AICERT.git
git push -u origin main


git rm --cached -r .
git commit --allow-empty -m "Remove secrets from history"
git filter-repo --invert-paths --path .env --path Readme.txt --force
git reflog expire --expire=now --all
git gc --prune=now --aggressive
git push origin main --force


gh repo create AICERT --private --source=. --remote=origin
git add .
git commit -m "Initial commit"
git push -u origin main

$env:AICERT_ADMIN_EMAILS="darrin.joncas@gmail.com"
python run.py
setx AICERT_ADMIN_EMAILS "darrin.joncas@gmail.com"
$env:AICERT_ADMIN_EMAILS="darrin.joncas@gmail.com"
Remove-Item .\aicert.db -Force
python run.py

cd backend
python -m venv venv
.\venv310\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python run.py

# Install git-filter-repo if not present (one-time)
# Via pip: pip install git-filter-repo
# Or download: https://github.com/newren/git-filter-repo

# Remove key from all history (assumes in Readme.txt or similar file)
git filter-repo --replace-text <(echo "s/YourOpenAIKeyHere/REDACTED/g") --force
# OR if whole line/file: git filter-repo --path Readme.txt --invert-paths --force
# (Adjust path/filename as needed; run git log to confirm commit)

git push origin --force --all
git push origin --force --tags   # if any tags


AICERT
Purpose
AICERT is an AI certification platform for DevReady that evaluates candidates across business, functional, and technical AI capability.
It starts with two certification tracks: - AI Solution Architect - AI Engineer
The platform uses a 10-level progression system. Each level represents broader depth, stronger judgment, and higher technical mastery.
The experience should feel like a professional testing platform: - secure login - candidate dashboard - timed exam page - countdown timer - submit and scoring - level outcome - certificate generation - certification history per user
The UI should visually align with DevReady style: modern, clean, dark, professional, and simple.
________________________________________
Core Concept
Each exam is 1 hour. Each exam measures a mix of: - business understanding - functional process thinking - technical AI skill - tooling and platform knowledge - coding and architecture judgment - cloud and deployment understanding - model and prompt understanding - governance, security, and responsible AI
The scoring logic should determine the candidate’s demonstrated level.
Example: - Candidate attempts Test Level 7 - If they score at Level 7 standard, they earn Level 7 Certification - If they fall short but still demonstrate Level 6 capability, they earn Level 6 Certification - If they underperform more significantly, they receive the highest level their score supports
This allows a single exam to still place the candidate accurately.
________________________________________
Level Framework
Level 1
Early-career technical practitioner with around 2 years of experience. Basic coding ability and basic AI awareness. Understands simple APIs, prompts, and common tools but needs guidance.
Level 2
Can build small working components independently. Understands model usage, simple integrations, and cloud basics. Can explain AI use cases in practical terms.
Level 3
Can develop usable AI features end to end with supervision. Understands prompts, APIs, vector basics, model limitations, testing, and deployment basics.
Level 4
Solid mid-level practitioner. Can design small AI solutions, code integrations, and reason about data, security, and performance. Can communicate with business teams effectively.
Level 5
Strong professional. Can own a scoped AI workstream. Balances technical choices, business outcomes, architecture tradeoffs, and implementation detail.
Level 6
Senior practitioner. Can lead solution design, implementation planning, and platform selection. Strong across delivery, governance, coding, and AI system design.
Level 7
Advanced expert. Can architect or engineer production-grade AI solutions across models, cloud, orchestration, evaluation, security, and enterprise integration. Strong judgment under ambiguity.
Level 8
Principal-level capability. Can standardize patterns, mentor teams, optimize enterprise AI operating models, and drive scalable architecture decisions.
Level 9
Elite cross-domain leader. Can unify business strategy, enterprise architecture, AI platform design, and engineering execution at scale.
Level 10
Master-level authority. Demonstrates broad and deep command across all relevant AI domains, from executive strategy to hands-on engineering, model design tradeoffs, enterprise governance, operations, and technical execution.
________________________________________
Two Certification Tracks
1) AI Solution Architect
Focus areas: - translating business needs into AI solutions - platform and vendor selection - enterprise architecture - systems integration - data flow design - security and governance - responsible AI - cost and scalability decisions - stakeholder communication - implementation roadmap thinking
Weighting for this track
•	Business and advisory: 25%
•	Functional solution design: 25%
•	Technical architecture: 30%
•	Governance, security, and operations: 20%
2) AI Engineer
Focus areas: - coding and implementation - APIs and orchestration - prompts and evaluation - agents and workflows - model integration - vector search and RAG - testing and debugging - cloud deployment - performance, monitoring, and reliability
Weighting for this track
•	Coding and engineering execution: 35%
•	AI technical foundations: 25%
•	Systems/platform integration: 20%
•	Business and product understanding: 20%
________________________________________
Exam Structure
Each exam is 60 minutes.
Recommended mix per exam: - 20 multiple choice questions - 8 scenario-based questions - 2 short written responses - 1 applied mini-case
Total: 31 questions/tasks
Question types: 1. Multiple choice 2. Multi-select 3. Rank / best option 4. Short text 5. Code review 6. Architecture decision scenario 7. Business case interpretation
This mix prevents shallow memorization.
________________________________________
Difficulty Design by Level
Test Level 1
Covers: - basic Python or JavaScript concepts - API basics - what AI/ML/LLM means - simple prompt concepts - basic cloud awareness - basic business communication
Test Level 2
Covers: - simple model usage - REST APIs - JSON handling - beginner cloud deployment concepts - intro security and responsible AI - practical business use cases
Test Level 3
Covers: - prompt quality - embeddings basics - vector search basics - debugging simple workflows - simple evaluation - requirements interpretation
Test Level 4
Covers: - component design - model tradeoffs - cost/performance basics - API orchestration - monitoring basics - solution mapping to business needs
Test Level 5
Covers: - production concerns - architecture decisions - RAG patterns - security controls - cloud implementation options - delivery planning and risk handling
Test Level 6
Covers: - enterprise integration - governance and compliance - platform comparisons - scalable evaluation methods - advanced coding scenarios - operational decision-making
Test Level 7
Covers: - production-grade architecture - multi-model strategy - advanced cloud design - prompt and model evaluation frameworks - failure handling - cross-functional tradeoffs - stakeholder alignment
Test Level 8
Covers: - enterprise standards - platform operating model - scaling across teams - advanced security and observability - architectural optimization - portfolio-level solution design
Test Level 9
Covers: - business transformation through AI - ecosystem strategy - large-scale platform and operating model choices - program governance - advanced technical failure and scaling scenarios
Test Level 10
Covers: - deep expertise across architecture, engineering, governance, economics, platform design, model operations, and enterprise execution - the candidate must demonstrate mastery, not just familiarity
________________________________________
Scoring Philosophy
Each question is mapped to: - track - level target - skill domain - difficulty score - discrimination weight
Each test should be unique, but still equivalent in difficulty.
Goal
No two tests are identical, but the scoring engine should still place the user at the same true level.
Simple MVP approach
Use a curated question bank with metadata: - track: architect or engineer - level: 1-10 - domain: business, functional, technical, platform, coding, cloud, models, governance - difficulty: 1-10 - question_type - correct_answer - weight
Then assemble each exam by blueprint.
Example for a Level 7 AI Engineer exam: - 3 business questions - 3 functional solution questions - 8 technical AI questions - 6 coding/integration questions - 4 cloud/platform questions - 4 governance/security questions - 3 scenario questions
This blueprint ensures equivalency.
________________________________________
Level Awarding Logic
Candidate attempts Test Level N
After score is calculated, assign the highest certified level they achieved.
Example thresholds for a Level 7 exam: - 85-100 = Level 7 Certification - 75-84 = Level 6 Certification - 65-74 = Level 5 Certification - below 65 = no certification from that attempt or assign the highest passed threshold depending on your policy
Recommended policy: - Level 1-6 can cascade downward - Level 7-10 should require stronger cutoffs - Show both: - attempted level - achieved level
Example message: > You attempted Test Level 7. > Your performance demonstrated Level 6 capability. > You have earned the AICERT AI Engineer Level 6 Certification.
________________________________________
Suggested Passing Thresholds
For MVP: - 90+ = target level certified - 82-89 = one level below - 74-81 = two levels below - 66-73 = three levels below - below 66 = no certification or lowest mapped pass depending on your policy
Cleaner version for launch: - use per-level calibration after pilot data is collected
________________________________________
Skill Domains
All questions should be tagged to one or more of these domains: - Business Acumen - Functional Process Thinking - AI Foundations - Models and Prompting - Data and RAG - Coding and APIs - Cloud and DevOps - Architecture and Integration - Security and Governance - Testing and Evaluation - Communication and Advisory
________________________________________
Candidate User Experience
Login Flow
•	Candidate creates account or signs in
•	Dashboard shows available certifications
•	Candidate selects track:
o	AI Solution Architect
o	AI Engineer
•	Candidate chooses test level to attempt
•	Candidate sees instructions and agreement
•	Candidate starts timed exam
Exam Page
•	clean focused interface
•	timer top right
•	progress bar
•	one question at a time or section view
•	next/back navigation
•	marked for review
•	auto-save answers
•	final submit confirmation
Result Page
Show: - candidate name - track attempted - level attempted - score percentage - achieved level - domain breakdown - pass/fall-short message - certificate button if certified
Candidate Dashboard History
•	past exams
•	past certifications
•	certificate download links
•	current highest achieved level by track
________________________________________
Certification Design
Certificate should look polished and professional.
Fields: - AICERT logo - DevReady branding - Candidate full name - Certification track - Certified level - Date awarded - Certificate ID - verification code or URL - signature line
Example title: AICERT Certification of Achievement
Example body: This certifies that [Candidate Name] has demonstrated competency at Level 7 in the AI Engineer track under the AICERT professional certification framework.
Add subtle visual elements: - dark border or modern frame - gold or silver accent by level - clean typography
________________________________________
Anti-Repetition Strategy
To ensure no two tests are alike but remain comparable:
MVP version
Create a question bank with at least: - 100 questions per level per track over time - blueprint-based exam assembly - random selection within constraints - randomized answer ordering
Smarter later version
Train a difficulty model using candidate results: - question success rates - question discrimination - domain balance - calibration by cohort performance
That can come after launch.
For now, the simple reliable solution is: 1. strong question tagging 2. blueprint-controlled assembly 3. weighted scoring 4. version tracking per test instance
________________________________________
Recommended Tech Stack
Keep simple and aligned with Railway + GitHub + VS Code.
Frontend
•	HTML
•	CSS
•	JavaScript
or, if following VETCODE structure: - React - Vite - simple CSS
Backend
•	Python
•	FastAPI
Database
•	SQLite for local MVP
•	PostgreSQL on Railway for deployed version
Auth
Simple email/password auth for MVP. Later add magic link or Google auth.
Certificate Generation
•	Python PDF generation
•	store certificate record in database
•	allow download from dashboard
________________________________________
Recommended Project Structure
AICERT/
  backend/
    app/
      main.py
      models.py
      database.py
      auth.py
      scoring.py
      exam_engine.py
      certificate.py
      seed_questions.py
      routers/
        auth.py
        exams.py
        results.py
        certificates.py
        admin.py
    requirements.txt
    Procfile or railway config
  frontend/
    src/
      pages/
        Login.jsx
        Dashboard.jsx
        TestIntro.jsx
        TestPage.jsx
        ResultPage.jsx
        CertificatePage.jsx
      components/
        Timer.jsx
        ProgressBar.jsx
        QuestionCard.jsx
        Navbar.jsx
      services/
        api.js
      App.jsx
      main.jsx
    package.json
  README.md
________________________________________
Core Database Tables
users
•	id
•	full_name
•	email
•	password_hash
•	created_at
certification_tracks
•	id
•	name
question_bank
•	id
•	track
•	level
•	domain
•	difficulty
•	question_type
•	prompt
•	choices_json
•	correct_answer_json
•	weight
•	explanation
•	active
exams
•	id
•	user_id
•	track
•	attempted_level
•	started_at
•	submitted_at
•	duration_minutes
•	status
•	generated_blueprint_json
exam_answers
•	id
•	exam_id
•	question_id
•	answer_json
•	is_correct
•	score_awarded
exam_results
•	id
•	exam_id
•	raw_score
•	percent_score
•	achieved_level
•	passed
•	domain_breakdown_json
certificates
•	id
•	user_id
•	track
•	certified_level
•	certificate_code
•	issued_at
•	pdf_path
________________________________________
Admin Features
Needed for your side later: - add/edit questions - activate/deactivate questions - preview exam blueprint by level - review candidate results - see weak domains by user - regenerate certificate
________________________________________
10 Initial Tests to Define
For now, each should be named simply: - Test Level 1 - Test Level 2 - Test Level 3 - Test Level 4 - Test Level 5 - Test Level 6 - Test Level 7 - Test Level 8 - Test Level 9 - Test Level 10
These exist separately for each track. So effectively: - AI Solution Architect: Levels 1-10 - AI Engineer: Levels 1-10
That means 20 exam blueprints total, even if the UI only shows 10 levels inside each track.
________________________________________
Sample Blueprint for Each Test
Test Level 1
•	10 basic technical questions
•	5 simple business/use case questions
•	5 AI basics questions
•	5 cloud/platform basics
•	6 simple scenario items
Test Level 2
•	slightly more independent implementation thinking
•	basic model/API decisions
•	beginner governance awareness
Test Level 3
•	practical coding and integration reasoning
•	prompt quality and evaluation basics
•	data handling and workflow logic
Test Level 4
•	architecture blocks
•	troubleshooting
•	business-to-technical translation
•	platform tradeoffs
Test Level 5
•	real delivery scenarios
•	production readiness
•	secure integration
•	system design and decision tradeoffs
Test Level 6
•	enterprise solutioning
•	scalable engineering
•	cloud and deployment detail
•	governance and architecture rigor
Test Level 7
•	advanced production architecture
•	orchestration, reliability, evaluation
•	executive and technical judgment combined
Test Level 8
•	standardization across teams
•	platform operating model
•	performance, observability, cost control
Test Level 9
•	transformation-level program decisions
•	enterprise portfolio AI strategy
•	deep failure and ambiguity scenarios
Test Level 10
•	full-spectrum mastery
•	advanced strategy + execution + platform depth
•	no weak areas tolerated
________________________________________
How to Keep It Simple for Build 1
Do not overbuild adaptive testing yet.
Build 1 should include only:
•	login
•	dashboard
•	track selection
•	level selection
•	60-minute timed exam
•	exam question rendering
•	submit
•	scoring
•	result page
•	certificate creation
•	certificate history
Build 2 later can add:
•	proctoring
•	webcam checks
•	AI-generated unique questions
•	psychometrics and calibration
•	employer-facing verification portal
•	admin analytics dashboards
•	retake rules
•	badge system
________________________________________
Recommended MVP Rules
•	one active exam at a time per user
•	timer starts once exam begins
•	auto-submit at 60 minutes
•	no answer changes after submit
•	certificate issued immediately after pass
•	store full result history
•	show highest achieved level prominently
________________________________________
Visual Direction
Match DevReady feel: - dark theme - clean modern layout - bright accent color - simple cards - professional typography - strong dashboard feel - minimal clutter
Pages should feel like: - login portal - professional certification system - tech talent verification platform
________________________________________
Recommended First Build Sequence
Phase 1
•	create project shell
•	set up backend and frontend
•	create auth
•	create dashboard
Phase 2
•	build question model and seed data
•	build exam engine
•	build timed test page
Phase 3
•	scoring engine
•	level awarding logic
•	result page
•	certificate PDF
Phase 4
•	styling polish to DevReady look
•	Railway deploy
•	GitHub repo under dcjoncas
________________________________________
Suggested Launch Positioning
AICERT can be presented as:
AICERT by DevReady
Professional AI capability certification for real-world engineers and solution architects.
Core message: - not trivia - not theory only - real-world mixed business, functional, and technical evaluation - level-based progression - employer-friendly capability signal
________________________________________
Best Next Build Output
The best next step is to generate: 1. full repo scaffold 2. database models 3. seed data structure 4. frontend pages 5. scoring engine 6. certificate generator
That will give you a working MVP base that can then be connected to Railway and GitHub.
