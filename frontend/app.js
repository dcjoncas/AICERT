const apiBase = "";

let currentUser = null;
let currentAttemptId = null;
let currentQuestions = [];
let currentEssayPrompt = "";
let currentScenarioPrompt = "";
let timerSeconds = 3600;
let timerInterval = null;

const authCard = document.getElementById("authCard");
const dashboardSection = document.getElementById("dashboardSection");
const examSection = document.getElementById("examSection");
const resultSection = document.getElementById("resultSection");

const userBadge = document.getElementById("userBadge");
const messageBox = document.getElementById("messageBox");

const registerBtn = document.getElementById("registerBtn");
const loginBtn = document.getElementById("loginBtn");
const startExamBtn = document.getElementById("startExamBtn");
const submitExamBtn = document.getElementById("submitExamBtn");

const trackSelect = document.getElementById("trackSelect");
const levelSelect = document.getElementById("levelSelect");
const questionsContainer = document.getElementById("questionsContainer");
const examTitle = document.getElementById("examTitle");
const timerDisplay = document.getElementById("timerDisplay");

const essayPromptText = document.getElementById("essayPromptText");
const scenarioPromptText = document.getElementById("scenarioPromptText");
const essayResponse = document.getElementById("essayResponse");
const scenarioResponse = document.getElementById("scenarioResponse");

const resultTrack = document.getElementById("resultTrack");
const resultAttemptedLevel = document.getElementById("resultAttemptedLevel");
const resultScore = document.getElementById("resultScore");
const resultAchievedLevel = document.getElementById("resultAchievedLevel");
const resultMcq = document.getElementById("resultMcq");
const resultEssay = document.getElementById("resultEssay");
const resultScenario = document.getElementById("resultScenario");
const resultStatus = document.getElementById("resultStatus");
const resultMessage = document.getElementById("resultMessage");
const certificateLink = document.getElementById("certificateLink");
const myAttemptsSection = document.getElementById("myAttemptsSection");

function showMessage(text, type = "success") {
  if (!messageBox) return;
  messageBox.textContent = text;
  messageBox.classList.remove("hidden", "success", "error");
  messageBox.classList.add(type);
}

function clearMessage() {
  if (!messageBox) return;
  messageBox.textContent = "";
  messageBox.classList.add("hidden");
  messageBox.classList.remove("success", "error");
}

function formatTime(seconds) {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${String(mins).padStart(2, "0")}:${String(secs).padStart(2, "0")}`;
}

function updateTimerDisplay() {
  if (timerDisplay) timerDisplay.textContent = formatTime(timerSeconds);
}

function stopTimer() {
  if (timerInterval) {
    clearInterval(timerInterval);
    timerInterval = null;
  }
}

function startTimer() {
  stopTimer();
  timerSeconds = 3600;
  updateTimerDisplay();

  timerInterval = setInterval(() => {
    timerSeconds -= 1;
    updateTimerDisplay();

    if (timerSeconds <= 0) {
      stopTimer();
      submitExam();
    }
  }, 1000);
}

async function apiRequest(path, options = {}) {
  const response = await fetch(`${apiBase}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {})
    },
    ...options
  });

  const contentType = response.headers.get("content-type") || "";
  const data = contentType.includes("application/json")
    ? await response.json()
    : await response.text();

  if (!response.ok) {
    const msg = typeof data === "object" && data?.detail ? data.detail : "Request failed";
    throw new Error(msg);
  }
  return data;
}

function setCurrentUser(user) {
  currentUser = user;
  localStorage.setItem("aicertUser", JSON.stringify(user));

  if (userBadge) {
    userBadge.textContent = user.full_name;
    userBadge.classList.remove("hidden");
  }

  authCard?.classList.add("hidden");
  dashboardSection?.classList.remove("hidden");
  loadMyAttempts();
}

function loadStoredUser() {
  const stored = localStorage.getItem("aicertUser");
  if (!stored) return;
  try {
    const user = JSON.parse(stored);
    if (user?.id) {
      setCurrentUser(user);
    }
  } catch (_) {}
}

