/* SkillBridge dashboard - talks only to the Flask API; all scoring is done in PostgreSQL. */
"use strict";

const $ = (sel) => document.querySelector(sel);
const fmt = (v, d = 2) => (v === null || v === undefined ? "–" : Number(v).toFixed(d));
const pct = (v) => (v === null || v === undefined ? "–" : Math.round(Number(v) * 100));
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const TYPE_LABEL = { skill: "Skill", knowledge: "Knowledge", technology: "Tool", work_activity: "Activity" };
const LAYER_COLORS = ["#e2bdb4", "#d6c0a3", "#c9968c", "#b9a493", "#a77d70", "#c4a27a", "#8e6a5e", "#6b4f4b"];
const inkFor = (hex) => { const n = parseInt(hex.slice(1), 16), r = n >> 16, g = (n >> 8) & 255, b = n & 255;
  return (0.299 * r + 0.587 * g + 0.114 * b) > 150 ? "#3b2c27" : "#fffbf6"; };
const DOMAIN_ORDER = ["Data & AI", "Software engineering", "Mechanical & manufacturing engineering", "Business & finance analytics"];

const state = { careers: [], domain: null, careerId: null, me: null, gap: null, typeFilter: "all", charts: {} };

async function api(path, opts = {}) {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...opts,
    body: opts.body ? JSON.stringify(opts.body) : undefined,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || res.statusText);
  return data;
}

function toast(msg) {
  const t = $("#toast");
  t.textContent = msg;
  t.classList.add("show");
  clearTimeout(t._h);
  t._h = setTimeout(() => t.classList.remove("show"), 2200);
}

function debounce(fn, ms) {
  let h;
  return (...a) => { clearTimeout(h); h = setTimeout(() => fn(...a), ms); };
}

/* ------------------------------------------------------------------ header */
async function loadOverview() {
  const s = await api("/api/overview");
  const items = [
    [s.rated_careers, "rated careers"],
    [s.skills, "skills"],
    [s.evidence, "evidence rows"],
    [s.transfer_edges, "transfer edges"],
    [s.prerequisites, "prerequisites"],
  ];
  $("#stats").innerHTML = items
    .map(([v, l]) => `<div class="stat-chip"><b>${Number(v).toLocaleString()}</b><span>${l}</span></div>`)
    .join("");
  $("#lambdaFoot").textContent = fmt(s.lambda, 2);
}

/* ------------------------------------------------------------------ profile */
async function loadMe() {
  state.me = await api("/api/me");
  const m = state.me;
  $("#profileName").textContent = m.full_name;
  $("#avatar").textContent = m.full_name.split(" ").map((w) => w[0]).join("").slice(0, 2);
  $("#hours").value = m.weekly_hours;
  $("#hoursLabel").textContent = `${Number(m.weekly_hours)} h`;
  renderMySkills();
}

function renderMySkills() {
  const box = $("#mySkills");
  const skills = state.me.skills;
  if (!skills.length) {
    box.innerHTML = `<div class="muted small" style="padding:16px 0">No skills yet. Search above to add what you already know.</div>`;
    return;
  }
  box.innerHTML = skills.map((s) => `
    <div class="my-skill" data-id="${s.skill_id}">
      <div class="my-skill-top">
        <span class="chip t-${s.skill_type}">${TYPE_LABEL[s.skill_type] || s.skill_type}</span>
        <span class="name" title="${esc(s.name)}">${esc(s.name)}</span>
        <span class="val">${pct(s.proficiency)}%</span>
        <button class="x" title="Remove">×</button>
      </div>
      <input type="range" min="0" max="100" step="5" value="${pct(s.proficiency)}">
    </div>`).join("");

  box.querySelectorAll(".my-skill").forEach((row) => {
    const id = Number(row.dataset.id);
    const range = row.querySelector("input");
    const val = row.querySelector(".val");
    range.addEventListener("input", () => { val.textContent = `${range.value}%`; });
    range.addEventListener("change", async () => {
      await api("/api/me/skills", { method: "PUT", body: { skill_id: id, proficiency: range.value / 100 } });
      const s = state.me.skills.find((x) => x.skill_id === id);
      if (s) s.proficiency = range.value / 100;
      toast("Proficiency saved · history recorded by trigger");
      refreshAnalysis();
    });
    row.querySelector(".x").addEventListener("click", async () => {
      await api(`/api/me/skills/${id}`, { method: "DELETE" });
      state.me.skills = state.me.skills.filter((x) => x.skill_id !== id);
      renderMySkills();
      toast("Skill removed");
      refreshAnalysis();
    });
  });
}

