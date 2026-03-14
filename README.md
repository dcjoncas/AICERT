
# AICERT V3

AICERT V3 adds:
- DevReady green visual styling
- separate candidate and admin experiences
- 20 randomized multiple-choice questions
- forward-only MCQ flow
- essay response section (30%)
- scenario response section (30%)
- MCQ weighted at 40%
- AI grading for essay and scenario when `OPENAI_API_KEY` is set
- fallback grading when the key is missing
- live admin monitoring
- saved JSON result files in `backend/results`
- certificate generation

## Important security note
Do **not** paste your real OpenAI API key into source files or chat. Set it as an environment variable locally and in Railway.

## Local run
```powershell
cd backend
python -m venv venv310
.env310\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
$env:AICERT_ADMIN_EMAILS="your-admin-email@example.com"
$env:OPENAI_API_KEY="your-key-here"
python run.py
```

## URLs
- Candidate app: `http://127.0.0.1:8000/`
- Admin app: `http://127.0.0.1:8000/admin`
- API docs: `http://127.0.0.1:8000/docs`

## If schema changed from an older version
Because this uses SQLite without migrations yet, delete the old DB once:
```powershell
Remove-Item .icert.db -Force
```