async function loadTracksAndLevels() {
  const [trackData, levelData] = await Promise.all([
    apiRequest("/api/tracks"),
    apiRequest("/api/levels")
  ]);

  trackSelect.innerHTML = "";
  levelSelect.innerHTML = "";

  trackData.tracks.forEach(track => {
    const option = document.createElement("option");
    option.value = track.id;
    option.textContent = track.name;
    trackSelect.appendChild(option);
  });

  levelData.levels.forEach(level => {
    const option = document.createElement("option");
    option.value = String(level.level);
    option.textContent = level.label;
    levelSelect.appendChild(option);
  });
}

async function loadMyAttempts() {
  if (!currentUser?.id || !myAttemptsSection) return;

  try {
    const data = await apiRequest(`/api/my-attempts?user_id=${currentUser.id}`);
    const attempts = data.attempts || [];

    if (!attempts.length) {
      myAttemptsSection.innerHTML = "";
      return;
    }

    myAttemptsSection.innerHTML = `
      <div class="card-header" style="margin-top:20px;">
        <h3>My Attempts</h3>
        <p>Recent exam activity.</p>
      </div>
      <div class="attempt-list">
        ${attempts.map(a => `
          <div class="attempt-item">
            <div><strong>${a.exam_name || "Untitled Exam"}</strong></div>
            <div>${a.track} · Level ${a.attempted_level}</div>
            <div>Status: ${a.status}</div>
            <div>Progress: ${a.current_index || 0} / ${a.total_questions || 0}</div>
            <div>Score: ${a.percent_score ?? 0}%</div>
          </div>
        `).join("")}
      </div>
    `;
  } catch (err) {
    console.error(err);
  }
}

async function registerUser() {
  clearMessage();
  const full_name = document.getElementById("registerName")?.value.trim();
  const email = document.getElementById("registerEmail")?.value.trim();
  const password = document.getElementById("registerPassword")?.value;

  if (!full_name || !email || !password) {
    showMessage("Please complete all register fields.", "error");
    return;
  }

  try {
    const data = await apiRequest("/api/register", {
      method: "POST",
      body: JSON.stringify({ full_name, email, password })
    });
    setCurrentUser(data.user);
    showMessage("Account created successfully.", "success");
  } catch (err) {
    showMessage(err.message, "error");
  }
}

async function loginUser() {
  clearMessage();
  const email = document.getElementById("loginEmail")?.value.trim();
  const password = document.getElementById("loginPassword")?.value;

  if (!email || !password) {
    showMessage("Please enter email and password.", "error");
    return;
  }

  try {
    const data = await apiRequest("/api/login", {
      method: "POST",
      body: JSON.stringify({ email, password })
    });
    setCurrentUser(data.user);
    showMessage("Login successful.", "success");
  } catch (err) {
    showMessage(err.message, "error");
  }
}

async function updateProgress(index) {
  if (!currentAttemptId || !currentUser?.id) return;
  try {
    await apiRequest(`/api/attempts/${currentAttemptId}/progress?current_index=${index}&user_id=${currentUser.id}`, {
      method: "POST"
    });
  } catch (err) {
    console.error("Progress update failed", err);
  }
}

function renderQuestions(questions) {
  if (!questionsContainer) return;
  questionsContainer.innerHTML = "";

  if (!questions.length) {
    questionsContainer.innerHTML = `<div class="question-card"><div class="question-text">No questions returned.</div></div>`;
    return;
  }

  questions.forEach((q, index) => {
    const card = document.createElement("div");
    card.className = "question-card";

    card.innerHTML = `
      <div class="question-number">Question ${index + 1} · ${q.section}</div>
      <div class="question-text">${q.question_text}</div>
      <div class="option-list">
        <label class="option-item">
          <input type="radio" name="question_${q.id}" value="A" />
          <span><strong>A.</strong> ${q.option_a}</span>
        </label>
        <label class="option-item">
          <input type="radio" name="question_${q.id}" value="B" />
          <span><strong>B.</strong> ${q.option_b}</span>
        </label>
        <label class="option-item">
          <input type="radio" name="question_${q.id}" value="C" />
          <span><strong>C.</strong> ${q.option_c}</span>
        </label>
        <label class="option-item">
          <input type="radio" name="question_${q.id}" value="D" />
          <span><strong>D.</strong> ${q.option_d}</span>
        </label>
      </div>
    `;

    card.querySelectorAll(`input[name="question_${q.id}"]`).forEach(input => {
      input.addEventListener("change", () => updateProgress(index + 1));
    });

    questionsContainer.appendChild(card);
  });
}