function setupSkillSearch() {
  const input = $("#skillSearch");
  const dd = $("#skillResults");
  const search = debounce(async () => {
    const q = input.value.trim();
    if (q.length < 2) { dd.classList.remove("open"); return; }
    const rows = await api(`/api/skills/search?q=${encodeURIComponent(q)}`);
    const owned = new Set(state.me.skills.map((s) => s.skill_id));
    dd.innerHTML = rows.length
      ? rows.map((r) => `
          <div class="opt" data-id="${r.skill_id}">
            <span>${esc(r.name)}${owned.has(r.skill_id) ? ' <span class="muted small">· added</span>' : ""}</span>
            <span>${r.is_hot_technology ? '<span class="chip hot">Hot</span> ' : ""}<span class="chip t-${r.skill_type}">${TYPE_LABEL[r.skill_type]}</span></span>
          </div>`).join("")
      : `<div class="none">No matching skill</div>`;
    dd.classList.add("open");
    dd.querySelectorAll(".opt").forEach((o) => o.addEventListener("click", async () => {
      await api("/api/me/skills", { method: "PUT", body: { skill_id: Number(o.dataset.id), proficiency: 0.5 } });
      input.value = "";
      dd.classList.remove("open");
      await loadMe();
      toast("Skill added at 50% - adjust the slider");
      refreshAnalysis();
    }));
  }, 200);
  input.addEventListener("input", search);
  document.addEventListener("click", (e) => { if (!e.target.closest(".search-wrap")) document.querySelectorAll(".dropdown").forEach((d) => d.classList.remove("open")); });
}

/* ------------------------------------------------------------------ careers */
async function loadCareers() {
  state.careers = await api("/api/careers");
  const domains = DOMAIN_ORDER.filter((d) => state.careers.some((c) => c.domain === d));
  state.domain = state.domain || domains[0];
  $("#domainTabs").innerHTML = domains
    .map((d) => `<button class="tab ${d === state.domain ? "on" : ""}" data-d="${esc(d)}">${esc(d)}</button>`)
    .join("");
  $("#domainTabs").querySelectorAll(".tab").forEach((b) => b.addEventListener("click", () => {
    state.domain = b.dataset.d;
    loadCareers();
  }));
  const list = state.careers.filter((c) => c.domain === state.domain);
  $("#careerPills").innerHTML = list
    .map((c) => `<button class="pill ${c.career_id === state.careerId ? "on" : ""}" data-id="${c.career_id}">${esc(c.title)}</button>`)
    .join("");
  $("#careerPills").querySelectorAll(".pill").forEach((p) => p.addEventListener("click", () => selectCareer(Number(p.dataset.id))));

  const sel = $("#compareSelect");
  if (!sel.options.length) {
    sel.innerHTML = `<option value="">Compare with…</option>` + DOMAIN_ORDER.map((d) =>
      `<optgroup label="${esc(d)}">` + state.careers.filter((c) => c.domain === d)
        .map((c) => `<option value="${c.career_id}">${esc(c.title)}</option>`).join("") + `</optgroup>`).join("");
    sel.addEventListener("change", loadCompare);
  }
  if (!state.careerId && list.length) {
    const pref = list.find((c) => c.title === "Data Scientists") || list[0];
    selectCareer(pref.career_id);
  }
}

function setupCareerSearch() {
  const input = $("#careerSearch");
  const dd = $("#careerResults");
  input.addEventListener("input", debounce(async () => {
    const q = input.value.trim();
    if (q.length < 2) { dd.classList.remove("open"); return; }
    const rows = await api(`/api/careers/search?q=${encodeURIComponent(q)}`);
    dd.innerHTML = rows.length
      ? rows.map((r) => `<div class="opt" data-id="${r.career_id}"><span>${esc(r.title)}</span><span class="muted small">${esc(r.domain || "")}</span></div>`).join("")
      : `<div class="none">No rated career found</div>`;
    dd.classList.add("open");
    dd.querySelectorAll(".opt").forEach((o) => o.addEventListener("click", () => {
      input.value = "";
      dd.classList.remove("open");
      selectCareer(Number(o.dataset.id));
    }));
  }, 200));
}

