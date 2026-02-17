const healthBadge = document.getElementById("healthBadge");
const tabs = document.querySelectorAll(".tab");
const panels = document.querySelectorAll(".panel");

const analyzeForm = document.getElementById("analyzeForm");
const analyzeResult = document.getElementById("analyzeResult");

const ingestForm = document.getElementById("ingestForm");
const ingestResult = document.getElementById("ingestResult");

const refreshTemplatesBtn = document.getElementById("refreshTemplatesBtn");
const templatesList = document.getElementById("templatesList");
const templateDetail = document.getElementById("templateDetail");

const trendForm = document.getElementById("trendForm");
const trendTemplate = document.getElementById("trendTemplate");
const trendMetric = document.getElementById("trendMetric");
const trendResult = document.getElementById("trendResult");
const trendChartWrap = document.getElementById("trendChartWrap");

let templatesCache = [];

function pretty(obj) {
  return JSON.stringify(obj, null, 2);
}

function extractErrorMessage(payload) {
  if (typeof payload === "string") return payload;
  if (!payload || typeof payload !== "object") return "Errore API";
  if (typeof payload.detail === "string") return payload.detail;
  if (payload.detail && typeof payload.detail === "object") {
    if (typeof payload.detail.message === "string") return payload.detail.message;
    return pretty(payload.detail);
  }
  if (typeof payload.message === "string") return payload.message;
  return pretty(payload);
}

async function fetchJson(url, options = {}) {
  const response = await fetch(url, options);
  const contentType = response.headers.get("content-type") || "";
  const isJson = contentType.includes("application/json");
  const payload = isJson ? await response.json() : await response.text();
  if (!response.ok) {
    throw new Error(isJson ? extractErrorMessage(payload) : payload);
  }
  return payload;
}

function setActiveTab(tabName) {
  tabs.forEach((tab) => {
    tab.classList.toggle("is-active", tab.dataset.tab === tabName);
  });
  panels.forEach((panel) => {
    panel.classList.toggle("is-active", panel.id === `panel-${tabName}`);
  });
}

tabs.forEach((tab) => {
  tab.addEventListener("click", () => setActiveTab(tab.dataset.tab));
});

async function checkHealth() {
  try {
    const payload = await fetchJson("/health");
    healthBadge.textContent = `API: ${payload.status}`;
  } catch (err) {
    healthBadge.textContent = "API: offline";
    healthBadge.classList.add("warn");
  }
}

analyzeForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  analyzeResult.textContent = "Analisi in corso...";

  const file = document.getElementById("analyzeFile").files[0];
  if (!file) {
    analyzeResult.textContent = "Seleziona un file";
    return;
  }

  const formData = new FormData();
  formData.append("file", file);

  try {
    const payload = await fetchJson("/template/analyze", {
      method: "POST",
      body: formData,
    });
    analyzeResult.textContent = pretty(payload);
  } catch (err) {
    analyzeResult.textContent = `Errore analisi: ${err.message}`;
  }
});

ingestForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  ingestResult.textContent = "Ingestion in corso...";

  const file = document.getElementById("ingestFile").files[0];
  if (!file) {
    ingestResult.textContent = "Seleziona un file";
    return;
  }

  const templateName = document.getElementById("ingestTemplateName").value.trim();
  const templateId = document.getElementById("ingestTemplateId").value.trim();
  const force = document.getElementById("ingestForce").checked;

  const formData = new FormData();
  formData.append("file", file);
  if (templateName) formData.append("template_name", templateName);
  if (templateId) formData.append("template_id", templateId);
  formData.append("force", String(force));

  try {
    const payload = await fetchJson("/template/ingest", {
      method: "POST",
      body: formData,
    });
    ingestResult.textContent = pretty(payload);
    await loadTemplates();
  } catch (err) {
    ingestResult.textContent = `Errore ingestion: ${err.message}`;
  }
});

function renderTemplateList(templates) {
  templatesList.innerHTML = "";
  if (!templates.length) {
    templatesList.innerHTML = "<div class='meta'>Nessun template disponibile.</div>";
    return;
  }

  templates.forEach((tpl) => {
    const row = document.createElement("div");
    row.className = "list-item";

    const left = document.createElement("div");
    left.innerHTML = `<strong>${tpl.template_name} v${tpl.template_version}</strong><div class='meta'>ID ${tpl.template_id} · ${tpl.created_at}</div>`;

    const right = document.createElement("button");
    right.textContent = "Apri";
    right.addEventListener("click", () => showTemplateDetail(tpl.template_id));

    row.appendChild(left);
    row.appendChild(right);
    templatesList.appendChild(row);
  });
}

