const apiBase = "";

let currentAdmin = null;

const adminMessage = document.getElementById("adminMessage");
const adminLoginBtn = document.getElementById("adminLoginBtn");
const adminPanel = document.getElementById("adminPanel");
const adminAuth = document.getElementById("adminAuth");
const adminAttemptCards = document.getElementById("adminAttemptCards");

function showAdminMessage(text, type = "error") {
  if (!adminMessage) return;
  adminMessage.textContent = text;
  adminMessage.classList.remove("hidden", "success", "error");
  adminMessage.classList.add(type);
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

function setAdminUser(user) {
  currentAdmin = user;
  localStorage.setItem("aicertAdminUser", JSON.stringify(user));
  adminAuth?.classList.add("hidden");
  adminPanel?.classList.remove("hidden");
}

function loadStoredAdmin() {
  const stored = localStorage.getItem("aicertAdminUser");
  if (!stored) return;
  try {
    const user = JSON.parse(stored);
    if (user?.id) {
      currentAdmin = user;
      adminAuth?.classList.add("hidden");
      adminPanel?.classList.remove("hidden");
      loadLiveAdmin();
    }
  } catch (_) {}
}

async function adminLogin() {
  const email = document.getElementById("adminEmail")?.value.trim();
  const password = document.getElementById("adminPassword")?.value;

  try {
    const data = await apiRequest("/api/login", {
      method: "POST",
      body: JSON.stringify({ email, password })
    });

    if (!data.user?.is_admin) {
      throw new Error("This account is not marked as admin. Add its email to AICERT_ADMIN_EMAILS and restart the app.");
    }

    setAdminUser(data.user);
    showAdminMessage("Admin login successful.", "success");
    await loadLiveAdmin();
  } catch (err) {
    showAdminMessage(err.message, "error");
  }
}

function renderQuestionKey(questions = []) {
  if (!questions.length) {
    return `<div class="subtle-note">No question key available.</div>`;
  }

  return `
    <div class="table-wrap">
      <table class="data-table">
        <thead>
          <tr>
            <th>#</th>
            <th>Code</th>
            <th>Section</th>
            <th>Question</th>
            <th>Correct</th>
          </tr>
        </thead>
        <tbody>
          ${questions.map((q, idx) => `
            <tr>
              <td>${idx + 1}</td>
              <td><strong>${q.question_code}</strong></td>
              <td>${q.section}</td>
              <td>${q.question_text}</td>
              <td><strong>${q.correct_option}</strong></td>
            </tr>
          `).join("")}
        </tbody>
      </table>
    </div>
  `;
}

async function requestRetake(attemptId) {
  if (!currentAdmin?.id) return;
  try {
    await apiRequest(`/api/admin/retake/${attemptId}?user_id=${currentAdmin.id}`, {
      method: "POST"
    });
    showAdminMessage(`Retake requested for attempt ${attemptId}.`, "success");
    await loadLiveAdmin();
  } catch (err) {
    showAdminMessage(err.message, "error");
  }
}

async function loadLiveAdmin() {
  if (!currentAdmin?.id) return;

  try {
    const data = await apiRequest(`/api/admin/live?user_id=${currentAdmin.id}`);
    adminAttemptCards.innerHTML = "";

    const attempts = data.attempts || [];

    if (!attempts.length) {
      adminAttemptCards.innerHTML = `<div class="attempt-item">No live or historical attempts yet.</div>`;
      return;
    }

    attempts.forEach(a => {
      const progressPercent = a.total_questions
        ? Math.round(((a.current_index || 0) / a.total_questions) * 100)
        : 0;

      const card = document.createElement("div");
      card.className = "attempt-item";
      card.innerHTML = `
        <div style="display:flex; justify-content:space-between; gap:16px; flex-wrap:wrap;">
          <div>
            <div><strong>${a.exam_name || "Untitled Exam"}</strong></div>
            <div>${a.candidate_name || ""} · ${a.candidate_email || ""}</div>
            <div>${a.track} · Level ${a.attempted_level}</div>
            <div>Status: ${a.status}</div>
            <div>Progress: ${a.current_index || 0} / ${a.total_questions || 0} (${progressPercent}%)</div>
            <div>Score: ${a.percent_score ?? 0}%</div>
          </div>
          <div style="display:flex; gap:10px; align-items:flex-start; flex-wrap:wrap;">
            <button class="btn btn-secondary retake-btn" data-attempt="${a.attempt_id}">Retake</button>
          </div>
        </div>
        <div class="section-banner" style="margin-top:14px;">
          <strong>Assigned Question Key</strong>
          <span>Correct answers for this candidate's test instance.</span>
        </div>
        ${renderQuestionKey(a.questions || [])}
      `;

      adminAttemptCards.appendChild(card);
    });

    document.querySelectorAll(".retake-btn").forEach(btn => {
      btn.addEventListener("click", () => {
        requestRetake(btn.getAttribute("data-attempt"));
      });
    });
  } catch (err) {
    showAdminMessage(err.message, "error");
  }
}

window.clearAICERTAdminState = () => {
  localStorage.removeItem("aicertAdminUser");
  sessionStorage.clear();
  location.reload();
};

window.loadLiveAdmin = loadLiveAdmin;

adminLoginBtn?.addEventListener("click", adminLogin);

window.addEventListener("load", () => {
  loadStoredAdmin();
});