async function selectCareer(id) {
  state.careerId = id;
  document.querySelectorAll(".pill").forEach((p) => p.classList.toggle("on", Number(p.dataset.id) === id));
  $("#roadmap").innerHTML = `<div class="empty">Generate a prerequisite-valid plan that fits your weekly hours.</div>`;
  $("#roadmapSummary").innerHTML = "";
  $("#nlpResult").hidden = true;
  nlp.cands = [];
  await refreshAnalysis();
}

/* ------------------------------------------------------------------ analysis */
const refreshAnalysis = debounce(async () => {
  if (!state.careerId) return;
  $("#gapList").innerHTML = `<div class="skeleton"></div><div class="skeleton"></div><div class="skeleton"></div>`;
  const g = await api(`/api/gap/${state.careerId}`);
  state.gap = g;
  renderHero(g);
  $("#nlpCareer").textContent = g.career.title;
  loadPostingEvidence();
  renderRadar(g);
  renderGapList();
  loadRank();
  loadCompare();
}, 120);

function ring(el, value, colorA, colorB, id) {
  const r = 42, c = 2 * Math.PI * r, v = Math.max(0, Math.min(1, Number(value) || 0));
  el.innerHTML = `
    <div class="ring-wrap">
      <svg viewBox="0 0 100 100">
        <defs><linearGradient id="${id}" x1="0" x2="1" y1="0" y2="1"><stop offset="0" stop-color="${colorA}"/><stop offset="1" stop-color="${colorB}"/></linearGradient></defs>
        <circle class="track" cx="50" cy="50" r="${r}" fill="none" stroke-width="9"/>
        <circle class="bar" cx="50" cy="50" r="${r}" fill="none" stroke="url(#${id})" stroke-width="9" stroke-linecap="round"
                stroke-dasharray="${c}" stroke-dashoffset="${c}"/>
      </svg>
      <div class="ring-val">${pct(v)}%</div>
    </div>`;
  requestAnimationFrame(() => requestAnimationFrame(() => {
    el.querySelector(".bar").style.strokeDashoffset = c * (1 - v);
  }));
}

function renderHero(g) {
  $("#careerTitle").textContent = g.career.title;
  $("#careerDomain").textContent = `${g.career.domain || "Career"} · ${g.career.origin_code}`;
  $("#careerDesc").textContent = g.career.description || "";
  ring($("#ringBase"), g.readiness.baseline, "#d6c4b1", "#a39282", "gBase");
  ring($("#ringTransfer"), g.readiness.transfer, "#d8a89f", "#7a5a50", "gTr");
  const lift = (Number(g.readiness.transfer) - Number(g.readiness.baseline)) * 100;
  $("#lift").textContent = `+${lift.toFixed(1)}`;
  $("#liftNote").textContent = `${g.summary.transfer_used} gaps reduced by related skills`;
  $("#reqCount").textContent = g.summary.requirements;
  const bt = g.summary.by_type;
  $("#reqNote").textContent = `${bt.skill || 0} skills · ${bt.knowledge || 0} knowledge · ${bt.technology || 0} tools · from ${g.summary.sources.join(", ")}`;
}

function chartDefaults() {
  Chart.defaults.color = "#8b7b70";
  Chart.defaults.font.family = "Inter, system-ui, sans-serif";
  Chart.defaults.borderColor = "rgba(122,90,80,0.12)";
}

