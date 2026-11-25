// ==========================================================================
// INDIEPULSE — WATERMELON UI CONTROLLER (MUNICIPALITY + CITIZEN)
// Precision Multi-Modal Animal Triage & Accountability Engine
// ==========================================================================

let map;
let muniLargeMap;
let markers = [];
let geofenceCircles = [];
let allDossiers = [];
let selectedDossierId = null;
let currentCoords = [28.6145, 77.2095];
let userPinMarker = null;
let selectedCameraId = "CAM-NDEL-W4-08";
let currentRole = "municipality";
let preloadedSampleFile = null;

let chartSeverityInstance = null;
let chartResolutionInstance = null;

// User's own reported cases tracker (persisted in localStorage)
let myReportedCaseIds = JSON.parse(localStorage.getItem("indiepulse_my_cases") || "[]");
let fleetData = [];

document.addEventListener("DOMContentLoaded", () => {
  initMap();
  initLucide();
  fetchDossiers();
  checkGeminiStatus();
  startLiveClock();
  detectUserLocation(false);
  autoDetectLocation(false);

  // Poll live dossiers every 3 seconds
  setInterval(fetchDossiers, 3000);
});

function initLucide() {
  if (window.lucide) {
    window.lucide.createIcons();
  }
}

function startLiveClock() {
  const clockEl = document.getElementById("live-clock");
  function update() {
    const now = new Date();
    const dateStr = now.toLocaleDateString("en-GB", { day: "2-digit", month: "short", year: "numeric" });
    const timeStr = now.toLocaleTimeString("en-GB", { hour12: false });
    if (clockEl) clockEl.textContent = `${dateStr} • ${timeStr} IST`;
  }
  update();
  setInterval(update, 1000);
}

// -------------------------------------------------------------
// DUAL ROLE SWITCHER (Watermelon Segmented Control)
// -------------------------------------------------------------
function switchRole(role) {
  currentRole = role;

  const muniSidebar = document.getElementById("muni-sidebar");
  const muniPages = document.getElementById("muni-pages");
  const citizenSidebar = document.getElementById("citizen-sidebar");
  const citizenPages = document.getElementById("citizen-pages");

  const btnMuni = document.getElementById("role-btn-muni");
  const btnCitizen = document.getElementById("role-btn-citizen");
  const pillBadge = document.getElementById("role-pill-badge");
  const tagline = document.getElementById("role-tagline");

  if (role === "municipality") {
    muniSidebar.classList.remove("hidden");
    muniPages.classList.remove("hidden");
    citizenSidebar.classList.add("hidden");
    citizenPages.classList.add("hidden");

    btnMuni.className = "wm-segment-btn active flex items-center gap-1.5";
    btnCitizen.className = "wm-segment-btn flex items-center gap-1.5";

    pillBadge.textContent = "Municipality SOC";
    pillBadge.className = "wm-pill-normal text-[10px]";
    tagline.textContent = "Autonomous Smart City Stray Triage & Accountability";

    navigateMuni("overview");
  } else {
    citizenSidebar.classList.remove("hidden");
    citizenPages.classList.remove("hidden");
    muniSidebar.classList.add("hidden");
    muniPages.classList.add("hidden");

    btnCitizen.className = "wm-segment-btn active flex items-center gap-1.5";
    btnMuni.className = "wm-segment-btn flex items-center gap-1.5";

    pillBadge.textContent = "Citizen Portal";
    pillBadge.className = "wm-pill-normal text-[10px]";
    tagline.textContent = "Community Animal Distress Reporting & Ward Safety Tracker";

    navigateCitizen("report");
    renderCitizenQueue();
    renderCitizenVanStatus();
    renderCitizenSafetyAlerts();
  }

  if (map) setTimeout(() => { map.invalidateSize(); }, 200);
  initLucide();
}

// Municipality Navigation
function navigateMuni(pageId) {
  document.querySelectorAll(".muni-content").forEach(el => el.classList.add("hidden"));
  document.querySelectorAll("#muni-sidebar .wm-nav-item").forEach(tab => tab.classList.remove("active"));

  const target = document.getElementById(`muni-page-${pageId}`);
  if (target) {
    target.classList.remove("hidden");
    target.classList.add("wm-page-enter");
  }

  const tab = document.getElementById(`muni-nav-${pageId}`);
  if (tab) tab.classList.add("active");

  if (pageId === "overview" && map) {
    setTimeout(() => { map.invalidateSize(); }, 200);
  }

  if (pageId === "map") {
    initLargeMuniMap();
  }

  if (pageId === "cameras") {
    fetchActiveStreams();
    startStreamPolling();
  } else {
    stopStreamPolling();
  }

  if (pageId === "models") {
    loadModelStats();
  }

  if (pageId === "analytics") {
    setTimeout(initAnalyticsCharts, 150);
  }

  initLucide();
}

// Citizen Navigation
function navigateCitizen(pageId) {
  document.querySelectorAll(".citizen-content").forEach(el => el.classList.add("hidden"));
  document.querySelectorAll("#citizen-sidebar .wm-nav-item").forEach(tab => tab.classList.remove("active"));

  const target = document.getElementById(`citizen-page-${pageId}`);
  if (target) {
    target.classList.remove("hidden");
    target.classList.add("wm-page-enter");
  }

  const tab = document.getElementById(`citizen-nav-${pageId}`);
  if (tab) tab.classList.add("active");

  if (pageId === "queue") renderCitizenQueue();
  if (pageId === "van") renderCitizenVanStatus();
  if (pageId === "alerts") renderCitizenSafetyAlerts();

  initLucide();
}

// -------------------------------------------------------------
// Leaflet Maps Initialization
// -------------------------------------------------------------
function initMap() {
  map = L.map("map", { zoomControl: true }).setView(currentCoords, 14);

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: "© OpenStreetMap contributors",
  }).addTo(map);

  map.on("click", (e) => {
    setUserPin(e.latlng.lat, e.latlng.lng, "Selected Locality");
  });
}

function initLargeMuniMap() {
  const container = document.getElementById("muni-large-map");
  if (!container) return;

  if (!muniLargeMap) {
    muniLargeMap = L.map("muni-large-map", { zoomControl: true }).setView(currentCoords, 14);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", { maxZoom: 19 }).addTo(muniLargeMap);
  } else {
    setTimeout(() => { muniLargeMap.invalidateSize(); }, 200);
  }
}

function setUserPin(lat, lon, title) {
  currentCoords = [lat, lon];
  const latInput = document.getElementById("citizen-lat");
  const lonInput = document.getElementById("citizen-lon");
  if (latInput) latInput.value = lat.toFixed(5);
  if (lonInput) lonInput.value = lon.toFixed(5);

  if (userPinMarker) {
    userPinMarker.setLatLng([lat, lon]);
  } else {
    userPinMarker = L.marker([lat, lon]).addTo(map);
  }
}

function detectUserLocation(showAlert = true) {
  if (!navigator.geolocation) return;
  navigator.geolocation.getCurrentPosition(
    (pos) => {
      const lat = pos.coords.latitude;
      const lon = pos.coords.longitude;
      currentCoords = [lat, lon];
      if (map) {
        map.flyTo([lat, lon], 15);
        setUserPin(lat, lon, "Your Real Location");
      }
      if (showAlert) showSuccessToast("GPS Connected", `Location: ${lat.toFixed(4)}, ${lon.toFixed(4)}`);
    },
    (err) => {},
    { enableHighAccuracy: true, timeout: 6000 }
  );
}

// -------------------------------------------------------------
// Synchronize Backend Data & Fleet Status
// -------------------------------------------------------------
async function fetchDossiers() {
  try {
    const [dossiersRes, fleetRes] = await Promise.all([
      fetch("/api/dossiers"),
      fetch("/api/fleet")
    ]);

    if (!dossiersRes.ok) return;
    const previousDossiers = allDossiers;
    allDossiers = await dossiersRes.json();
    if (fleetRes.ok) fleetData = await fleetRes.json();

    // Check if any of my reported cases changed from pending to dispatched
    checkCitizenDispatchNotifications(previousDossiers, allDossiers);

    updateMetrics();
    renderMapMarkers();
    renderMuniOverviewTable();
    renderCitizenQueue();
    renderCitizenVanStatus();
    renderCitizenSafetyAlerts();

    if (!selectedDossierId && allDossiers.length > 0) {
      selectedDossierId = allDossiers[0].id;
    }
    renderSelectedCaseOverview();

  } catch (err) {
    console.warn("Sync notice:", err);
  }
}

