const API_BASE = "http://127.0.0.1:8000/api/v1";

// Character Counter
const symptomsInput = document.getElementById("symptomsInput");
const charCount     = document.getElementById("charCount");
const minWarning    = document.getElementById("minWarning");

symptomsInput.addEventListener("input", () => {
  const len = symptomsInput.value.length;
  charCount.textContent = len;
  minWarning.classList.toggle("hidden", len === 0 || len >= 10);
});

// UI State Helpers 
function setLoading(isLoading) {
  const btn     = document.getElementById("analyzeBtn");
  const btnText = document.getElementById("btnText");
  const spinner = document.getElementById("btnSpinner");

  btn.disabled = isLoading;
  btnText.textContent = isLoading ? "Analyzing..." : "Analyze Symptoms";
  spinner.classList.toggle("hidden", !isLoading);

  document.getElementById("emptyState").classList.add("hidden");
  document.getElementById("loadingState").classList.toggle("hidden", !isLoading);
  document.getElementById("resultsContent").classList.add("hidden");
}

function showError(message) {
  const el = document.getElementById("errorMsg");
  el.textContent = message;
  el.classList.remove("hidden");
}

function clearError() {
  const el = document.getElementById("errorMsg");
  el.textContent = "";
  el.classList.add("hidden");
}

// Urgency Config
const URGENCY_CONFIG = {
  Emergency: { icon: "🚨", cls: "urgency-emergency" },
  High:      { icon: "⚠️",  cls: "urgency-high"      },
  Moderate:  { icon: "🔶", cls: "urgency-moderate"  },
  Low:       { icon: "✅", cls: "urgency-low"        },
};

// Render Results 
function renderResults(data) {
  // Urgency
  const urgency = URGENCY_CONFIG[data.urgency_level] || URGENCY_CONFIG["Moderate"];
  const banner  = document.getElementById("urgencyBanner");
  banner.className = `urgency-banner ${urgency.cls}`;
  document.getElementById("urgencyIcon").textContent  = urgency.icon;
  document.getElementById("urgencyLevel").textContent = data.urgency_level;

  // Conditions
  const condList = document.getElementById("conditionsList");
  condList.innerHTML = data.conditions.map(c => `
    <div class="condition-card">
      <div class="condition-header">
        <span class="condition-name">${escapeHtml(c.name)}</span>
        <span class="likelihood-badge likelihood-${c.likelihood.toLowerCase()}">
          ${escapeHtml(c.likelihood)}
        </span>
      </div>
      <p class="condition-desc">${escapeHtml(c.description)}</p>
    </div>
  `).join("");

  // Steps
  const stepsList = document.getElementById("stepsList");
  stepsList.innerHTML = data.recommended_steps
    .map(s => `<li>${escapeHtml(s)}</li>`)
    .join("");

  // Disclaimer
  document.getElementById("resultDisclaimer").textContent = `ℹ️ ${data.disclaimer}`;

  // Show results
  document.getElementById("loadingState").classList.add("hidden");
  document.getElementById("resultsContent").classList.remove("hidden");
}

// Main: Analyze Symptoms
async function analyzeSymptoms(event) {

  if (event) event.preventDefault();
  clearError();
  const symptoms = symptomsInput.value.trim();

  // Client-side validation
  if (symptoms.length < 10) {
    showError("Please describe your symptoms in at least 10 characters.");
    return;
  }

  if (symptoms.length > 2000) {
    showError("Please keep your description under 2000 characters.");
    return;
  }

  setLoading(true);

  try {
    const response = await fetch(`${API_BASE}/check-symptoms`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ symptoms }),
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new Error(err.detail || `Server error (${response.status}). Please try again.`);
    }

    const data = await response.json();
    renderResults(data);

  } catch (err) {
    document.getElementById("loadingState").classList.add("hidden");
    document.getElementById("emptyState").classList.remove("hidden");

    if (err.name === "TypeError") {
      showError("Cannot connect to the server. Make sure the backend is running on port 8000.");
    } else {
      showError(err.message);
    }
  } finally {
    const btn     = document.getElementById("analyzeBtn");
    const btnText = document.getElementById("btnText");
    const spinner = document.getElementById("btnSpinner");
    btn.disabled  = false;
    btnText.textContent = "Analyze Symptoms";
    spinner.classList.add("hidden");
  }
}

// History 
async function loadHistory() {
  const historyList = document.getElementById("historyList");
  historyList.innerHTML = `<p class="history-empty">Loading...</p>`;

  try {
    const response = await fetch(`${API_BASE}/history`);

    if (!response.ok) throw new Error("Failed to load history.");

    const data = await response.json();

    if (data.total === 0) {
      historyList.innerHTML = `<p class="history-empty">No past queries found.</p>`;
      return;
    }

    historyList.innerHTML = data.queries.map(q => `
      <div class="history-item" onclick="loadHistoryItem(${q.id})">
        <div class="history-item-symptoms">${escapeHtml(q.symptoms)}</div>
        <div class="history-item-meta">
          <span>🕐 ${formatDate(q.created_at)}</span>
          <span>Urgency: ${escapeHtml(q.urgency_level)}</span>
          <span>${q.conditions.length} conditions</span>
        </div>
      </div>
    `).join("");

    // Store history data globally for item lookup
    window._historyData = data.queries;

  } catch (err) {
    historyList.innerHTML = `<p class="history-empty" style="color:#dc2626">Failed to load history.</p>`;
  }
}

// Load a Past History Item into Results Panel
function loadHistoryItem(id) {
  const item = (window._historyData || []).find(q => q.id === id);
  if (!item) return;

  symptomsInput.value = item.symptoms;
  charCount.textContent = item.symptoms.length;

  document.getElementById("emptyState").classList.add("hidden");
  document.getElementById("loadingState").classList.add("hidden");
  renderResults(item);
}

// Utilities 
function escapeHtml(str) {
  const div = document.createElement("div");
  div.appendChild(document.createTextNode(String(str)));
  return div.innerHTML;
}

function formatDate(iso) {
  try {
    return new Date(iso).toLocaleString();
  } catch {
    return iso;
  }
}

// Allow Enter key on textarea (Ctrl+Enter to submit) 
symptomsInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && e.ctrlKey) analyzeSymptoms();
});