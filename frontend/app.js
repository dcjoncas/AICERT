const apiBase = "";
const launchParams = new URLSearchParams(window.location.search);
const launchContext = {
  profileId: launchParams.get("profileId") || "",
  candidate: launchParams.get("candidate") || "",
  email: launchParams.get("email") || "",
  source: launchParams.get("source") || "",
  returnTo: launchParams.get("returnTo") || "",
  badgeRole: launchParams.get("badgeRole") || "",
  badgeRoleKey: launchParams.get("badgeRoleKey") || "",
  badgeLevel: launchParams.get("badgeLevel") || "",
  badgeTitle: launchParams.get("badgeTitle") || "",
  examId: launchParams.get("examId") || "",
  examVersion: launchParams.get("examVersion") || "",
  certificateId: launchParams.get("certificateId") || "",
};

let currentUser = null;
let currentAttemptId = null;
let currentQuestions = [];
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
const certPathBadges = document.getElementById("certPathBadges");
const answerKeyWrap = document.getElementById("answerKeyWrap");

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

function formatTime(value) {
  const minutes = Math.floor(value / 60);
  const seconds = value % 60;
  return `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
}

function updateTimerDisplay() {
  if (timerDisplay) timerDisplay.textContent = formatTime(timerSeconds);
}

function renderCertificationPath(activeLevel = 1, achievedLevel = 0) {
  if (!certPathBadges) return;
  certPathBadges.innerHTML = "";
  for (let level = 1; level <= 10; level += 1) {
    const badge = document.createElement("div");
    badge.className = "cert-badge";
    if (level === Number(activeLevel)) badge.classList.add("active");
    if (achievedLevel && level <= Number(achievedLevel)) badge.classList.add("earned");
    badge.innerHTML = `<span>Level</span><strong>${level}</strong>`;
    certPathBadges.appendChild(badge);
  }
}

function stopTimer() {
  if (timerInterval) clearInterval(timerInterval);
  timerInterval = null;
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
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  const contentType = response.headers.get("content-type") || "";
  const payload = contentType.includes("application/json") ? await response.json() : await response.text();
  if (!response.ok) {
    const message = typeof payload === "object" && payload?.detail ? payload.detail : "Request failed";
    throw new Error(message);
  }
  return payload;
}

function prefillLaunchCandidate() {
  document.querySelectorAll(".written-section").forEach((section) => {
    section.style.display = "none";
  });
  resultEssay?.closest(".metric")?.remove();
  resultScenario?.closest(".metric")?.remove();

  if (launchContext.candidate) {
    const registerName = document.getElementById("registerName");
    if (registerName && !registerName.value) registerName.value = launchContext.candidate;
  }

  if (launchContext.email) {
    const registerEmail = document.getElementById("registerEmail");
    const loginEmail = document.getElementById("loginEmail");
    if (registerEmail && !registerEmail.value) registerEmail.value = launchContext.email;
    if (loginEmail && !loginEmail.value) loginEmail.value = launchContext.email;
  }

  if (launchContext.profileId || launchContext.candidate || launchContext.email) {
    showMessage("Connected from DevReady. Use this candidate account so the certification can return to the profile.", "success");
  }
}

function selectedBadgeContext() {
  const rawLevel = launchContext.badgeLevel || launchParams.get("level") || "";
  const levelNumber = Number(String(rawLevel).replace(/[^\d]/g, "")) || 1;
  const version = (
    launchContext.examVersion ||
    (launchContext.certificateId.match(/-v([a-c])$/i) || [])[1] ||
    "A"
  )
    .toString()
    .toUpperCase();
  const roleKey = launchContext.badgeRoleKey || "";
  const role = launchContext.badgeRole || launchParams.get("track") || "AI Engineer";
  const title = launchContext.badgeTitle || `${role} L${levelNumber}`;
  const backendTrack = roleKey.includes("architect") || roleKey.includes("solution") ? "AI Solution Architect" : "AI Engineer";
  return {
    role,
    roleKey,
    title,
    level: Math.max(1, Math.min(10, levelNumber)),
    version,
    examId: launchContext.examId,
    certificateId: launchContext.certificateId,
    backendTrack,
    hasSelection: Boolean(launchContext.badgeRole || launchContext.badgeLevel || launchContext.examId),
  };
}

function selectedExamLabel() {
  const badge = selectedBadgeContext();
  return badge.hasSelection ? `${badge.title} - Version ${badge.version}` : "";
}

function isDevReadyLaunch() {
  return Boolean(launchContext.source === "devready_invite" || launchContext.source === "devready" || launchContext.profileId || launchContext.examId);
}

function devReadyTargetOrigins() {
  const origins = new Set(["http://127.0.0.1:8000", "http://localhost:8000", "https://vetcode-production.up.railway.app"]);
  if (launchContext.returnTo) {
    try {
      origins.add(new URL(launchContext.returnTo).origin);
    } catch {
      // Keep fixed origins when returnTo is unavailable or malformed.
    }
  }
  return origins;
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
  if (isDevReadyLaunch()) return;
  const raw = localStorage.getItem("aicertUser");
  if (!raw) return;
  try {
    const user = JSON.parse(raw);
    if (user?.id) setCurrentUser(user);
  } catch {
    // ignore stale storage
  }
}

async function launchFromDevReady() {
  if (!isDevReadyLaunch()) return false;
  if (!launchContext.email) {
    authCard?.classList.remove("hidden");
    showMessage("This certification link is missing the candidate email. Ask DevReady to resend it.", "error");
    return true;
  }
  const badge = selectedBadgeContext();
  authCard?.classList.add("hidden");
  dashboardSection?.classList.remove("hidden");
  showMessage("DevReady certification link loaded. Preparing the assigned exam.", "success");
  const payload = await apiRequest("/api/devready-launch", {
    method: "POST",
    body: JSON.stringify({
      full_name: launchContext.candidate || launchContext.email.split("@")[0],
      email: launchContext.email,
      profile_id: launchContext.profileId,
      badge_role: badge.role,
      badge_role_key: badge.roleKey,
      badge_level: `L${badge.level}`,
      badge_title: badge.title,
      exam_id: badge.examId,
      exam_version: badge.version,
      certificate_id: badge.certificateId,
    }),
  });
  setCurrentUser(payload.user);
  trackSelect.value = badge.backendTrack;
  trackSelect.disabled = true;
  levelSelect.value = String(badge.level);
  levelSelect.disabled = true;
  if (startExamBtn) startExamBtn.textContent = `Start ${badge.title} (${badge.examId || "assigned exam"})`;
  renderCertificationPath(badge.level, 0);
  return true;
}

async function loadTracksAndLevels() {
  const [tracksPayload, levelsPayload] = await Promise.all([apiRequest("/api/tracks"), apiRequest("/api/levels")]);
  trackSelect.innerHTML = "";
  levelSelect.innerHTML = "";
  tracksPayload.tracks.forEach((track) => {
    const option = document.createElement("option");
    option.value = track.id;
    option.textContent = track.name;
    trackSelect.appendChild(option);
  });
  levelsPayload.levels.forEach((level) => {
    const option = document.createElement("option");
    option.value = String(level.level);
    option.textContent = level.label;
    levelSelect.appendChild(option);
  });
  const badge = selectedBadgeContext();
  if (badge.hasSelection) {
    trackSelect.value = badge.backendTrack;
    levelSelect.value = String(badge.level);
    const dashboardCopy = dashboardSection?.querySelector(".card-header p");
    if (dashboardCopy) dashboardCopy.textContent = `Assigned exam: ${badge.title} - Version ${badge.version}.`;
    if (startExamBtn) startExamBtn.textContent = `Start ${badge.title} (${badge.examId || "assigned exam"})`;
  }
  renderCertificationPath(Number(levelSelect.value || 1), 0);
}

async function loadMyAttempts() {
  if (!currentUser?.id || !myAttemptsSection) return;
  try {
    const payload = await apiRequest(`/api/my-attempts?user_id=${currentUser.id}`);
    const attempts = payload.attempts || [];
    if (!attempts.length) {
      myAttemptsSection.innerHTML = "";
      return;
    }
    myAttemptsSection.innerHTML = `<div class="card-header" style="margin-top:20px;"><h3>My Attempts</h3><p>Recent exam activity.</p></div><div class="attempt-list">${attempts
      .map(
        (attempt) => `<div class="attempt-item"><div><strong>${attempt.exam_name || "Untitled Exam"}</strong></div><div>${attempt.track} - Level ${attempt.attempted_level}</div><div>Status: ${attempt.status}</div><div>Progress: ${attempt.current_index || 0} / ${attempt.total_questions || 0}</div><div>Score: ${attempt.percent_score ?? 0}%</div></div>`,
      )
      .join("")}</div>`;
  } catch (error) {
    console.error(error);
  }
}

async function registerUser() {
  clearMessage();
  const fullName = document.getElementById("registerName")?.value.trim();
  const email = document.getElementById("registerEmail")?.value.trim();
  const password = document.getElementById("registerPassword")?.value;
  if (!fullName || !email || !password) {
    showMessage("Please complete all register fields.", "error");
    return;
  }
  try {
    const payload = await apiRequest("/api/register", {
      method: "POST",
      body: JSON.stringify({ full_name: fullName, email, password }),
    });
    setCurrentUser(payload.user);
    showMessage("Account created successfully.", "success");
  } catch (error) {
    showMessage(error.message, "error");
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
    const payload = await apiRequest("/api/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
    setCurrentUser(payload.user);
    showMessage("Login successful.", "success");
  } catch (error) {
    showMessage(error.message, "error");
  }
}

async function updateProgress(currentIndex) {
  if (!currentAttemptId || !currentUser?.id) return;
  try {
    await apiRequest(`/api/attempts/${currentAttemptId}/progress?current_index=${currentIndex}&user_id=${currentUser.id}`, {
      method: "POST",
    });
  } catch (error) {
    console.error("Progress update failed", error);
  }
}

function renderQuestions(questions) {
  if (!questionsContainer) return;
  questionsContainer.innerHTML = "";
  if (!questions.length) {
    questionsContainer.innerHTML = '<div class="question-card"><div class="question-text">No questions returned.</div></div>';
    return;
  }

  questions.forEach((question, index) => {
    const card = document.createElement("div");
    card.className = "question-card";
    card.innerHTML = `<div class="question-number">Question ${index + 1} - ${question.section}</div><div class="question-text">${question.question_text}</div><div class="option-list"><label class="option-item"><input type="radio" name="question_${question.id}" value="A" /><span><strong>A.</strong> ${question.option_a}</span></label><label class="option-item"><input type="radio" name="question_${question.id}" value="B" /><span><strong>B.</strong> ${question.option_b}</span></label><label class="option-item"><input type="radio" name="question_${question.id}" value="C" /><span><strong>C.</strong> ${question.option_c}</span></label><label class="option-item"><input type="radio" name="question_${question.id}" value="D" /><span><strong>D.</strong> ${question.option_d}</span></label></div>`;
    card.querySelectorAll(`input[name="question_${question.id}"]`).forEach((input) => {
      input.addEventListener("change", () => updateProgress(index + 1));
    });
    questionsContainer.appendChild(card);
  });
}

function renderAnswerKey(answerKey = []) {
  if (!answerKeyWrap) return;
  if (!answerKey.length) {
    answerKeyWrap.classList.add("hidden");
    answerKeyWrap.innerHTML = "";
    return;
  }

  answerKeyWrap.classList.remove("hidden");
  answerKeyWrap.innerHTML = `
    <div class="answer-key-header">
      <div>
        <div class="eyebrow">Answer key</div>
        <h3>This test attempt</h3>
      </div>
      <span>${answerKey.length} questions</span>
    </div>
    <div class="answer-key-grid">
      ${answerKey
        .map(
          (item) => `<div class="answer-key-item">
            <span>Q${item.index} - ${item.section}</span>
            <strong>${item.correct_option}. ${item.correct_text}</strong>
          </div>`,
        )
        .join("")}
    </div>
  `;
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
    const payload = await apiRequest("/api/start-exam", {
      method: "POST",
      body: JSON.stringify({ user_id: Number(currentUser.id), track, level }),
    });
    currentAttemptId = payload.attempt_id;
    currentQuestions = payload.questions || [];
    renderCertificationPath(level, 0);
    examTitle.textContent = selectedExamLabel() || payload.exam_name || `${payload.track} Test`;
    renderQuestions(currentQuestions);
    if (essayPromptText) essayPromptText.textContent = payload.essay_prompt || "";
    if (scenarioPromptText) scenarioPromptText.textContent = payload.scenario_prompt || "";
    if (essayResponse) essayResponse.value = "";
    if (scenarioResponse) scenarioResponse.value = "";
    document.querySelectorAll(".written-section").forEach((section) => {
      section.style.display = "none";
    });
    examSection?.classList.remove("hidden");
    resultSection?.classList.add("hidden");
    startTimer();
    examSection?.scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (error) {
    showMessage(error.message, "error");
  }
}

function collectAnswers() {
  return currentQuestions
    .map((question) => {
      const selected = document.querySelector(`input[name="question_${question.id}"]:checked`);
      return { question_id: question.id, selected_option: selected ? selected.value : "" };
    })
    .filter((answer) => answer.selected_option !== "");
}

function notifyDevReady(result) {
  const badge = selectedBadgeContext();
  const achievedLevel = result.achieved_level > 0 ? `L${result.achieved_level}` : `L${result.attempted_level || badge.level}`;
  const payload = {
    type: "ai-cert-complete",
    profileId: launchContext.profileId,
    candidate: launchContext.candidate || currentUser?.full_name || "",
    email: launchContext.email || currentUser?.email || "",
    status: result.passed ? "certified" : "failed",
    level: achievedLevel,
    score: result.percent_score ? `${result.percent_score}%` : "",
    certificateId: launchContext.certificateId || (result.certificate_url ? `AICERT-${String(result.attempt_id).padStart(6, "0")}` : ""),
    certificateUrl: result.certificate_url || "",
    attemptId: result.attempt_id,
    passed: result.passed,
    title: badge.title,
    examId: badge.examId,
    examVersion: badge.version,
    notes: `AICERT submitted. Attempt ${result.attempt_id}; ${result.raw_score}/${result.total_questions || currentQuestions.length} correct; achieved ${achievedLevel}.`,
  };

  if (window.parent && window.parent !== window) {
    for (const origin of devReadyTargetOrigins()) {
      window.parent.postMessage(payload, origin);
    }
  }

  if (launchContext.returnTo && window.parent === window) {
    const url = new URL(launchContext.returnTo);
    url.searchParams.set("certComplete", "1");
    url.searchParams.set("profileId", launchContext.profileId);
    url.searchParams.set("candidate", payload.candidate);
    url.searchParams.set("email", payload.email);
    url.searchParams.set("status", payload.status);
    url.searchParams.set("level", payload.level);
    url.searchParams.set("score", payload.score);
    url.searchParams.set("certificateId", payload.certificateId);
    url.searchParams.set("badgeTitle", payload.title);
    url.searchParams.set("examId", payload.examId);
    url.searchParams.set("examVersion", payload.examVersion);
    setTimeout(() => {
      window.location.href = url.toString();
    }, 900);
  }
}

async function submitExam() {
  clearMessage();
  if (!currentAttemptId) {
    showMessage("No active exam found.", "error");
    return;
  }

  const answers = collectAnswers();
  if (!answers.length) {
    showMessage("Please answer the multiple-choice section.", "error");
    return;
  }

  try {
    const result = await apiRequest("/api/submit-exam", {
      method: "POST",
      body: JSON.stringify({
        attempt_id: Number(currentAttemptId),
        answers,
        essay_response: "",
        scenario_response: "",
      }),
    });
    stopTimer();
    resultTrack.textContent = result.track;
    resultAttemptedLevel.textContent = `Level ${result.attempted_level}`;
    resultScore.textContent = `${result.percent_score}%`;
    resultAchievedLevel.textContent = result.achieved_level > 0 ? `Level ${result.achieved_level}` : "No certification";
    resultMcq.textContent = `${result.mcq_percent}%`;
    if (resultEssay) resultEssay.textContent = `${result.essay_percent}%`;
    if (resultScenario) resultScenario.textContent = `${result.scenario_percent}%`;
    resultStatus.textContent = result.passed ? "Passed" : "Not Passed";
    resultMessage.textContent = result.message;
    renderCertificationPath(result.attempted_level, result.achieved_level);
    renderAnswerKey(result.answer_key || []);
    if (result.certificate_url) {
      certificateLink.href = result.certificate_url;
      certificateLink.classList.remove("hidden");
    } else {
      certificateLink.classList.add("hidden");
    }
    resultSection?.classList.remove("hidden");
    loadMyAttempts();
    notifyDevReady(result);
    if (!isDevReadyLaunch()) {
      window.open(result.results_url || `/results?attempt_id=${result.attempt_id}`, "_blank");
    }
    resultSection?.scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (error) {
    showMessage(error.message, "error");
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
levelSelect?.addEventListener("change", () => renderCertificationPath(Number(levelSelect.value || 1), 0));
window.addEventListener("load", async () => {
  try {
    await loadTracksAndLevels();
    prefillLaunchCandidate();
    const launched = await launchFromDevReady();
    if (!launched) loadStoredUser();
  } catch (error) {
    showMessage(`App failed to initialize: ${error.message}`, "error");
  }
});
