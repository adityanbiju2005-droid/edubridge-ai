// ============================================================
//  EduBridge AI — Frontend Logic
//  Fetch API, pipeline animation, tabs, copy/download
// ============================================================

// ── API Base URL ─────────────────────────────────────────────
// In development  → points to local FastAPI server
// In production   → points to your Render backend URL
// Update PROD_API_URL below after deploying to Render
const PROD_API_URL = 'https://edubridge-ai.onrender.com';
const API_BASE = (window.location.hostname === '127.0.0.1' || window.location.hostname === 'localhost')
  ? 'http://127.0.0.1:8000'
  : PROD_API_URL;

// ── DOM References ──────────────────────────────────────────
const form            = document.getElementById('input-form');
const sourceInput     = document.getElementById('source-material');
const langSelect      = document.getElementById('target-language');
const regionSelect    = document.getElementById('target-region');
const generateBtn     = document.getElementById('generate-btn');
const charCount       = document.getElementById('char-count');
const statusMsg       = document.getElementById('status-msg');
const progressBar     = document.getElementById('progress-bar');
const resultsSection  = document.getElementById('results-section');
const timingBadge     = document.getElementById('timing-badge');
const toastContainer  = document.getElementById('toast-container');

// Pipeline stage elements
const stages = [
  document.getElementById('stage-router'),
  document.getElementById('stage-structurer'),
  document.getElementById('stage-localizer'),
  document.getElementById('stage-quiz'),
];

// Result content areas
const resultPanels = {
  structured: document.getElementById('result-structured'),
  localized:  document.getElementById('result-localized'),
  rubric:     document.getElementById('result-rubric'),
};

// ── State ───────────────────────────────────────────────────
let isProcessing = false;

// ── Init: Load language & region options ────────────────────
async function loadOptions() {
  try {
    const [langRes, regionRes] = await Promise.all([
      fetch(`${API_BASE}/api/languages`),
      fetch(`${API_BASE}/api/regions`),
    ]);

    if (langRes.ok) {
      const languages = await langRes.json();
      languages.forEach(lang => {
        const opt = document.createElement('option');
        opt.value = lang.value;
        opt.textContent = lang.label;
        langSelect.appendChild(opt);
      });
    }

    if (regionRes.ok) {
      const regions = await regionRes.json();
      regions.forEach(region => {
        const opt = document.createElement('option');
        opt.value = region.value;
        opt.textContent = region.label;
        regionSelect.appendChild(opt);
      });
    }
  } catch (err) {
    console.warn('Could not reach backend for options. Ensure the server is running.', err);
  }
}

// ── Character Count ──────────────────────────────────────────
sourceInput.addEventListener('input', () => {
  const len = sourceInput.value.length;
  charCount.textContent = `${len.toLocaleString()} characters`;
});

// ── Pipeline Animation Helpers ───────────────────────────────
const STAGE_MESSAGES = [
  '🔍 Supervisor Router is validating your input…',
  '📚 Pedagogical Structurer is extracting core concepts…',
  '🌍 Localization Agent is adapting cultural context…',
  '📝 Quiz Generator is creating assessments & rubrics…',
];

const STAGE_DELAYS = [1200, 8000, 8000, 8000]; // approx pacing (ms)

let stageTimeouts = [];

function resetPipeline() {
  stages.forEach(s => { s.classList.remove('active', 'completed'); });
  stageTimeouts.forEach(t => clearTimeout(t));
  stageTimeouts = [];
  setProgress(0);
  setStatus('', '');
}

function setProgress(pct) {
  progressBar.style.width = `${pct}%`;
}

function setStatus(msg, type = '') {
  statusMsg.textContent = msg;
  statusMsg.className = `status-msg ${type}`;
}

function activateStage(index) {
  stages.forEach((s, i) => {
    s.classList.remove('active');
    if (i < index) s.classList.add('completed');
  });
  if (index < stages.length) {
    stages[index].classList.add('active');
  }
  setProgress(Math.round((index / stages.length) * 90));
  setStatus(STAGE_MESSAGES[index] || '', 'active');
}

function animatePipeline() {
  // Immediately activate stage 0
  activateStage(0);

  // Then pace through each subsequent stage using delays
  let cumulativeDelay = 0;
  for (let i = 1; i < stages.length; i++) {
    cumulativeDelay += STAGE_DELAYS[i - 1];
    const idx = i;
    stageTimeouts.push(
      setTimeout(() => activateStage(idx), cumulativeDelay)
    );
  }
}