function renderRadar(g) {
  const top = [...g.gaps].sort((a, b) => b.importance - a.importance || b.gap - a.gap).slice(0, 10);
  const labels = top.map((r) => (r.skill.length > 22 ? r.skill.slice(0, 21) + "…" : r.skill));
  const data = {
    labels,
    datasets: [
      { label: "Required importance", data: top.map((r) => r.importance), borderColor: "rgba(176,98,91,0.85)",
        backgroundColor: "rgba(176,98,91,0.05)", borderWidth: 2, pointRadius: 2, borderDash: [5, 4] },
      { label: "You (with transfer)", data: top.map((r) => r.effective_proficiency), borderColor: "#7a5a50",
        backgroundColor: "rgba(201,150,140,0.30)", borderWidth: 2, pointRadius: 3, pointBackgroundColor: "#7a5a50" },
      { label: "You (exact skills only)", data: top.map((r) => r.own_proficiency), borderColor: "rgba(200,173,141,0.95)",
        backgroundColor: "rgba(200,173,141,0.14)", borderWidth: 1.5, pointRadius: 2 },
    ],
  };
  const opts = {
    responsive: true, maintainAspectRatio: false, animation: { duration: 700 },
    scales: { r: { min: 0, max: 1, ticks: { display: false, stepSize: 0.25 },
      grid: { color: "rgba(122,90,80,0.12)" }, angleLines: { color: "rgba(122,90,80,0.12)" },
      pointLabels: { font: { size: 10.5 }, color: "#5e4540" } } },
    plugins: { legend: { position: "bottom", labels: { boxWidth: 10, boxHeight: 10, usePointStyle: true, font: { size: 11 } } },
      tooltip: { callbacks: { title: (it) => top[it[0].dataIndex].skill, label: (it) => `${it.dataset.label}: ${fmt(it.raw)}` } } },
  };
  if (state.charts.radar) { state.charts.radar.data = data; state.charts.radar.update(); }
  else state.charts.radar = new Chart($("#radar"), { type: "radar", data, options: opts });
}

function renderGapList() {
  const g = state.gap;
  const rows = g.gaps.filter((r) => state.typeFilter === "all" || r.skill_type === state.typeFilter).slice(0, 40);
  const max = Math.max(...g.gaps.map((r) => r.gap_baseline), 0.01);
  $("#gapList").innerHTML = rows.length ? rows.map((r) => {
    const sub = r.transfer_used
      ? `↳ <b>+${fmt(r.transfer_credit)}</b> transfer credit from ${esc(r.transfer_from)}`
      : r.own_proficiency > 0 ? `You: ${pct(r.own_proficiency)}% · needed importance ${fmt(r.importance)}`
      : `Not in your profile · importance ${fmt(r.importance)}`;
    return `
      <div class="gap-row" data-id="${r.skill_id}">
        <div class="gap-name">
          <div class="n"><span class="chip t-${r.skill_type}">${TYPE_LABEL[r.skill_type]}</span><span title="${esc(r.skill)}">${esc(r.skill)}</span></div>
          <div class="sub">${sub}</div>
        </div>
        <div class="bars"><div class="b0" style="width:${(r.gap_baseline / max) * 100}%"></div><div class="b1" style="width:${(r.gap / max) * 100}%"></div></div>
        <div class="gap-val">${fmt(r.gap)}</div>
      </div>`;
  }).join("") : `<div class="empty">No gaps of this type - you meet these requirements.</div>`;
  $("#gapList").querySelectorAll(".gap-row").forEach((el) => el.addEventListener("click", () => openExplain(Number(el.dataset.id))));
}

function setupTypeFilter() {
  $("#typeFilter").querySelectorAll("button").forEach((b) => b.addEventListener("click", () => {
    $("#typeFilter").querySelectorAll("button").forEach((x) => x.classList.remove("on"));
    b.classList.add("on");
    state.typeFilter = b.dataset.t;
    renderGapList();
  }));
}