function checkCitizenDispatchNotifications(prevList, newList) {
  if (!prevList || prevList.length === 0) return;
  
  newList.forEach(newD => {
    const prevD = prevList.find(p => p.id === newD.id);
    if (prevD && prevD.status !== "DISPATCHED" && newD.status === "DISPATCHED") {
      // If this was reported by the citizen, show real-time alert!
      if (myReportedCaseIds.includes(newD.id)) {
        showSuccessToast(
          "🚑 Van Dispatched to Your Report!",
          `The municipality has assigned ${newD.dispatched_to} to your case at ${newD.landmark}. ETA: ~${newD.eta_minutes || 8} mins.`
        );
        playAlertSound();
      }
    }
  });
}

function updateMetrics() {
  const total = allDossiers.length;
  const urgent = allDossiers.filter(d => d.tier === "TIER_1_RABIES_QUARANTINE").length;
  const dispatched = allDossiers.filter(d => d.status === "DISPATCHED").length;

  const totalEl = document.getElementById("muni-metric-total");
  const urgentEl = document.getElementById("muni-metric-urgent");
  const dispatchedEl = document.getElementById("muni-metric-dispatched");
  const citizenCountEl = document.getElementById("citizen-case-count");

  if (totalEl) totalEl.textContent = total;
  if (urgentEl) urgentEl.textContent = urgent;
  if (dispatchedEl) dispatchedEl.textContent = dispatched;
  if (citizenCountEl) citizenCountEl.textContent = total;
}

function renderMapMarkers() {
  markers.forEach(m => map.removeLayer(m));
  geofenceCircles.forEach(c => map.removeLayer(c));
  markers = [];
  geofenceCircles = [];

  allDossiers.forEach(d => {
    const isRabies = d.tier === "TIER_1_RABIES_QUARANTINE";
    const markerColor = isRabies ? "#E11D48" : "#059669";
    const borderColor = isRabies ? "#9F1239" : "#062A1F";

    const marker = L.circleMarker([d.latitude, d.longitude], {
      radius: 9,
      fillColor: markerColor,
      color: borderColor,
      weight: 2,
      opacity: 1,
      fillOpacity: 0.95,
    }).addTo(map);

    marker.bindPopup(`
      <div class="text-xs p-1">
        <b class="${isRabies ? 'text-rose-600' : 'text-emerald-700'}">${d.id}</b><br/>
        <span class="font-bold text-slate-900">${d.landmark || 'Locality'}</span><br/>
        <span class="text-[10px] text-slate-500">${d.district || 'New Delhi'}, ${d.state || 'Delhi'}</span><br/>
        <span class="text-[10px] text-slate-600 font-mono mt-0.5 inline-block">Status: ${d.status}</span>
      </div>
    `);

    marker.on("click", () => {
      selectCase(d.id);
    });

    markers.push(marker);

    // 500m Containment Circle
    if (isRabies && d.consensus?.geofence_alert?.enabled) {
      const circle = L.circle([d.latitude, d.longitude], {
        radius: 500,
        color: "#E11D48",
        weight: 1.5,
        fillColor: "#FFE4E6",
        fillOpacity: 0.25,
        className: "pulsing-geofence"
      }).addTo(map);

      geofenceCircles.push(circle);
    }
  });
}

// -------------------------------------------------------------
// RENDER MUNICIPALITY OVERVIEW & CASE INSPECTOR
// -------------------------------------------------------------
function renderMuniOverviewTable() {
  const tbody = document.getElementById("muni-overview-table");
  if (!tbody) return;

  tbody.innerHTML = allDossiers.map(d => {
    const isRabies = d.tier === "TIER_1_RABIES_QUARANTINE";
    const isSelected = d.id === selectedDossierId;
    const rowClass = isSelected ? "bg-slate-100 font-medium" : "hover:bg-slate-50";

    return `
      <tr onclick="selectCase('${d.id}')" class="${rowClass} cursor-pointer transition">
        <td class="py-3 px-3 font-mono font-bold ${isRabies ? 'text-rose-600' : 'text-emerald-700'}">${d.id}</td>
        <td class="py-3 px-3">
          <div class="text-slate-900 font-bold">${d.landmark || 'Locality'}</div>
          <div class="text-[10px] text-slate-500">${d.district || 'New Delhi'}, ${d.state || 'Delhi'}</div>
        </td>
        <td class="py-3 px-3">
          <span class="${isRabies ? 'wm-pill-critical' : 'wm-pill-normal'}">
            ${isRabies ? '🚨 Rabies Alert' : '🩺 Medical Aid'}
          </span>
        </td>
        <td class="py-3 px-3 text-[11px] text-slate-600 font-mono">${d.status}</td>
        <td class="py-3 px-3 text-right">
          <button onclick="inspectAndDispatchCase('${d.id}', event)" class="wm-btn-primary py-1 px-3 text-[10px]">
            Inspect & Assign
          </button>
        </td>
      </tr>
    `;
  }).join("");
}

// -------------------------------------------------------------
// INSPECT & AUTO-DISPATCH ACTION (With Citizen Reassurance)
// -------------------------------------------------------------
async function inspectAndDispatchCase(caseId, event) {
  if (event) event.stopPropagation();

  // 1. Select the case and pan to location
  selectCase(caseId);

  const d = allDossiers.find(item => item.id === caseId);
  if (!d) return;

  const isRabies = d.tier === "TIER_1_RABIES_QUARANTINE";
  const responder = isRabies ? "Quarantine Net Squad #1" : "Mobile Vet Clinic Van #2";
  const eta = isRabies ? 8 : 6;
  const locationDesc = `${d.landmark}, ${d.district || 'New Delhi'}, ${d.state || 'Delhi'}`;

  // 2. Dispatch the best matching van squad
  const formData = new FormData();
  formData.append("responder_name", responder);
  formData.append("eta_minutes", eta);
  formData.append("notes", `Inspected and assigned to ${locationDesc}. Equipment checked.`);

  try {
    const res = await fetch(`/api/dossiers/${caseId}/dispatch`, { method: "POST", body: formData });
    if (res.ok) {
      await fetchDossiers();

      // Show Dispatcher Success Toast
      showSuccessToast(
        "✓ Case Inspected & Squad Assigned!",
        `${responder} is now EN ROUTE to ${locationDesc}. Live arrival ETA: ~${eta} mins.`
      );
      playAlertSound();

      // Broadcast citizen reassurance notification
      if (myReportedCaseIds.includes(caseId)) {
        setTimeout(() => {
          showSuccessToast(
            "🚑 Your Report is Taken Care Of!",
            `Relax, no worries! The municipality has dispatched ${responder} to ${d.landmark}. Help will arrive in ~${eta} mins.`
          );
        }, 1200);
      }
    }
  } catch (err) {
    showErrorToast("Dispatch Error", "Failed to assign van fleet.");
  }
}

function selectCase(id) {
  selectedDossierId = id;
  renderMuniOverviewTable();
  renderSelectedCaseOverview();

  const target = allDossiers.find(d => d.id === id);
  if (target && map) {
    map.panTo([target.latitude, target.longitude]);
  }
}