async function showTemplateDetail(templateId) {
  templateDetail.textContent = "Caricamento dettaglio template...";
  try {
    const payload = await fetchJson(`/template/${templateId}`);
    templateDetail.textContent = pretty(payload);
  } catch (err) {
    templateDetail.textContent = `Errore dettaglio: ${err.message}`;
  }
}

function fillTrendTemplateSelect(templates) {
  trendTemplate.innerHTML = "<option value=''>Seleziona template</option>";
  templates.forEach((tpl) => {
    const option = document.createElement("option");
    option.value = String(tpl.template_id);
    option.textContent = `${tpl.template_name} v${tpl.template_version} (ID ${tpl.template_id})`;
    trendTemplate.appendChild(option);
  });
}

async function loadTemplates() {
  const templates = await fetchJson("/templates");
  templatesCache = templates;
  renderTemplateList(templates);
  fillTrendTemplateSelect(templates);
}

refreshTemplatesBtn.addEventListener("click", async () => {
  try {
    await loadTemplates();
    templateDetail.textContent = "Templates aggiornati.";
  } catch (err) {
    templateDetail.textContent = `Errore refresh: ${err.message}`;
  }
});

trendTemplate.addEventListener("change", async () => {
  trendMetric.innerHTML = "<option value=''>Seleziona metrica</option>";
  trendResult.textContent = "";
  trendChartWrap.innerHTML = "";

  if (!trendTemplate.value) {
    return;
  }

  try {
    const payload = await fetchJson(`/template/${trendTemplate.value}/metrics`);
    payload.metrics.forEach((m) => {
      const opt = document.createElement("option");
      opt.value = m;
      opt.textContent = m;
      trendMetric.appendChild(opt);
    });
  } catch (err) {
    trendResult.textContent = `Errore metriche: ${err.message}`;
  }
});

function renderSimpleChart(rows) {
  if (!rows.length) {
    trendChartWrap.innerHTML = "Nessun punto disponibile";
    return;
  }

  const width = 860;
  const height = 180;
  const padding = 24;

  const values = rows.map((r) => Number(r.metric_value || 0));
  const min = Math.min(...values);
  const max = Math.max(...values);
  const span = max - min || 1;

  const points = rows
    .map((row, idx) => {
      const x = padding + (idx * (width - 2 * padding)) / Math.max(rows.length - 1, 1);
      const y = height - padding - ((Number(row.metric_value || 0) - min) / span) * (height - 2 * padding);
      return `${x},${y}`;
    })
    .join(" ");

  trendChartWrap.innerHTML = `
    <svg viewBox="0 0 ${width} ${height}" preserveAspectRatio="none">
      <polyline fill="none" stroke="#0f766e" stroke-width="3" points="${points}" />
      <line x1="${padding}" y1="${height - padding}" x2="${width - padding}" y2="${height - padding}" stroke="#c9d4e8" stroke-width="1" />
    </svg>
  `;
}

trendForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const templateId = trendTemplate.value;
  const metric = trendMetric.value;
  const sheetName = document.getElementById("trendSheet").value.trim();
  const start = document.getElementById("trendStart").value;
  const end = document.getElementById("trendEnd").value;

  if (!templateId || !metric) {
    trendResult.textContent = "Seleziona template e metrica.";
    return;
  }

  trendResult.textContent = "Calcolo trend in corso...";

  const query = new URLSearchParams({ metric });
  if (sheetName) query.set("sheet_name", sheetName);
  if (start) query.set("start_date", start);
  if (end) query.set("end_date", end);

  try {
    const rows = await fetchJson(`/template/${templateId}/trend?${query.toString()}`);
    renderSimpleChart(rows);
    trendResult.textContent = pretty(rows);
  } catch (err) {
    trendResult.textContent = `Errore trend: ${err.message}`;
  }
});

(async function boot() {
  await checkHealth();
  try {
    await loadTemplates();
  } catch (err) {
    templatesList.innerHTML = `<div class='warn'>Errore caricamento templates: ${err.message}</div>`;
  }
})();