/* ------------------------------------------------------------------ explanation drawer */
async function openExplain(skillId) {
  const d = await api(`/api/explain/${state.careerId}/${skillId}`);
  const g = d.gap, s = d.skill;
  const ev = d.evidence.map((e) => `
    <tr>
      <td><b>${esc(e.source)}</b><div class="muted small">${esc(e.requirement_type)}</div></td>
      <td class="mono">${e.importance_raw !== null ? `IM ${fmt(e.importance_raw)} → ` : ""}${fmt(e.importance)}</td>
      <td class="mono">${e.level_norm !== null ? fmt(e.level_norm) : "–"}</td>
      <td class="mono">${fmt(e.confidence)}</td>
    </tr>
    <tr><td colspan="4" class="muted small" style="border-bottom:1px solid rgba(255,255,255,.14)">${esc(e.source_record)}</td></tr>`).join("");
  const tc = d.transfer_candidates.length
    ? d.transfer_candidates.map((t) => `<div class="tc-row"><span>${esc(t.name)} <span class="muted">(you ${pct(t.proficiency)}% × T ${fmt(t.weight)} × λ)</span></span><span class="mono">+${fmt(t.credit)}</span></div>`).join("")
    : `<div class="muted small">None of your current skills has a transfer edge into this skill.</div>`;
  const pre = d.prerequisites.length
    ? d.prerequisites.map((p) => `<div class="tc-row"><span>${esc(p.name)}</span><span class="mono">your level ${pct(p.your_level)}%</span></div>`).join("")
    : `<div class="muted small">No curated prerequisites for this skill.</div>`;
  const transferLine = g.transfer_from
    ? `<span class="k">T(${esc(g.transfer_from)} → ${esc(s.name)})</span> = <span class="hl">${fmt(g.transfer_weight, 4)}</span><br>
       <span class="k">credit = λ × p(${esc(g.transfer_from)}) × T</span> = <span class="hl">${fmt(g.transfer_credit, 4)}</span><br>`
    : `<span class="k">transfer credit</span> = 0 (no related skill in your profile)<br>`;

  $("#drawerBody").innerHTML = `
    <div class="eyebrow">Why this gap? · ${esc(state.gap.career.title)}</div>
    <h2>${esc(s.name)}</h2>
    <div>${s.is_hot_technology ? '<span class="chip hot">Hot technology</span> ' : ""}<span class="chip t-${s.skill_type}">${TYPE_LABEL[s.skill_type]}</span></div>
    <p class="desc">${esc(s.description || "")}</p>

    <div class="compare-pair">
      <div><span class="muted small">Gap without transfer</span><b>${fmt(d.gap_baseline, 3)}</b></div>
      <div class="hl-box"><span class="muted small">Gap with transfer</span><b>${fmt(g.gap, 3)}</b></div>
    </div>

    <div class="q"><div class="q-title"><span class="num">1</span>Which sources require it?</div>
      <table class="ev"><thead><tr><th>Source</th><th>Importance</th><th>Level</th><th>Confidence</th></tr></thead><tbody>${ev}</tbody></table>
    </div>

    <div class="q"><div class="q-title"><span class="num">2</span>How the gap is calculated</div>
      <div class="calc">
        <span class="k">I (aggregated importance)</span> = <span class="hl">${fmt(g.importance, 4)}</span> <span class="k">from ${(g.sources || []).join(", ")}</span><br>
        <span class="k">P_own (your level)</span> = <span class="hl">${fmt(g.own_proficiency, 2)}</span><br>
        ${transferLine}
        <hr>
        <span class="k">P_eff = max(P_own, credit)</span> = <span class="hl">${fmt(g.effective_proficiency, 4)}</span><br>
        <span class="k">Gap = I × (1 − P_eff)</span> = ${fmt(g.importance, 4)} × ${fmt(1 - g.effective_proficiency, 4)} = <span class="res">${fmt(g.gap, 4)}</span>
      </div>
    </div>

    <div class="q"><div class="q-title"><span class="num">3</span>Which of your skills transfer here?</div>${tc}</div>
    <div class="q"><div class="q-title"><span class="num">4</span>Learn these first (prerequisites)</div>${pre}</div>
    <p class="muted small" style="margin-top:24px">Computed by <span class="mono">core.fn_gap_analysis()</span> in PostgreSQL · λ = ${fmt(d.lambda)}</p>`;
  $("#drawer").classList.add("open");
  $("#scrim").classList.add("open");
}

function closeDrawer() { $("#drawer").classList.remove("open"); $("#scrim").classList.remove("open"); }

/* ------------------------------------------------------------------ roadmap */
async function buildRoadmap() {
  const btn = $("#buildRoadmap");
  btn.disabled = true;
  btn.textContent = "Building…";
  try {
    const d = await api(`/api/roadmap/${state.careerId}`, {
      method: "POST", body: { weekly_hours: Number($("#hours").value), use_transfer: $("#useTransfer").checked },
    });
    renderRoadmap(d);
  } catch (e) {
    toast(`Roadmap failed: ${e.message}`);
  } finally {
    btn.disabled = false;
    btn.textContent = "Generate roadmap";
  }
}