async function startExam() {
  clearMessage();

  if (!currentUser?.id) {
    showMessage("Please login first.", "error");
    return;
  }

  const track = trackSelect.value;
  const level = parseInt(levelSelect.value, 10);

  try {
    const data = await apiRequest("/api/start-exam", {
      method: "POST",
      body: JSON.stringify({
        user_id: Number(currentUser.id),
        track,
        level
      })
    });

    currentAttemptId = data.attempt_id;
    currentQuestions = data.questions || [];
    currentEssayPrompt = data.essay_prompt || "";
    currentScenarioPrompt = data.scenario_prompt || "";

    examTitle.textContent = data.exam_name || `${data.track} Test`;
    renderQuestions(currentQuestions);

    essayPromptText.textContent = currentEssayPrompt;
    scenarioPromptText.textContent = currentScenarioPrompt;
    essayResponse.value = "";
    scenarioResponse.value = "";

    examSection?.classList.remove("hidden");
    resultSection?.classList.add("hidden");

    startTimer();
    examSection?.scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (err) {
    showMessage(err.message, "error");
  }
}

function collectAnswers() {
  return currentQuestions
    .map(q => {
      const selected = document.querySelector(`input[name="question_${q.id}"]:checked`);
      return {
        question_id: q.id,
        selected_option: selected ? selected.value : ""
      };
    })
    .filter(a => a.selected_option !== "");
}

function scoreWrittenResponse(text) {
  const lengthScore = Math.min(100, Math.floor((text.trim().length / 1500) * 100));
  return Math.max(20, lengthScore);
}

async function submitExam() {
  clearMessage();

  if (!currentAttemptId) {
    showMessage("No active exam found.", "error");
    return;
  }

  const answers = collectAnswers();
  const essayText = essayResponse.value || "";
  const scenarioText = scenarioResponse.value || "";

  if (!answers.length) {
    showMessage("Please answer the multiple-choice section.", "error");
    return;
  }

  if (!essayText.trim()) {
    showMessage("Please complete the essay response.", "error");
    return;
  }

  if (!scenarioText.trim()) {
    showMessage("Please complete the scenario response.", "error");
    return;
  }

  const essayPercent = scoreWrittenResponse(essayText);
  const scenarioPercent = scoreWrittenResponse(scenarioText);

  try {
    const data = await apiRequest("/api/submit-exam", {
      method: "POST",
      body: JSON.stringify({
        attempt_id: Number(currentAttemptId),
        answers,
        essay_response: essayText,
        essay_feedback: "Initial local scoring applied. AI grading can be added next.",
        scenario_response: scenarioText,
        scenario_feedback: "Initial local scoring applied. AI grading can be added next.",
        essay_percent: essayPercent,
        scenario_percent: scenarioPercent
      })
    });

    stopTimer();

    resultTrack.textContent = data.track;
    resultAttemptedLevel.textContent = `Level ${data.attempted_level}`;
    resultScore.textContent = `${data.percent_score}%`;
    resultAchievedLevel.textContent = data.achieved_level > 0 ? `Level ${data.achieved_level}` : "No certification";
    resultMcq.textContent = `${data.mcq_percent}%`;
    resultEssay.textContent = `${data.essay_percent}%`;
    resultScenario.textContent = `${data.scenario_percent}%`;
    resultStatus.textContent = data.passed ? "Passed" : "Not Passed";
    resultMessage.textContent = data.message;

    if (data.certificate_url) {
      certificateLink.href = data.certificate_url;
      certificateLink.classList.remove("hidden");
    } else {
      certificateLink.classList.add("hidden");
    }

    resultSection?.classList.remove("hidden");
    loadMyAttempts();
    resultSection?.scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (err) {
    showMessage(err.message, "error");
  }
}

window.clearAICERTState = () => {
  localStorage.clear();
  sessionStorage.clear();
  location.reload();
};

registerBtn?.addEventListener("click", registerUser);
loginBtn?.addEventListener("click", loginUser);
startExamBtn?.addEventListener("click", startExam);
submitExamBtn?.addEventListener("click", submitExam);

window.addEventListener("load", async () => {
  try {
    await loadTracksAndLevels();
    loadStoredUser();
  } catch (err) {
    showMessage(`App failed to initialize: ${err.message}`, "error");
  }
});