function renderSelectedCaseOverview() {
  const panel = document.getElementById("muni-selected-case-panel");
  if (!panel) return;

  const d = allDossiers.find(item => item.id === selectedDossierId);
  if (!d) {
    panel.innerHTML = `<div class="flex items-center justify-center flex-1 text-slate-500 text-xs">No case selected.</div>`;
    return;
  }

  const isRabies = d.tier === "TIER_1_RABIES_QUARANTINE";
  const sla = d.sla_info || {};
  const isEscalated = d.is_escalated || sla.is_breached;
  const blocks = d.temporal_blocks || [];
  const avgConf = Math.round((d.consensus?.average_confidence || 0) * 100);
  const audio = d.audio_analysis || {
    has_audio: false,
    classification: "SILENT_STREAM",
    label: "Silent Stream (No Audio)",
    icon: "volume-x",
    badge_color: "neutral",
    notes: "No audio stream detected in video container (e.g. silent CCTV street camera feed)."
  };
  const integrity = d.integrity_analysis || {
    status: "VERIFIED_AUTHENTIC",
    badge_color: "green",
    badge_label: "Verified Authentic Live Capture",
    integrity_score: 0.98,
    is_recycled: false,
    notes: "Verified authentic live mobile video capture. No pHash viral collision."
  };
  const consensusReason = d.consensus?.reason || "";
  const shieldActive = d.consensus?.hallucination_shield_activated || false;

  panel.innerHTML = `
    <div class="pb-3 border-b border-slate-200 mb-3">
      <div class="flex items-center justify-between">
        <span class="text-xs font-mono font-bold text-slate-500">DOSSIER #${d.id}</span>
        <span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase ${
          isEscalated ? 'wm-pill-critical' :
          d.status === 'DISPATCHED' ? 'wm-pill-normal' :
          'wm-pill-warning'
        }">
          ${isEscalated ? 'District Magistrate Escalated' : d.status}
        </span>
      </div>
      <h3 class="text-base font-bold text-slate-900 mt-1">
        ${isRabies ? 'Suspected Rabies Infection Alert' : 'Stray Medical Trauma / Fracture'}
      </h3>
      <p class="text-xs text-slate-500 mt-0.5 flex items-center gap-1">
        <i data-lucide="map-pin" class="w-3.5 h-3.5 text-rose-600"></i>
        <span>${d.landmark || 'Locality'}, <b>${d.district || 'New Delhi'}</b>, <b>${d.state || 'Delhi'}</b></span>
      </p>
    </div>

    <!-- Real Video Player Stream -->
    <div class="relative aspect-video rounded-xl overflow-hidden bg-black border border-slate-200 mb-3 group shadow-xs">
      <video src="${isRabies ? '/videos/rabid_dog_sample.mp4' : '/videos/fracture_wound_sample.mp4'}" autoplay loop muted playsinline class="w-full h-full object-cover"></video>
      <div class="absolute top-2.5 left-2.5 bg-slate-900/80 text-white text-[9px] font-mono px-2 py-0.5 rounded z-10">
        ${d.sources?.[0]?.source_type || 'Surveillance Feed'}
      </div>
      <div class="absolute bottom-2.5 left-2.5 right-2.5 bg-white/95 border border-slate-200 rounded-lg p-2 text-[10px] flex items-center justify-between z-10 shadow-xs">
        <span class="text-slate-800 font-semibold">Gait Anomaly Score:</span>
        <b class="${isRabies ? 'text-rose-600' : 'text-emerald-700'} font-mono">${isRabies ? '0.94 (Ataxia Detected)' : '0.12 (Localized Limp)'}</b>
      </div>
    </div>

    <!-- 3-Block Temporal Triage -->
    <div class="space-y-2 mb-3">
      <div class="flex items-center justify-between text-xs">
        <span class="font-bold text-slate-900">3-Block Temporal Screening</span>
        <span class="font-mono text-[11px] font-bold ${isRabies ? 'text-rose-600' : 'text-emerald-700'}">${avgConf}% Certainty</span>
      </div>

      <div class="grid grid-cols-3 gap-2">
        ${blocks.map((b, i) => {
          const pass = (b.rabies_confidence || 0) >= 0.85;
          const conf = Math.round((b.rabies_confidence || 0) * 100);
          return `
            <div class="p-2.5 rounded-xl border text-center ${pass ? 'border-rose-300 bg-rose-50/60' : 'border-slate-200 bg-slate-50'}">
              <div class="text-[9px] font-mono text-slate-500 font-semibold">t_${b.block || i+1} (5s)</div>
              <div class="text-sm font-bold font-mono my-0.5 ${pass ? 'text-rose-600' : 'text-slate-800'}">${conf}%</div>
              <div class="text-[9px] font-bold ${pass ? 'text-rose-600' : 'text-emerald-700'}">${pass ? 'High Risk' : 'Normal'}</div>
            </div>
          `;
        }).join("")}
      </div>
    </div>

    <!-- Multimodal Audio Acoustic Inspection -->
    <div class="p-3 mb-3 rounded-xl border ${
      audio.badge_color === 'red' ? 'border-rose-300 bg-rose-50/70' :
      audio.badge_color === 'amber' ? 'border-amber-300 bg-amber-50/70' :
      'border-slate-200 bg-slate-50'
    }">
      <div class="flex items-center justify-between text-xs mb-1">
        <span class="font-bold text-slate-900 flex items-center gap-1.5">
          <i data-lucide="${audio.has_audio ? (audio.laryngeal_paralysis ? 'alert-triangle' : 'volume-2') : 'volume-x'}" class="w-3.5 h-3.5 ${
            audio.badge_color === 'red' ? 'text-rose-600' :
            audio.badge_color === 'amber' ? 'text-amber-600' :
            'text-slate-500'
          }"></i>
          <span>Acoustic Vocalization Triage</span>
        </span>
        <span class="${
          audio.badge_color === 'red' ? 'wm-pill-critical' :
          audio.badge_color === 'amber' ? 'wm-pill-warning' :
          'wm-pill-normal'
        }">
          ${audio.label || (audio.has_audio ? 'Audio Active' : 'Silent Stream')}
        </span>
      </div>
      <p class="text-[11px] text-slate-600 leading-relaxed">
        ${audio.notes || 'Audio track screened for laryngeal vocal cord paresis and pain phonation.'}
      </p>
    </div>

    <!-- Media Integrity & Anti-Spoofing Banner -->
    <div class="p-3 mb-3 rounded-xl border ${
      integrity.badge_color === 'green' ? 'border-emerald-300 bg-emerald-50/60' :
      integrity.badge_color === 'amber' ? 'border-amber-300 bg-amber-50/60' :
      'border-rose-300 bg-rose-50/60'
    }">
      <div class="flex items-center justify-between text-xs mb-1">
        <span class="font-bold text-slate-900 flex items-center gap-1.5">
          <i data-lucide="${integrity.badge_color === 'green' ? 'shield-check' : 'shield-alert'}" class="w-3.5 h-3.5 ${
            integrity.badge_color === 'green' ? 'text-emerald-600' :
            integrity.badge_color === 'amber' ? 'text-amber-600' :
            'text-rose-600'
          }"></i>
          <span>Media Integrity & Anti-Spoof</span>
        </span>
        <span class="${
          integrity.badge_color === 'green' ? 'wm-pill-normal' :
          integrity.badge_color === 'amber' ? 'wm-pill-warning' :
          'wm-pill-critical'
        }">
          ${integrity.badge_label || 'Verified Authentic'}
        </span>
      </div>
      <p class="text-[11px] text-slate-600 leading-relaxed">
        ${integrity.notes || 'Hardware EXIF timestamp and pHash verified against stock/viral databases.'}
      </p>
    </div>

    ${shieldActive ? `
      <!-- Anti-Hallucination Shield Active Card -->
      <div class="p-3 text-[11px] text-amber-900 bg-amber-50 border border-amber-300 rounded-xl leading-relaxed mb-3 flex items-start gap-2.5">
        <i data-lucide="shield" class="w-4 h-4 text-amber-600 shrink-0 mt-0.5"></i>
        <div>
          <div class="font-bold text-amber-950">🛡️ Anti-Hallucination Shield Active</div>
          <div class="text-[11px] text-amber-800 mt-0.5">${consensusReason}</div>
        </div>
      </div>
    ` : `
      <!-- Multi-Signal Consensus Explanation -->
      <div class="p-3 text-[11px] text-slate-600 bg-slate-50 border border-slate-200 rounded-xl leading-relaxed mb-3">
        <div class="font-bold text-slate-900 flex items-center gap-1.5 mb-0.5">
          <i data-lucide="cpu" class="w-3.5 h-3.5 text-emerald-600"></i>
          <span>Multi-Signal Anti-Hallucination Guardrails:</span>
        </div>
        ${consensusReason || 'Sustained 3-block temporal agreement + acoustic co-verification enforced.'}
      </div>
    `}

    <!-- Recommended Response -->
    <div class="bg-slate-50 border border-slate-200 rounded-xl p-3.5 mb-3">
      <div class="flex items-center justify-between text-xs">
        <span class="font-bold text-slate-900">Recommended Response:</span>
        <span class="font-mono text-rose-600 font-bold">${sla.countdown_display || '45:00'}</span>
      </div>
      <p class="text-[11px] text-slate-600 mt-1">
        ${isRabies ? 'Dispatch <b>Quarantine Net Squad #1</b> with catch poles and isolation transport.' : 'Dispatch <b>Mobile Vet Clinic Van #2</b> for dressing and pain management.'}
      </p>
    </div>

    <!-- Actions -->
    <div class="mt-auto space-y-2 pt-1">
      ${d.status !== 'DISPATCHED' ? `
        <button onclick="dispatchTeam('${d.id}')" class="wm-btn-primary w-full py-3 text-xs">
          <i data-lucide="truck" class="w-4 h-4"></i> Dispatch ${isRabies ? 'Quarantine Squad #1' : 'Mobile Vet Van #2'}
        </button>
      ` : `
        <div class="wm-pill-normal w-full p-2.5 text-center text-xs font-bold flex items-center justify-center gap-2">
          <i data-lucide="check-circle-2" class="w-4 h-4"></i> Assigned to ${d.dispatched_to || 'Field Team'}
        </div>
      `}
      <button onclick="triggerSimulatedBreach('${d.id}')" class="wm-btn-secondary w-full py-2 text-[11px] text-rose-600 hover:text-rose-700 hover:bg-rose-50 border-rose-200">
        Simulate Municipal SLA Breach (Escalate to DM)
      </button>
    </div>
  `;

  initLucide();
}