function renderRoadmap(d) {
  const r = d.roadmap, items = d.items;
  const layers = Math.max(0, ...items.map((i) => i.layer));
  $("#roadmapSummary").innerHTML = `
    <div class="rm-chip"><b>${items.length}</b>learning steps</div>
    <div class="rm-chip"><b>${fmt(r.total_hours, 0)}</b>hours total</div>
    <div class="rm-chip"><b>${r.total_weeks}</b>weeks at ${Number(r.weekly_hours)} h/week</div>
    <div class="rm-chip"><b>${layers}</b>prerequisite layers</div>
    <div class="rm-chip ${r.violations === 0 ? "ok" : ""}"><b>${r.violations === 0 ? "✓" : r.violations}</b>${r.violations === 0 ? "prerequisites valid" : "violations"}</div>`;
  if (!items.length) {
    $("#roadmap").innerHTML = `<div class="empty">No gaps above the threshold - you're ready for this career.</div>`;
    return;
  }
  const weeks = Math.max(1, r.total_weeks);
  const step = weeks <= 12 ? 1 : weeks <= 30 ? 2 : weeks <= 60 ? 4 : 8;
  let ruler = "";
  for (let w = 1; w <= weeks; w += step) ruler += `<span style="left:${((w - 0.5) / weeks) * 100}%">W${w}</span>`;
  const rows = items.map((it) => {
    const left = ((it.week_start - 1) / weeks) * 100;
    const width = Math.max(((it.week_end - it.week_start + 1) / weeks) * 100, 1.2);
    const color = LAYER_COLORS[(it.layer - 1) % LAYER_COLORS.length];
    const after = it.after && it.after.length ? `<div class="g-after">after ${esc(it.after.join(", "))}</div>` : "";
    return `
      <div class="g-row">
        <div class="g-label">
          <span class="layer">L${it.layer}</span>
          <div style="min-width:0"><div class="n" title="${esc(it.skill)}">${esc(it.skill)}</div>${after}</div>
        </div>
        <div class="g-track" style="background-size:${100 / weeks}% 100%">
          <div class="g-bar" style="left:${left}%;width:${width}%;background:${color};color:${inkFor(color)};animation-delay:${it.item_no * 40}ms"
               title="${esc(it.skill)} · weeks ${it.week_start}–${it.week_end} · ${fmt(it.hours, 1)} h">${fmt(it.hours, 0)}h</div>
        </div>
      </div>`;
  }).join("");
  $("#roadmap").innerHTML = `<div class="g-head"><div></div><div class="g-ruler">${ruler}</div></div>${rows}`;
  toast(`Roadmap #${r.roadmap_id} stored · gap snapshot saved`);
}

/* ------------------------------------------------------------------ rank + compare */
async function loadRank() {
  const rows = await api("/api/rank");
  const labels = rows.map((r) => r.title.length > 34 ? r.title.slice(0, 33) + "…" : r.title);
  const data = {
    labels,
    datasets: [
      { label: "Exact skills only", data: rows.map((r) => r.baseline), backgroundColor: "rgba(200,173,141,0.45)", borderRadius: 4, barPercentage: 0.9, categoryPercentage: 0.75 },
      { label: "With transfer credit", data: rows.map((r) => r.transfer),
        backgroundColor: rows.map((r) => r.career_id === state.careerId ? "#7a5a50" : "rgba(201,150,140,0.85)"), borderRadius: 4, barPercentage: 0.9, categoryPercentage: 0.75 },
    ],
  };
  const opts = {
    indexAxis: "y", responsive: true, maintainAspectRatio: false, animation: { duration: 600 },
    scales: { x: { min: 0, max: 1, ticks: { callback: (v) => `${v * 100}%` }, grid: { color: "rgba(122,90,80,0.10)" } },
      y: { ticks: { font: { size: 10.5 }, color: "#5e4540" }, grid: { display: false } } },
    plugins: { legend: { position: "bottom", labels: { boxWidth: 10, usePointStyle: true, font: { size: 11 } } },
      tooltip: { callbacks: { title: (it) => rows[it[0].dataIndex].title, label: (it) => `${it.dataset.label}: ${pct(it.raw)}%` } } },
    onClick: (_, els) => { if (els.length) selectCareer(rows[els[0].index].career_id); },
  };
  if (state.charts.rank) { state.charts.rank.data = data; state.charts.rank.update(); }
  else state.charts.rank = new Chart($("#rankChart"), { type: "bar", data, options: opts });
}

