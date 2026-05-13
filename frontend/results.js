const apiBase = "";
const params = new URLSearchParams(window.location.search);
const attemptId = params.get("attempt_id");

const scoreFinal = document.getElementById("scoreFinal");
const scoreMcq = document.getElementById("scoreMcq");
const scoreBusiness = document.getElementById("scoreBusiness");
const scoreFunctional = document.getElementById("scoreFunctional");
const scoreTechnical = document.getElementById("scoreTechnical");
const scoreAchieved = document.getElementById("scoreAchieved");
const scoreStatus = document.getElementById("scoreStatus");
const scoreQuestions = document.getElementById("scoreQuestions");
const scoreMessage = document.getElementById("scoreMessage");
const resultsTitle = document.getElementById("resultsTitle");
const resultsSubtitle = document.getElementById("resultsSubtitle");
const reviewTableWrap = document.getElementById("reviewTableWrap");
const badgeCard = document.getElementById("badgeCard");
const badgeImage = document.getElementById("badgeImage");
const certificateLink = document.getElementById("certificateLink");
const retakeBtn = document.getElementById("retakeBtn");

function getCurrentUser() {
  try {
    return JSON.parse(localStorage.getItem("aicertUser") || "{}");
  } catch {
    return null;
  }
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

function renderReviewTable(questions) {
  reviewTableWrap.innerHTML = questions?.length
    ? `<table class="data-table"><thead><tr><th>#</th><th>Section</th><th>Question</th><th>You Chose</th><th>Correct</th><th>Status</th></tr></thead><tbody>${questions
        .map(
          (question) =>
            `<tr><td>${question.index}</td><td>${question.section}</td><td>${question.question_text}</td><td><strong>${question.selected_option || "-"}</strong></td><td><strong>${question.correct_option || "-"}</strong></td><td><strong>${question.is_correct ? "Correct" : "Incorrect"}</strong></td></tr>`,
        )
        .join("")}</tbody></table>`
    : '<div class="result-message">No question review available.</div>';
}

async function loadReview() {
  const user = getCurrentUser();
  if (!user?.id || !attemptId) return;
  const review = await apiRequest(`/api/attempt-review/${attemptId}?user_id=${user.id}`);
  resultsTitle.textContent = review.exam_name || "AICERT Results";
  resultsSubtitle.textContent = `${review.track} - Attempted Level ${review.attempted_level}`;
  scoreFinal.textContent = `${review.percent_score}%`;
  scoreMcq.textContent = `${review.mcq_percent}%`;
  scoreBusiness.textContent = `${review.business_score}%`;
  scoreFunctional.textContent = `${review.functional_score}%`;
  scoreTechnical.textContent = `${review.technical_score}%`;
  scoreAchieved.textContent = review.achieved_level > 0 ? `Level ${review.achieved_level}` : "No certification";
  scoreStatus.textContent = review.passed ? "Passed" : "Not Passed";
  scoreQuestions.textContent = String(review.total_questions || review.questions?.length || 0);
  scoreMessage.textContent = review.passed ? "Certification earned or downgraded to demonstrated level." : "No certification earned on this attempt.";
  renderReviewTable(review.questions);
  if (review.badge_url) {
    badgeCard.style.display = "";
    badgeImage.src = review.badge_url;
  }
  if (review.certificate_url) {
    certificateLink.href = review.certificate_url;
  } else {
    certificateLink.style.display = "none";
  }
  retakeBtn.onclick = async () => {
    const payload = await apiRequest("/api/retake", {
      method: "POST",
      body: JSON.stringify({ user_id: user.id, source_attempt_id: Number(attemptId) }),
    });
    if (payload?.attempt_id) window.location.href = "/";
  };
}

window.addEventListener("load", async () => {
  try {
    await loadReview();
  } catch (error) {
    document.body.innerHTML = `<div style="padding:30px;color:white;background:#07140d;font-family:Arial;">Failed to load review: ${error.message}</div>`;
  }
});