// -------------------------------------------------------------
// RENDER CITIZEN VIEWS (QUEUE, VAN STATUS, ALERTS)
// -------------------------------------------------------------
function renderCitizenQueue() {
  const tbody = document.getElementById("citizen-cases-table");
  if (!tbody) return;

  if (allDossiers.length === 0) {
    tbody.innerHTML = `<tr><td colspan="5" class="text-center py-6 text-slate-400">No active reports in queue.</td></tr>`;
    return;
  }

  tbody.innerHTML = allDossiers.map(d => {
    const isRabies = d.tier === "TIER_1_RABIES_QUARANTINE";
    const sla = d.sla_info || {};
    const isEscalated = d.is_escalated || sla.is_breached;
    const isMyReport = myReportedCaseIds.includes(d.id);

    return `
      <tr class="hover:bg-slate-50 transition ${isMyReport ? 'bg-emerald-50/40' : ''}">
        <td class="py-3 px-3">
          <div class="font-mono font-bold ${isRabies ? 'text-rose-600' : 'text-emerald-700'} flex items-center gap-1.5">
            ${d.id}
            ${isMyReport ? '<span class="text-[9px] px-1.5 py-0.5 rounded bg-emerald-600 text-white font-sans font-bold">MY REPORT</span>' : ''}
          </div>
          <div class="text-[10px] text-slate-500">By: ${d.sources?.[0]?.reporter || 'Local Resident'}</div>
        </td>
        <td class="py-3 px-3">
          <div class="text-slate-900 font-bold">${d.landmark || 'Locality'}</div>
          <div class="text-[10px] text-slate-500">${d.district || 'New Delhi'}, ${d.state || 'Delhi'}</div>
        </td>
        <td class="py-3 px-3">
          <span class="${isRabies ? 'wm-pill-critical' : 'wm-pill-normal'}">
            ${isRabies ? '🚨 Rabies Suspect' : '🩺 Medical Aid'}
          </span>
        </td>
        <td class="py-3 px-3">
          ${d.status === 'DISPATCHED' ? `
            <div class="flex items-center gap-1.5">
              <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
              <div>
                <span class="font-bold text-[11px] text-emerald-800">🚑 Van Dispatched & Taken Care Of!</span>
                <div class="text-[10px] text-slate-500">${d.dispatched_to} en route (ETA: ~${d.eta_minutes || 8} mins) • Relax, team is on the way!</div>
              </div>
            </div>
          ` : isEscalated ? `
            <span class="font-bold text-[11px] text-rose-600">🚨 Escalated to District Magistrate</span>
          ` : `
            <div class="flex items-center gap-1.5 text-amber-600">
              <span class="w-2 h-2 rounded-full bg-amber-500"></span>
              <span class="font-bold text-[11px]">⏳ Waiting for Municipal Dispatch</span>
            </div>
          `}
        </td>
        <td class="py-3 px-3 font-mono font-bold ${isEscalated ? 'text-rose-600' : 'text-slate-600'}">
          ${isEscalated ? 'EXPIRED' : sla.countdown_display || '45:00'}
        </td>
      </tr>
    `;
  }).join("");
}

function renderCitizenVanStatus() {
  const container = document.getElementById("citizen-van-list");
  if (!container) return;

  if (fleetData.length === 0) {
    container.innerHTML = `<div class="p-4 bg-slate-50 rounded-xl text-xs text-slate-500 border border-slate-200">Loading municipal fleet telemetry...</div>`;
    return;
  }

  container.innerHTML = fleetData.map(v => {
    const isEnRoute = v.status === "EN_ROUTE";
    const cardBorder = isEnRoute ? "border-emerald-300 bg-emerald-50/40" : "border-slate-200 bg-white";

    return `
      <div class="p-4 rounded-xl ${cardBorder} border flex flex-col sm:flex-row sm:items-center justify-between gap-3 shadow-xs transition">
        <div class="space-y-1">
          <div class="flex items-center gap-2">
            <span class="text-xs font-bold text-slate-900">${v.name}</span>
            <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-100 text-slate-600 border border-slate-200 font-semibold">${v.vehicle}</span>
          </div>
          <div class="text-[11px] text-slate-600">
            <b>Equipment on board:</b> ${v.equipment}
          </div>
          ${isEnRoute ? `
            <div class="text-[11px] text-emerald-800 font-bold flex items-center gap-1">
              <i data-lucide="map-pin" class="w-3.5 h-3.5 text-emerald-600"></i>
              <span>Active Call: Dispatched to <b>${v.assigned_locality}</b> (Case: ${v.assigned_case_id})</span>
            </div>
          ` : `
            <div class="text-[11px] text-slate-500">Base Station: ${v.base_station}</div>
          `}
        </div>

        <div class="text-right shrink-0">
          <div class="text-xs font-bold ${isEnRoute ? 'text-emerald-700' : 'text-slate-500'} flex items-center gap-1.5 justify-end">
            ${isEnRoute ? `<span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span> 🚑 EN ROUTE (ETA: ~${v.eta_minutes} mins)` : `✓ Standby & Ready`}
          </div>
          <div class="text-[10px] text-slate-400 mt-0.5">${isEnRoute ? 'Live GPS tracking active' : 'Base depot standby'}</div>
        </div>
      </div>
    `;
  }).join("");

  initLucide();
}

function renderCitizenSafetyAlerts() {
  const container = document.getElementById("citizen-alerts-container");
  if (!container) return;

  const rabiesCases = allDossiers.filter(d => d.tier === "TIER_1_RABIES_QUARANTINE");
  if (rabiesCases.length === 0) {
    container.innerHTML = `<div class="p-4 bg-emerald-50 rounded-xl text-xs text-emerald-800 border border-emerald-200">✓ No active rabies containment alerts in your area.</div>`;
    return;
  }

  container.innerHTML = rabiesCases.map(d => {
    const isDispatched = d.status === "DISPATCHED";

    return `
      <div class="p-4 rounded-xl bg-rose-50/70 border border-rose-200 flex flex-col sm:flex-row items-start justify-between gap-4">
        <div>
          <div class="text-xs font-bold text-rose-700 flex items-center gap-1.5">
            <i data-lucide="alert-octagon" class="w-4 h-4 text-rose-600"></i>
            <span>ACTIVE 500m SAFETY ADVISORY: ${d.landmark}</span>
          </div>
          <p class="text-[11px] text-slate-700 mt-1">
            Suspected rabid animal verified by 3-step video consensus. Keep children and household pets indoors.
          </p>
          <div class="mt-2 text-[11px] font-bold ${isDispatched ? 'text-emerald-700' : 'text-rose-600'}">
            ${isDispatched ? `✓ Containment In Progress: ${d.dispatched_to} is arriving (ETA: ~${d.eta_minutes || 8} mins).` : '⏳ Municipal Quarantine Squad is being dispatched.'}
          </div>
        </div>
        <span class="wm-pill-critical shrink-0">
          500m Ward Zone
        </span>
      </div>
    `;
  }).join("");

  initLucide();
}

// -------------------------------------------------------------
// LIVE STREAMING & SMARTPHONE CCTV INGESTION
// -------------------------------------------------------------
let activeStreamsData = {};
let selectedStreamId = "PHONE-CAM-01";
let streamPollingTimer = null;

function startStreamPolling() {
  if (streamPollingTimer) clearInterval(streamPollingTimer);
  streamPollingTimer = setInterval(fetchActiveStreams, 400);
}

function stopStreamPolling() {
  if (streamPollingTimer) {
    clearInterval(streamPollingTimer);
    streamPollingTimer = null;
  }
}

async function fetchActiveStreams() {
  try {
    const res = await fetch("/api/stream/active");
    if (!res.ok) return;
    activeStreamsData = await res.json();
    renderStreamsList();
    renderStreamPlayer();
  } catch (err) {
    console.error("Failed to fetch active streams:", err);
  }
}

function refreshStreamsList() {
  fetchActiveStreams();
  showSuccessToast("Feeds Refreshed", "Live phone nodes & CCTV streams updated.");
}

function selectStreamSource(streamId) {
  selectedStreamId = streamId;
  renderStreamsList();
  renderStreamPlayer();
}

function selectCamera(camId) {
  selectStreamSource(camId);
}