async function loadCompare() {
  const b = $("#compareSelect").value;
  const box = $("#compare");
  if (!state.careerId) return;
  if (!b) {
    box.innerHTML = `<div class="empty" style="grid-column:1/-1">Pick a second career to compare readiness and top gaps side by side.</div>`;
    return;
  }
  const rows = await api(`/api/compare?a=${state.careerId}&b=${b}`);
  box.innerHTML = rows.map((c, i) => `
    <div class="cmp">
      <div class="eyebrow">${esc(c.domain || "")}</div>
      <h4>${esc(c.title)}</h4>
      <div class="rbar"><i style="width:${pct(c.baseline)}%;background:#d6c4b1"></i></div>
      <div class="rlabel"><span>Exact skills</span><span class="mono">${pct(c.baseline)}%</span></div>
      <div class="rbar"><i style="width:${pct(c.transfer)}%;background:${i === 0 ? "var(--grad)" : "linear-gradient(90deg,#d6c0a3,#9a7849)"}"></i></div>
      <div class="rlabel"><span>With transfer</span><span class="mono">${pct(c.transfer)}%</span></div>
      <ul>${c.top_gaps.map((g) => `<li><span>${esc(g.skill)}</span><span>${fmt(g.gap)}</span></li>`).join("")}</ul>
    </div>`).join("");
}


/* ------------------------------------------------------------------ NLP: job description analyser */
const EXAMPLE_AD = `Data Scientist - Analytics & Insights
We are looking for a data scientist to turn data into decisions across the business.

What you will do:
- Clean and analyse large datasets using Python and SQL
- Build machine learning models with scikit-learn and PyTorch
- Present findings to stakeholders with Tableau dashboards
- Work with engineers on data pipelines in Apache Spark

What we look for:
- Strong mathematics and statistics, critical thinking and complex problem-solving
- Experience with pandas, NumPy and version control with Git
- Excellent communication; Excel is a plus`;

const nlp = { tokens: [], cands: [] };

function joinTokens(tokens, spans) {
  // spans: map start index -> {end, html-open, html-close}
  let html = "", prev = "";
  for (let i = 1; i <= tokens.length; i++) {
    const t = tokens[i - 1];
    if (t === "¶") { html += "<br>"; prev = "¶"; continue; }
    const noSpaceBefore = /^[,.;:!?)\]]$/.test(t) || prev === "(" || prev === "[" || prev === "/" || t === "/" || prev === "¶" || prev === "";
    const sp = spans[i];
    html += (noSpaceBefore ? "" : " ") + (sp ? sp.open : "");
    if (sp) {
      const inner = [];
      for (let j = i; j <= sp.end; j++) inner.push(esc(tokens[j - 1]));
      html += inner.join(" ").replace(/ ([,.;:!?)])/g, "$1") + sp.close;
      prev = tokens[sp.end - 1];
      i = sp.end;
    } else {
      html += esc(t);
      prev = t;
    }
  }
  return html;
}

function renderNlp() {
  const spans = {};
  nlp.cands.forEach((c) => {
    if (!c.span_start) return;
    const cls = `hl t-${c.skill_type || "skill"} ${c.method === "fuzzy" ? "fuzzy" : ""} ${c.status}`;
    spans[c.span_start] = {
      end: c.span_end,
      open: `<mark class="${cls}" title="${esc(c.skill)} · ${c.method} ${fmt(c.score)} · ${c.status}">`,
      close: "</mark>",
    };
  });
  $("#nlpText").innerHTML = joinTokens(nlp.tokens, spans);
  const n = (st) => nlp.cands.filter((c) => c.status === st).length;
  $("#nlpCounts").textContent = `· ${nlp.cands.length} found · ${n("pending")} pending · ${n("approved")} approved`;
  $("#candList").innerHTML = nlp.cands.length ? nlp.cands.map((c) => `
    <div class="cand ${c.status}" data-id="${c.candidate_id}">
      <div>
        <div class="top"><span class="span">“${esc(c.span_text)}”</span><span class="arrow">→</span>
          <span class="chip t-${c.skill_type}">${TYPE_LABEL[c.skill_type] || ""}</span><span>${esc(c.skill)}</span></div>
        <div class="meta">${c.method} match · score ${fmt(c.score)} · ${esc((c.taxonomy || "").replace("onet_", "O*NET ").replace("esco", "ESCO"))}</div>
      </div>
      <div class="acts">${c.status === "pending"
        ? `<button class="btn-ok" data-a="1">Approve</button><button class="btn-no" data-a="0">Reject</button>`
        : `<span class="status-tag ${c.status}">${c.status}</span>`}</div>
    </div>`).join("") : `<div class="empty">No known skills found in this text.</div>`;
  $("#candList").querySelectorAll(".cand button").forEach((b) => b.addEventListener("click", () =>
    reviewCandidate(Number(b.closest(".cand").dataset.id), b.dataset.a === "1")));
}