function completePipeline(elapsedSec) {
  stageTimeouts.forEach(t => clearTimeout(t));
  stages.forEach(s => { s.classList.remove('active'); s.classList.add('completed'); });
  setProgress(100);
  setStatus(`✅ Pipeline complete in ${elapsedSec}s`, 'success');
}

// ── Submit Handler ───────────────────────────────────────────
form.addEventListener('submit', async (e) => {
  e.preventDefault();
  if (isProcessing) return;

  const sourceMaterial = sourceInput.value.trim();
  const targetLanguage = langSelect.value;
  const targetRegion   = regionSelect.value;

  if (!sourceMaterial) {
    showToast('Please paste some source material first.', 'error', '⚠️');
    return;
  }
  if (!targetLanguage) {
    showToast('Please select a target language.', 'error', '⚠️');
    return;
  }
  if (!targetRegion) {
    showToast('Please select a target region.', 'error', '⚠️');
    return;
  }

  // Start processing
  isProcessing = true;
  generateBtn.disabled = true;
  generateBtn.innerHTML = '<span class="btn-icon">⏳</span> Processing…';
  resultsSection.classList.remove('visible');
  resetPipeline();

  animatePipeline();

  try {
    const res = await fetch(`${API_BASE}/api/process`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        source_material: sourceMaterial,
        target_language: targetLanguage,
        target_region:   targetRegion,
      }),
    });

    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData.detail || `Server error ${res.status}`);
    }

    const data = await res.json();

    completePipeline(data.processing_time_seconds);
    displayResults(data);
    showToast('Content generated successfully!', 'success', '🎉');

  } catch (err) {
    stageTimeouts.forEach(t => clearTimeout(t));
    setStatus(`❌ Error: ${err.message}`, 'error');
    showToast(err.message, 'error', '❌');
    console.error(err);
  } finally {
    isProcessing = false;
    generateBtn.disabled = false;
    generateBtn.innerHTML = '<span class="btn-icon">✨</span> Generate Content';
  }
});

// ── Display Results ──────────────────────────────────────────
function displayResults(data) {
  resultPanels.structured.textContent = data.structured_lessons  || '(No output)';
  resultPanels.localized.textContent  = data.localized_content   || '(No output)';
  resultPanels.rubric.textContent     = data.evaluation_rubric   || '(No output)';

  if (timingBadge) {
    timingBadge.textContent = `⏱ ${data.processing_time_seconds}s`;
  }

  // Show results section
  resultsSection.classList.add('visible');

  // Activate first tab
  switchTab('structured');

  // Scroll to results
  setTimeout(() => {
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }, 300);
}

// ── Tab Switching ────────────────────────────────────────────
function switchTab(tabId) {
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.tab === tabId);
  });
  document.querySelectorAll('.tab-panel').forEach(panel => {
    panel.classList.toggle('active', panel.id === `panel-${tabId}`);
  });
}

document.querySelectorAll('.tab-btn').forEach(btn => {
  btn.addEventListener('click', () => switchTab(btn.dataset.tab));
});

// ── Copy & Download ──────────────────────────────────────────
function getActiveContent() {
  const activePanel = document.querySelector('.tab-panel.active');
  if (!activePanel) return '';
  return activePanel.querySelector('.result-content')?.textContent || '';
}

function getActiveTabName() {
  const activeBtn = document.querySelector('.tab-btn.active');
  return activeBtn?.textContent.trim() || 'output';
}

document.getElementById('btn-copy')?.addEventListener('click', async () => {
  const text = getActiveContent();
  if (!text) return;
  try {
    await navigator.clipboard.writeText(text);
    showToast('Copied to clipboard!', 'success', '📋');
  } catch {
    showToast('Copy failed. Please select text manually.', 'error', '⚠️');
  }
});

document.getElementById('btn-download')?.addEventListener('click', () => {
  const text = getActiveContent();
  if (!text) return;
  const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
  const url  = URL.createObjectURL(blob);
  const a    = document.createElement('a');
  a.href     = url;
  a.download = `EduBridge_${getActiveTabName().replace(/\s+/g, '_')}.txt`;
  a.click();
  URL.revokeObjectURL(url);
  showToast('File downloaded!', 'success', '⬇️');
});

// ── Toast System ─────────────────────────────────────────────
function showToast(message, type = 'success', emoji = '✅') {
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `<span style="font-size:1.1rem">${emoji}</span> ${message}`;
  toastContainer.appendChild(toast);
  setTimeout(() => {
    toast.style.transition = 'opacity 0.4s ease';
    toast.style.opacity    = '0';
    setTimeout(() => toast.remove(), 400);
  }, 3500);
}

// ── Boot ─────────────────────────────────────────────────────
loadOptions();