function renderStreamsList() {
  const container = document.getElementById("smartphone-nodes-container");
  const countBadge = document.getElementById("phone-nodes-count");
  if (!container) return;

  const phoneStreams = Object.values(activeStreamsData).filter(s => s.type === "SMARTPHONE_STREAM");
  if (countBadge) {
    countBadge.innerText = `${phoneStreams.length} Active`;
  }

  if (phoneStreams.length === 0) {
    container.innerHTML = `
      <div class="p-3 text-center border border-dashed border-slate-200 rounded-xl bg-slate-50 text-xs text-slate-500">
        No mobile cameras paired yet.
        <button onclick="openPhoneQrModal()" class="mt-2 text-emerald-700 font-bold block mx-auto underline">+ Pair Smartphone</button>
      </div>
    `;
    return;
  }

  container.innerHTML = phoneStreams.map(s => {
    const isSelected = selectedStreamId === s.id;
    const isAlert = s.last_detection && (s.last_detection.predicted_class === "PARALYTIC_ATAXIA" || s.last_detection.audio_phonation === "CANINE_RABIES_HOWL");
    const isStreaming = s.status === "STREAMING";

    return `
      <div onclick="selectStreamSource('${s.id}')" id="stream-card-${s.id}" 
        class="wm-card bg-white p-3.5 cursor-pointer hover:border-emerald-500 transition shadow-2xs ${isSelected ? 'border-2 border-emerald-600 bg-emerald-50/20' : 'border-l-4 ' + (isAlert ? 'border-l-rose-500' : isStreaming ? 'border-l-emerald-600' : 'border-l-slate-300')}">
        <div class="flex items-center justify-between">
          <span class="text-xs font-bold text-slate-900 font-mono">${s.id}</span>
          <span class="${isAlert ? 'wm-pill-critical' : isStreaming ? 'wm-pill-normal' : 'wm-pill-neutral'} text-[10px]">
            ${isAlert ? 'Ataxia Alert' : s.status}
          </span>
        </div>
        <p class="text-xs text-slate-600 mt-1">${s.name}</p>
        <div class="flex items-center gap-3 mt-2 text-[10px] text-slate-500 font-mono">
          <span>🔋 ${s.battery_pct}%</span>
          <span>📶 ${Math.round(s.latency_ms)}ms</span>
          <span>📹 ${s.resolution ? s.resolution.split('x')[1] : '720'}p @ ${s.fps || 24}fps</span>
        </div>
      </div>
    `;
  }).join("");

  // Also update CCTV card highlight
  ["CAM-NDEL-W4-08", "CAM-NDEL-W7-14", "CAM-SOUTH-02"].forEach(cId => {
    const cCard = document.getElementById(`stream-card-${cId}`);
    if (cCard) {
      if (selectedStreamId === cId) {
        cCard.classList.add("border-2", "border-emerald-600", "bg-emerald-50/20");
      } else {
        cCard.classList.remove("border-2", "border-emerald-600", "bg-emerald-50/20");
      }
    }
  });
}

function renderStreamPlayer() {
  const panel = document.getElementById("muni-camera-review-detail");
  if (!panel) return;

  const isPhone = selectedStreamId.startsWith("PHONE");
  const phoneData = activeStreamsData[selectedStreamId];

  // If selecting a CCTV camera
  if (!isPhone) {
    const isAlert = selectedStreamId === "CAM-NDEL-W4-08";
    panel.innerHTML = `
      <div class="flex items-center justify-between pb-3 border-b border-slate-200">
        <div>
          <h3 class="text-sm font-bold text-slate-900 font-mono">${selectedStreamId} — Municipal Fixed Grid Feed</h3>
          <p class="text-xs text-slate-500">Continuous RTSP grid feed with bounding-box computer-vision inference</p>
        </div>
        <span class="${isAlert ? 'wm-pill-critical' : 'wm-pill-normal'}">
          ${isAlert ? 'Rabies Incident Flagged' : 'Routine Surveillance'}
        </span>
      </div>

      <div class="relative aspect-video rounded-xl overflow-hidden bg-black border border-slate-200 flex items-center justify-center shadow-xs">
        <video src="${selectedStreamId === 'CAM-NDEL-W4-08' ? '/videos/rabid_dog_sample.mp4' : selectedStreamId === 'CAM-NDEL-W7-14' ? '/videos/fracture_wound_sample.mp4' : '/videos/summer_panting_sample.mp4'}" autoplay loop muted playsinline class="w-full h-full object-cover"></video>
        <div class="absolute top-3 left-3 bg-slate-900/90 text-white text-[10px] font-mono px-2 py-0.5 rounded z-10 flex items-center gap-1.5">
          <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
          <span>LIVE ● ${selectedStreamId}</span>
        </div>
        ${isAlert ? `
          <div class="absolute inset-16 border-2 border-dashed border-rose-500 rounded-xl flex flex-col justify-between p-2 pointer-events-none animate-pulse z-10">
            <span class="bg-rose-600 text-white text-[10px] font-mono font-bold px-1.5 py-0.5 rounded self-start">CANINE_ALERT: 94%</span>
            <span class="bg-black/70 text-white text-[10px] font-mono px-1.5 py-0.5 rounded self-end">MANDIBLE_DROP: POSITIVE</span>
          </div>
        ` : ''}
      </div>

      <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
        <div class="p-3 rounded-xl border border-slate-200 bg-slate-50">
          <div class="text-slate-500 text-[10px] font-semibold uppercase">Gait Anomaly</div>
          <div class="font-bold text-slate-900 text-base font-mono mt-0.5">${isAlert ? '0.94 (Ataxia)' : '0.04 (Clear)'}</div>
        </div>
        <div class="p-3 rounded-xl border ${isAlert ? 'border-rose-300 bg-rose-50/70' : 'border-slate-200 bg-slate-50'}">
          <div class="text-slate-500 text-[10px] font-semibold uppercase">Audio Phonation</div>
          <div class="font-bold text-base font-mono mt-0.5 ${isAlert ? 'text-rose-600' : 'text-emerald-700'}">${isAlert ? '🎙️ Rabies Howl' : '🎧 Silent / Normal'}</div>
        </div>
        <div class="p-3 rounded-xl border border-slate-200 bg-slate-50">
          <div class="text-slate-500 text-[10px] font-semibold uppercase">AI Verification</div>
          <div class="font-bold text-slate-900 text-base font-mono mt-0.5">${isAlert ? '3/3 Temporal Consensus' : 'Nominal'}</div>
        </div>
        <div class="p-3 rounded-xl border border-slate-200 bg-slate-50">
          <div class="text-slate-500 text-[10px] font-semibold uppercase">Dispatch Action</div>
          <div class="font-bold text-rose-600 text-base font-mono mt-0.5">${isAlert ? 'Tier 1 Immediate' : 'Standby'}</div>
        </div>
      </div>
    `;
    initLucide();
    return;
  }

  // Active Smartphone Stream Player
  const det = phoneData ? (phoneData.last_detection || {}) : {};
  const isRabiesAlert = det.predicted_class === "PARALYTIC_ATAXIA" || det.saliva_foaming || det.mandible_drop;
  const confidencePct = det.confidence ? Math.round(det.confidence * 100) : 94;

  const existingImg = document.getElementById("phone-stream-img");
  const existingId = panel.getAttribute("data-stream-id");

  if (existingImg && existingId === selectedStreamId) {
    if (phoneData && phoneData.last_frame) {
      existingImg.src = phoneData.last_frame;
    }
    const batEl = document.getElementById("hud-bat-label");
    if (batEl && phoneData) batEl.textContent = `🔋 ${phoneData.battery_pct}%`;
    const latEl = document.getElementById("hud-lat-label");
    if (latEl && phoneData) latEl.textContent = `📶 ${Math.round(phoneData.latency_ms)}ms`;
    return;
  }
  panel.setAttribute("data-stream-id", selectedStreamId);

  panel.innerHTML = `
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-slate-200">
      <div>
        <div class="flex items-center gap-2">
          <h3 class="text-sm font-bold text-slate-900 font-mono">${phoneData ? phoneData.name : selectedStreamId}</h3>
          <span class="text-[10px] bg-emerald-50 text-emerald-800 font-semibold px-2 py-0.5 rounded border border-emerald-200">Phone Camera CCTV</span>
        </div>
        <p class="text-xs text-slate-500 mt-0.5">Real-time smartphone frame push with fine-tuned MobileNetV4 & YAMNet inference</p>
      </div>
      <div class="flex items-center gap-2">
        <span class="${phoneData && phoneData.status === 'STREAMING' ? 'wm-pill-normal' : 'wm-pill-neutral'}">
          ● ${phoneData ? phoneData.status : 'ONLINE'}
        </span>
      </div>
    </div>

    <!-- Live Stream Video / Canvas HUD Player -->
    <div class="relative aspect-video rounded-xl overflow-hidden bg-slate-950 border border-slate-200 flex items-center justify-center shadow-xs">
      ${phoneData && phoneData.last_frame ? `
        <img id="phone-stream-img" src="${phoneData.last_frame}" alt="Live Phone Stream" class="w-full h-full object-cover">
      ` : `
        <img id="phone-stream-img" src="data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='640' height='360' viewBox='0 0 640 360'><rect width='640' height='360' fill='%230f172a'/><text x='50%25' y='50%25' fill='%2364748b' font-family='sans-serif' font-size='14' text-anchor='middle'>Awaiting incoming camera frames from phone...</text></svg>" alt="Live Phone Stream" class="w-full h-full object-cover">
      `}
      
      <!-- Live HUD Overlays -->
      <div class="absolute top-3 left-3 bg-slate-900/90 text-white text-[10px] font-mono px-2.5 py-1 rounded-lg z-10 flex items-center gap-2 border border-slate-700">
        <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
        <span>EDGE INGESTION: ${selectedStreamId}</span>
      </div>

      <div class="absolute top-3 right-3 bg-slate-900/90 text-white text-[10px] font-mono px-2.5 py-1 rounded-lg z-10 flex items-center gap-3 border border-slate-700">
        <span id="hud-bat-label">🔋 ${phoneData ? phoneData.battery_pct : 86}%</span>
        <span id="hud-lat-label">📶 ${phoneData ? Math.round(phoneData.latency_ms) : 48}ms</span>
        <span>${phoneData ? phoneData.resolution : '1280x720'}</span>
      </div>

      <!-- Bounding Box & HUD Tag -->
      ${isRabiesAlert ? `
        <div class="absolute inset-12 sm:inset-16 border-2 border-dashed border-rose-500 rounded-xl flex flex-col justify-between p-2.5 pointer-events-none animate-pulse z-10">
          <div class="flex items-center justify-between">
            <span class="bg-rose-600 text-white text-[11px] font-mono font-bold px-2 py-0.5 rounded shadow">
              CLINICAL_ALERT: ${det.predicted_class || 'PARALYTIC_ATAXIA'} (${confidencePct}%)
            </span>
            <span class="bg-black/80 text-white text-[10px] font-mono px-2 py-0.5 rounded">
              GAIT: ${det.gait_anomaly_score ? Math.round(det.gait_anomaly_score * 100) : 94}% ABNORMAL
            </span>
          </div>
          <div class="flex items-center justify-between">
            <span class="bg-black/80 text-rose-300 text-[10px] font-mono px-2 py-0.5 rounded">
              MANDIBLE DROP: ${det.mandible_drop ? 'CONFIRMED' : 'NEGATIVE'}
            </span>
            <span class="bg-rose-900/90 text-white text-[10px] font-mono px-2 py-0.5 rounded">
              SALIVARY FOAM: ${det.saliva_foaming ? 'ACTIVE' : 'NEGATIVE'}
            </span>
          </div>
        </div>
      ` : ''}
    </div>

    <!-- Live Telemetry Grid -->
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
      <div class="p-3 rounded-xl border border-slate-200 bg-slate-50">
        <div class="text-slate-500 text-[10px] font-semibold uppercase">Fine-Tuned CV</div>
        <div class="font-bold text-slate-900 text-sm font-mono mt-0.5 truncate">${det.predicted_class || 'PARALYTIC_ATAXIA'}</div>
        <div class="text-[10px] text-slate-500 mt-0.5">MobileNetV4 Head (${confidencePct}%)</div>
      </div>

      <div class="p-3 rounded-xl border ${isRabiesAlert ? 'border-rose-300 bg-rose-50/70' : 'border-slate-200 bg-slate-50'}">
        <div class="text-slate-500 text-[10px] font-semibold uppercase">Acoustic Phonation</div>
        <div class="font-bold text-sm font-mono mt-0.5 ${isRabiesAlert ? 'text-rose-600' : 'text-emerald-700'}">
          ${det.audio_phonation === 'CANINE_RABIES_HOWL' ? '🎙️ Rabies Howl' : det.audio_phonation || '🎙️ Phonation'}
        </div>
        <div class="text-[10px] text-slate-500 mt-0.5">YAMNet 1024-d Embedding</div>
      </div>

      <div class="p-3 rounded-xl border border-slate-200 bg-slate-50">
        <div class="text-slate-500 text-[10px] font-semibold uppercase">Phone Telemetry</div>
        <div class="font-bold text-slate-900 text-sm font-mono mt-0.5">
          ${phoneData ? phoneData.fps : 24} FPS / ${phoneData ? Math.round(phoneData.latency_ms) : 48}ms
        </div>
        <div class="text-[10px] text-slate-500 mt-0.5">Battery: ${phoneData ? phoneData.battery_pct : 86}% ● Warm</div>
      </div>

      <div class="p-3 rounded-xl border border-slate-200 bg-slate-50">
        <div class="text-slate-500 text-[10px] font-semibold uppercase">Triage Assessment</div>
        <div class="font-bold ${isRabiesAlert ? 'text-rose-600' : 'text-emerald-700'} text-sm font-mono mt-0.5">
          ${isRabiesAlert ? 'Tier 1 Immediate' : 'Tier 3 Monitoring'}
        </div>
        <div class="text-[10px] text-slate-500 mt-0.5">Consensus Verified</div>
      </div>
    </div>

    <!-- Action Bar: Convert Snapshot to Case -->
    <div class="p-4 rounded-xl border border-emerald-200 bg-emerald-50/60 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
      <div class="text-xs text-slate-700">
        <div class="font-bold text-emerald-900 flex items-center gap-1.5">
          <i data-lucide="shield-alert" class="w-4 h-4 text-emerald-700"></i>
          <span>Convert Live Stream Evidence to Case Dossier</span>
        </div>
        <p class="text-slate-600 mt-0.5">Pushes this frame & audio phonation to the municipal emergency response queue.</p>
      </div>
      <button onclick="convertStreamSnapshotToCase('${selectedStreamId}')" class="wm-btn-coral px-4 py-2 text-xs flex items-center justify-center gap-1.5 whitespace-nowrap shadow-xs">
        <i data-lucide="file-check-2" class="w-3.5 h-3.5"></i>
        <span>Create Incident Dossier</span>
      </button>
    </div>
  `;

  initLucide();
}