async function reviewCandidate(id, approve, quiet = false) {
  const d = await api(`/api/candidates/${id}/review`, { method: "POST", body: { approve } });
  const i = nlp.cands.findIndex((c) => c.candidate_id === id);
  if (i >= 0) nlp.cands[i] = d.candidate;
  if (!quiet) {
    renderNlp();
    toast(approve ? `“${d.candidate.skill}” added as Job-postings evidence (trigger)` : "Rejected");
    loadPostingEvidence();
    refreshAnalysis();
  }
}

async function extractSkills() {
  const text = $("#jobText").value.trim();
  if (!state.careerId) return toast("Select a target career first");
  if (text.length < 10) return toast("Paste a job description first");
  const btn = $("#extractBtn");
  btn.disabled = true; btn.textContent = "Extracting…";
  try {
    const d = await api("/api/extract", { method: "POST", body: { career_id: state.careerId, text, fuzzy: $("#useFuzzy").checked } });
    nlp.tokens = d.tokens; nlp.cands = d.candidates;
    $("#nlpResult").hidden = false;
    renderNlp();
    loadPostingEvidence();
    toast(`Posting #${d.batch_id}: ${d.candidates.length} skills found, waiting for review`);
  } catch (e) {
    toast(e.message);
  } finally {
    btn.disabled = false; btn.textContent = "Extract skills";
  }
}

async function approveAllExact() {
  const todo = nlp.cands.filter((c) => c.status === "pending" && c.method === "exact");
  if (!todo.length) return toast("No pending exact matches");
  for (const c of todo) await reviewCandidate(c.candidate_id, true, true);
  renderNlp();
  loadPostingEvidence();
  refreshAnalysis();
  toast(`${todo.length} skills approved · evidence updated by trigger`);
}

async function loadPostingEvidence() {
  if (!state.careerId) return;
  const d = await api(`/api/postings/${state.careerId}`);
  const box = $("#postingEvidence");
  if (!d.evidence.length) { box.innerHTML = ""; return; }
  box.innerHTML = `
    <div class="posting-ev">
      <div class="nlp-sub">Contribution 1 · where job postings agree or disagree with O*NET / ESCO
        <span class="muted">· ${d.stats.postings} posting(s), ${d.stats.approved} approved extraction(s)</span></div>
      <table><thead><tr><th>Skill</th><th>Sources</th><th>Aggregated importance</th><th>Disagreement</th></tr></thead><tbody>
      ${d.evidence.map((r) => `<tr>
        <td><span class="chip t-${r.skill_type}">${TYPE_LABEL[r.skill_type]}</span> ${esc(r.skill)}</td>
        <td>${(r.sources || []).map(esc).join(" + ")}</td>
        <td class="mono">${fmt(r.importance, 3)}</td>
        <td class="mono"><span class="disagree" style="width:${Math.round(r.disagreement * 60)}px"></span>${fmt(r.disagreement, 2)}</td>
      </tr>`).join("")}</tbody></table>
    </div>`;
}

/* ------------------------------------------------------------------ init */
async function init() {
  chartDefaults();
  setupSkillSearch();
  setupCareerSearch();
  setupTypeFilter();
  $("#buildRoadmap").addEventListener("click", buildRoadmap);
  $("#extractBtn").addEventListener("click", extractSkills);
  $("#approveAll").addEventListener("click", approveAllExact);
  $("#loadExample").addEventListener("click", () => { $("#jobText").value = EXAMPLE_AD; });
  $("#closeDrawer").addEventListener("click", closeDrawer);
  $("#scrim").addEventListener("click", closeDrawer);
  document.addEventListener("keydown", (e) => { if (e.key === "Escape") closeDrawer(); });
  $("#hours").addEventListener("input", (e) => { $("#hoursLabel").textContent = `${e.target.value} h`; });
  $("#hours").addEventListener("change", async (e) => {
    await api("/api/me", { method: "PUT", body: { weekly_hours: Number(e.target.value) } });
    toast("Weekly budget saved");
  });
  $("#resetBtn").addEventListener("click", async () => {
    state.me = await api("/api/me/reset", { method: "POST" });
    renderMySkills();
    toast("Demo profile restored");
    refreshAnalysis();
  });
  try {
    await Promise.all([loadOverview(), loadMe()]);
    await loadCareers();
  } catch (e) {
    toast(`Could not reach the database: ${e.message}`);
  }
}

init();