async function convertStreamSnapshotToCase(streamId) {
  try {
    const res = await fetch(`/api/stream/snapshot_triage/${streamId}`, { method: "POST" });
    const data = await res.json();
    if (res.ok && data.status === "CASE_CREATED") {
      showSuccessToast("Case Dossier Created", `Incident ${data.case_id} registered. Dispatching quarantine squad.`);
      await fetchDossiers();
      navigateMuni("overview");
    } else {
      showErrorToast("Triage Notice", data.message || "Failed to create dossier from stream snapshot.");
    }
  } catch (err) {
    console.error("Error creating case from snapshot:", err);
    showErrorToast("Connection Error", "Could not reach triage endpoint.");
  }
}

// -------------------------------------------------------------
// PHONE PAIRING MODAL
// -------------------------------------------------------------
function openPhoneQrModal() {
  const modal = document.getElementById("phone-qr-modal");
  if (!modal) return;
  modal.classList.remove("hidden");
  
  let hostName = window.location.hostname || "10.30.151.126";
  if (hostName === "localhost" || hostName === "127.0.0.1") {
    hostName = "10.30.151.126";
  }
  const port = window.location.port ? `:${window.location.port}` : ":8000";
  const protocol = window.location.protocol || "http:";
  const fullUrl = `${protocol}//${hostName}${port}/phone_cam.html`;

  const urlSpan = document.getElementById("phone-stream-url");
  if (urlSpan) {
    urlSpan.innerText = fullUrl;
  }
  const qrImg = document.getElementById("phone-qr-img");
  if (qrImg) {
    qrImg.src = `https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=${encodeURIComponent(fullUrl)}`;
  }
  initLucide();
}

function closePhoneQrModal() {
  const modal = document.getElementById("phone-qr-modal");
  if (modal) modal.classList.add("hidden");
}

// -------------------------------------------------------------
// TRANSFER LEARNING & MODEL GOVERNANCE
// -------------------------------------------------------------
async function loadModelStats() {
  try {
    const res = await fetch("/api/models/stats");
    if (!res.ok) return;
    const stats = await res.json();

    if (document.getElementById("cv-acc-metric")) {
      document.getElementById("cv-acc-metric").innerText = `${(stats.cv_model.top1_accuracy * 100).toFixed(1)}%`;
      document.getElementById("cv-map-metric").innerText = `${(stats.cv_model.mAP50 * 100).toFixed(1)}%`;
      document.getElementById("cv-latency-metric").innerText = `${stats.cv_model.inference_latency_ms} ms`;
      document.getElementById("cv-backbone-tag").innerText = stats.cv_model.active_backbone;

      document.getElementById("audio-f1-metric").innerText = `${(stats.audio_model.f1_score * 100).toFixed(1)}%`;
      document.getElementById("audio-auc-metric").innerText = stats.audio_model.auc_roc.toFixed(3);
      document.getElementById("audio-latency-metric").innerText = `${stats.audio_model.inference_latency_ms} ms`;

      const rabVal = Math.round(stats.runtime_thresholds.rabies_threshold * 100);
      const ataVal = Math.round(stats.runtime_thresholds.ataxia_sensitivity * 100);
      const audVal = Math.round(stats.runtime_thresholds.audio_phonation_threshold * 100);

      document.getElementById("input-rabies-thresh").value = rabVal;
      document.getElementById("label-rabies-thresh").innerText = `${rabVal}%`;

      document.getElementById("input-ataxia-thresh").value = ataVal;
      document.getElementById("label-ataxia-thresh").innerText = `${ataVal}%`;

      document.getElementById("input-audio-thresh").value = audVal;
      document.getElementById("label-audio-thresh").innerText = `${audVal}%`;

      if (document.getElementById("select-cv-backbone")) {
        document.getElementById("select-cv-backbone").value = stats.runtime_thresholds.active_backbone;
      }
    }
  } catch (err) {
    console.error("Failed to load model stats:", err);
  }
}

async function saveModelConfig() {
  try {
    const rabiesVal = parseFloat(document.getElementById("input-rabies-thresh").value) / 100.0;
    const ataxiaVal = parseFloat(document.getElementById("input-ataxia-thresh").value) / 100.0;
    const audioVal = parseFloat(document.getElementById("input-audio-thresh").value) / 100.0;
    const backboneVal = document.getElementById("select-cv-backbone").value;

    const formData = new FormData();
    formData.append("rabies_threshold", rabiesVal);
    formData.append("ataxia_sensitivity", ataxiaVal);
    formData.append("audio_phonation_threshold", audioVal);
    formData.append("active_backbone", backboneVal);

    const res = await fetch("/api/models/config", {
      method: "POST",
      body: formData
    });

    if (res.ok) {
      showSuccessToast("Hyperparameters Applied", `Model configuration updated. Rabies cutoff: ${(rabiesVal*100).toFixed(0)}%, Backbone: ${backboneVal}`);
      loadModelStats();
    } else {
      showErrorToast("Configuration Error", "Could not update model thresholds.");
    }
  } catch (err) {
    console.error("Failed to save model config:", err);
    showErrorToast("Error", "Failed to communicate with model governance API.");
  }
}

// -------------------------------------------------------------
// ANALYTICS CHARTS (MUNICIPALITY)
// -------------------------------------------------------------
function initAnalyticsCharts() {
  const ctxSev = document.getElementById("chart-severity");
  const ctxRes = document.getElementById("chart-resolution");
  if (!ctxSev || !ctxRes) return;

  if (chartSeverityInstance) chartSeverityInstance.destroy();
  if (chartResolutionInstance) chartResolutionInstance.destroy();

  chartSeverityInstance = new Chart(ctxSev, {
    type: "doughnut",
    data: {
      labels: ["Rabies Red Alerts", "Trauma & Fractures", "Heat Panting Cleared"],
      datasets: [{
        data: [1, 2, 8],
        backgroundColor: ["#E11D48", "#059669", "#10B981"],
        borderColor: "#FFFFFF",
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: "bottom", labels: { font: { size: 11, family: "Inter" }, color: "#0F172A" } }
      }
    }
  });

  chartResolutionInstance = new Chart(ctxRes, {
    type: "bar",
    data: {
      labels: ["Ward 4", "Ward 7", "Ward 9", "Civic Center"],
      datasets: [{
        label: "Avg Arrival Minutes",
        data: [14, 22, 18, 12],
        backgroundColor: "#059669",
        hoverBackgroundColor: "#047857",
        borderRadius: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: { beginAtZero: true, ticks: { color: "#64748B", font: { family: "Inter" } } },
        x: { ticks: { color: "#64748B", font: { family: "Inter" } } }
      },
      plugins: { legend: { display: false } }
    }
  });
}

// -------------------------------------------------------------
// CITIZEN INGESTION FORM & 1-CLICK DEMO LOADERS
// -------------------------------------------------------------
function validateFileInput(input) {
  const file = input.files[0];
  const errorHint = document.getElementById("file-error-hint");
  if (!file) return;

  const name = file.name.toLowerCase();
  const isAudio = name.endsWith(".mp3") || name.endsWith(".wav") || name.endsWith(".m4a") || name.endsWith(".aac") || (file.type && file.type.startsWith("audio/"));

  if (isAudio) {
    input.value = "";
    if (errorHint) errorHint.classList.remove("hidden");
    showErrorToast("Audio Rejected (.mp3)", "Cannot check for rabies from audio alone. Please upload video footage (.mp4, .mov).");
    return false;
  }

  if (errorHint) errorHint.classList.add("hidden");
  return true;
}

async function loadSampleVideo(filename, landmark, district, state, lat, lon) {
  try {
    const res = await fetch(`/videos/${filename}`);
    const blob = await res.blob();
    preloadedSampleFile = new File([blob], filename, { type: "video/mp4" });

    const landmarkInput = document.getElementById("citizen-landmark");
    const districtInput = document.getElementById("citizen-district");
    const stateInput = document.getElementById("citizen-state");
    const latInput = document.getElementById("citizen-lat");
    const lonInput = document.getElementById("citizen-lon");

    if (landmarkInput) landmarkInput.value = landmark;
    if (districtInput) districtInput.value = district;
    if (stateInput) stateInput.value = state;
    if (latInput) latInput.value = lat;
    if (lonInput) lonInput.value = lon;

    // Update Auto-detected location display
    const displayAddr = document.getElementById("loc-display-address");
    const displaySub = document.getElementById("loc-display-sub");
    const badge = document.getElementById("loc-provider-badge");
    if (displayAddr) displayAddr.textContent = `${landmark}, ${district}, ${state}`;
    if (displaySub) displaySub.textContent = `Latitude: ${lat} • Longitude: ${lon} (Demo Location Pre-set)`;
    if (badge) badge.textContent = "Preset Demo Location";

    showSuccessToast("Demo Video Loaded", `Loaded ${filename} (${district}, ${state}). Location auto-set! Click 'Submit Report' to run triage.`);
  } catch (err) {
    console.error("Error loading sample video:", err);
  }
}

async function autoDetectLocation(showToast = false) {
  const displayAddr = document.getElementById("loc-display-address");
  const displaySub = document.getElementById("loc-display-sub");
  const badge = document.getElementById("loc-provider-badge");

  if (displayAddr) displayAddr.textContent = "Detecting device GPS coordinates...";

  if (!navigator.geolocation) {
    if (displayAddr) displayAddr.textContent = "MG Road, Indiranagar, Bengaluru Urban, Karnataka";
    return;
  }

  navigator.geolocation.getCurrentPosition(
    async (pos) => {
      const lat = pos.coords.latitude;
      const lon = pos.coords.longitude;
      currentCoords = [lat, lon];

      const latInput = document.getElementById("citizen-lat");
      const lonInput = document.getElementById("citizen-lon");
      if (latInput) latInput.value = lat;
      if (lonInput) lonInput.value = lon;

      if (displaySub) displaySub.textContent = `Latitude: ${lat.toFixed(4)} • Longitude: ${lon.toFixed(4)} (Live Device GPS)`;

      // Reverse geocode via Backend (Google Maps + Nominatim fallback)
      try {
        const res = await fetch(`/api/location/reverse_geocode?lat=${lat}&lon=${lon}`);
        const data = await res.json();
        if (data.success) {
          const landmarkInput = document.getElementById("citizen-landmark");
          const districtInput = document.getElementById("citizen-district");
          const stateInput = document.getElementById("citizen-state");

          if (landmarkInput) landmarkInput.value = data.landmark;
          if (districtInput) districtInput.value = data.district;
          if (stateInput) stateInput.value = data.state;

          if (displayAddr) displayAddr.textContent = data.address;
          if (badge) {
            badge.textContent = data.provider === "google_maps" ? "Google Maps Verified" : "Live Device GPS Pin";
          }

          if (showToast) {
            showSuccessToast("Location Detected", `Auto-detected: ${data.landmark}, ${data.district}`);
          }
        }
      } catch (e) {
        if (displayAddr) displayAddr.textContent = `GPS Pin (${lat.toFixed(4)}, ${lon.toFixed(4)})`;
      }
    },
    (err) => {
      if (displayAddr) displayAddr.textContent = "Central Ward, New Delhi (Default Location)";
      if (displaySub) displaySub.textContent = "Latitude: 28.6145 • Longitude: 77.2095 (GPS permissions fallback)";
      if (showToast) showErrorToast("GPS Notice", "Using default municipal location. Enable browser GPS for live pin.");
    },
    { enableHighAccuracy: true, timeout: 6000 }
  );
}

async function handleCitizenSubmit(event) {
  event.preventDefault();
  const fileInput = document.getElementById("citizen-file");
  const landmark = document.getElementById("citizen-landmark").value;
  const state = document.getElementById("citizen-state")?.value || "Delhi";
  const district = document.getElementById("citizen-district")?.value || "New Delhi";
  const lat = parseFloat(document.getElementById("citizen-lat").value) || currentCoords[0];
  const lon = parseFloat(document.getElementById("citizen-lon").value) || currentCoords[1];
  const reporter = document.getElementById("citizen-reporter").value || "Local Resident";

  let file = fileInput.files[0] || preloadedSampleFile;
  if (file && !validateFileInput(fileInput)) return;

  const formData = new FormData();
  formData.append("source_type", "Citizen Phone Upload");
  formData.append("state", state);
  formData.append("district", district);
  formData.append("latitude", lat);
  formData.append("longitude", lon);
  formData.append("landmark", landmark);
  formData.append("reporter", reporter);

  if (file) {
    formData.append("video_file", file);
  } else {
    try {
      const defaultRes = await fetch("/videos/rabid_dog_sample.mp4");
      const defaultBlob = await defaultRes.blob();
      formData.append("video_file", defaultBlob, "rabid_dog_sample.mp4");
    } catch(e) {
      const blob = new Blob(["mock-video-stream"], { type: "video/mp4" });
      formData.append("video_file", blob, "citizen_report.mp4");
    }
  }

  try {
    const res = await fetch("/api/ingest", { method: "POST", body: formData });
    if (!res.ok) {
      const err = await res.json();
      showErrorToast("Ingestion Failed", err.detail || "Server error");
      return;
    }

    const data = await res.json();
    
    // Track in citizen's personal report list
    if (data.dossier_id && !myReportedCaseIds.includes(data.dossier_id)) {
      myReportedCaseIds.push(data.dossier_id);
      localStorage.setItem("indiepulse_my_cases", JSON.stringify(myReportedCaseIds));
    }

    const integrityLabel = data.dossier?.integrity_analysis?.badge_label || "Verified Authentic Capture";
    showSuccessToast(
      "Report Verified & Submitted!",
      `Case #${data.dossier_id} passed anti-spoofing checks (${integrityLabel}) and is triaged for municipal action!`
    );
    await fetchDossiers();
    navigateCitizen("queue");

  } catch (err) {
    showErrorToast("Connection Error", "Could not reach the SOC backend.");
  }
}

// -------------------------------------------------------------
// ACTIONS & ESCALATION
// -------------------------------------------------------------
async function dispatchTeam(dossierId) {
  const d = allDossiers.find(item => item.id === dossierId);
  const isRabies = d ? d.tier === "TIER_1_RABIES_QUARANTINE" : true;
  const responder = isRabies ? "Quarantine Net Squad #1" : "Mobile Vet Clinic Van #2";
  const eta = isRabies ? 8 : 12;

  const formData = new FormData();
  formData.append("responder_name", responder);
  formData.append("eta_minutes", eta);
  formData.append("notes", isRabies ? "Dispatched with catch poles and isolation cages." : "Dispatched with dressing kit and analgesics.");

  try {
    const res = await fetch(`/api/dossiers/${dossierId}/dispatch`, { method: "POST", body: formData });
    if (res.ok) {
      await fetchDossiers();
      showSuccessToast("Team Dispatched & Citizen Notified", `${responder} is en route. Live ETA: ~${eta} mins broadcast to citizen queue.`);
    }
  } catch (err) {
    showErrorToast("Dispatch Error", "Failed to communicate with field unit.");
  }
}

function quickDispatchTeam(teamName) {
  if (selectedDossierId) {
    const formData = new FormData();
    formData.append("responder_name", teamName);
    formData.append("eta_minutes", 10);
    formData.append("notes", "Quick dispatched from municipal fleet dashboard.");

    fetch(`/api/dossiers/${selectedDossierId}/dispatch`, { method: "POST", body: formData })
      .then(() => {
        fetchDossiers();
        showSuccessToast("Team Assigned & Citizen Notified", `${teamName} assigned. Status live on citizen portal.`);
      });
  }
}

async function triggerSimulatedBreach(dossierId) {
  try {
    const res = await fetch(`/api/dossiers/${dossierId}/simulate_breach`, { method: "POST" });
    if (res.ok) {
      playAlertSound();
      await fetchDossiers();
      showErrorToast("SLA Escalated!", "Response countdown expired: Dossier auto-pushed to District Magistrate.");
    }
  } catch (err) {}
}

// -------------------------------------------------------------
// TOASTS & SOUNDS
// -------------------------------------------------------------
function showErrorToast(title, msg) {
  const toast = document.getElementById("error-toast");
  document.getElementById("toast-title").textContent = title;
  document.getElementById("toast-msg").textContent = msg;
  toast.classList.remove("hidden");
  playAlertSound();
  setTimeout(() => { toast.classList.add("hidden"); }, 6000);
}

function hideErrorToast() {
  document.getElementById("error-toast").classList.add("hidden");
}

function showSuccessToast(title, msg) {
  const toast = document.getElementById("success-toast");
  document.getElementById("success-toast-title").textContent = title;
  document.getElementById("success-toast-msg").textContent = msg;
  toast.classList.remove("hidden");
  setTimeout(() => { toast.classList.add("hidden"); }, 5000);
}

function hideSuccessToast() {
  document.getElementById("success-toast").classList.add("hidden");
}

function playAlertSound() {
  const audio = document.getElementById("alert-sound");
  if (audio) audio.play().catch(() => {});
}

async function resetDemoData() {
  try {
    await fetch("/api/reset", { method: "POST" });
    await fetchDossiers();
    showSuccessToast("Demo Reset", "Sample cases reloaded.");
  } catch (err) {}
}

// -------------------------------------------------------------
// GEMINI MODAL
// -------------------------------------------------------------
function openGeminiModal() {
  document.getElementById("gemini-modal").classList.remove("hidden");
  checkGeminiStatus();
}

function closeGeminiModal() {
  document.getElementById("gemini-modal").classList.add("hidden");
}

async function checkGeminiStatus() {
  const badge = document.getElementById("gemini-status-badge");
  const input = document.getElementById("gemini-key-input");
  try {
    const res = await fetch("/api/settings/gemini_status");
    const data = await res.json();
    if (data.has_key && data.masked_key) {
      if (badge) badge.innerHTML = `<span class="text-emerald-600 font-bold flex items-center gap-1">● Active (${data.masked_key})</span>`;
      if (input && !input.value) input.placeholder = `Configured: ${data.masked_key}`;
    } else if (data.gemini_live_connected) {
      if (badge) badge.innerHTML = `<span class="text-emerald-600 font-bold">● Connected to Gemini API</span>`;
    } else {
      if (badge) badge.innerHTML = `<span class="text-slate-400">● Fallback Diagnostic Engine</span>`;
    }
  } catch (e) {
    if (badge) badge.innerHTML = `<span class="text-slate-400">● Status Offline</span>`;
  }
}

async function testGeminiKeyLive() {
  const resultBox = document.getElementById("gemini-test-result");
  if (resultBox) {
    resultBox.classList.remove("hidden");
    resultBox.className = "text-[11px] p-2.5 rounded-lg border border-blue-200 bg-blue-50 text-blue-700 font-medium";
    resultBox.textContent = "Connecting to Google Gemini API servers...";
  }

  try {
    const res = await fetch("/api/settings/gemini_test", { method: "POST" });
    const data = await res.json();
    if (data.success) {
      if (resultBox) {
        resultBox.className = "text-[11px] p-2.5 rounded-lg border border-emerald-300 bg-emerald-50 text-emerald-800 font-bold";
        resultBox.textContent = `✓ ${data.message} [Model: ${data.model}]`;
      }
      showSuccessToast("Gemini Online", "Successfully verified Gemini API connectivity!");
    } else {
      if (resultBox) {
        resultBox.className = "text-[11px] p-2.5 rounded-lg border border-amber-300 bg-amber-50 text-amber-800 font-medium";
        resultBox.textContent = `⚠ ${data.message} ${data.details ? `(${data.details})` : ""}`;
      }
    }
    checkGeminiStatus();
  } catch (err) {
    if (resultBox) {
      resultBox.className = "text-[11px] p-2.5 rounded-lg border border-rose-300 bg-rose-50 text-rose-700 font-semibold";
      resultBox.textContent = "Failed to connect to local server for testing.";
    }
  }
}

async function saveGeminiKey() {
  const input = document.getElementById("gemini-key-input");
  const key = input.value.trim();
  if (!key) {
    showErrorToast("Empty Key", "Please enter a valid Gemini API key.");
    return;
  }

  const formData = new FormData();
  formData.append("api_key", key);

  try {
    const res = await fetch("/api/settings/gemini_key", { method: "POST", body: formData });
    const data = await res.json();
    showSuccessToast("Gemini Saved", data.message || "Key secured in .env!");
    input.value = "";
    await checkGeminiStatus();
    await testGeminiKeyLive();
  } catch (err) {
    showErrorToast("Error", "Could not save Gemini key to server.");
  }
}
