let allScans = [];

// Placeholder SVG (rectangle coloré, sans emoji)
const PLACEHOLDER_IMG = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='260' height='160'%3E%3Crect width='260' height='160' fill='%231a2e1a'/%3E%3Cpath d='M141 50a17 17 0 0 1-12.2 15.1c5.7-1.1 7.2-1.6 9.2-4.1 1 2 2 4.2 2 8 0 5.5-4.8 10-10 10z' fill='none' stroke='%2352b788' stroke-width='3' stroke-linecap='round' stroke-linejoin='round'/%3E%3Cpath d='M122 91c0-3 1.9-5.4 5.1-6 2.9-.5 5.4-1.5 6.4-2.5' fill='none' stroke='%2352b788' stroke-width='3' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E";

async function loadHistory() {
  try {
    const resp = await fetch(`${API_BASE}/history`);
    allScans = await resp.json();
    renderHistory(allScans);
  } catch {
    document.getElementById("historyGrid").innerHTML = '<div class="empty-state">Erreur de chargement</div>';
  }
}

function renderHistory(scans) {
  const grid = document.getElementById("historyGrid");
  if (!scans.length) {
    grid.innerHTML = '<div class="empty-state"><svg class="il-empty" aria-hidden="true"><use href="#ic-sprout"/></svg>Aucun scan pour le moment</div>';
    return;
  }
  grid.innerHTML = scans.map(s => {
    const report = s.ai_report || {};
    const imgSrc = s.image_path ? `${API_BASE}/image/${s.image_path}` : PLACEHOLDER_IMG;
    return `
    <div class="history-card" onclick="openScanModal(${s.id})">
      <img src="${imgSrc}" alt="${s.common_name}" loading="lazy" onerror="this.onerror=null;this.src=PLACEHOLDER_IMG"/>
      <div class="history-card-body">
        <h4>${s.common_name || "Plante inconnue"}</h4>
        <p class="sci">${s.scientific_name || ""}</p>
        <div class="history-card-badges">
          <span class="mini-badge badge ${badgeClass(s.is_edible)}"><svg class="ic"><use href="#ic-bowl"/></svg> ${s.is_edible || "?"}</span>
          <span class="mini-badge badge ${badgeClass(s.is_toxic)}"><svg class="ic"><use href="#ic-mushroom"/></svg> ${s.is_toxic || "?"}</span>
        </div>
        <p class="date">${formatDate(s.created_at)}</p>
      </div>
    </div>`;
  }).join("");
}

// Recherche
document.getElementById("historySearch").addEventListener("input", e => {
  const q = e.target.value.toLowerCase();
  renderHistory(allScans.filter(s =>
    (s.common_name || "").toLowerCase().includes(q) ||
    (s.scientific_name || "").toLowerCase().includes(q)
  ));
});

// Modal détail
async function openScanModal(id) {
  const resp = await fetch(`${API_BASE}/scan/${id}`);
  const scan = await resp.json();
  const report = scan.ai_report || {};

  const modal = document.createElement("div");
  modal.className = "modal-overlay";
  const imgSrc = scan.image_path ? `${API_BASE}/image/${scan.image_path}` : "";
  modal.innerHTML = `
    <div class="modal-content">
      <div class="modal-close">
        <h3>${scan.common_name || "Plante"}</h3>
        <button onclick="this.closest('.modal-overlay').remove()">&#x2715;</button>
      </div>
      <div style="padding:1.5rem">
        ${imgSrc ? `<img src="${imgSrc}" style="width:100%;max-height:250px;object-fit:cover;border-radius:12px;margin-bottom:1rem" alt="" onerror="this.remove()"/>` : ""}
        <p style="color:var(--text-muted);font-style:italic;margin-bottom:0.5rem">${scan.scientific_name || ""}</p>
        <p style="color:var(--accent);font-size:0.85rem;margin-bottom:1rem">Famille : ${scan.family || "?"} | Confiance : ${scan.confidence || 0}%</p>
        <div class="badges-row" style="padding:0;margin-bottom:1rem">
          <span class="badge ${badgeClass(scan.is_edible)}"><svg class="ic"><use href="#ic-bowl"/></svg> Comestible : ${scan.is_edible || "?"}</span>
          <span class="badge ${badgeClass(scan.is_medicinal)}"><svg class="ic"><use href="#ic-mortar"/></svg> Médicinal : ${scan.is_medicinal || "?"}</span>
          <span class="badge ${badgeClass(scan.is_toxic)}"><svg class="ic"><use href="#ic-mushroom"/></svg> Toxique : ${scan.is_toxic || "?"}</span>
          <span class="badge ${badgeClass(scan.is_invasive)}"><svg class="ic"><use href="#ic-globe"/></svg> Invasif : ${scan.is_invasive || "?"}</span>
        </div>
        <div class="result-section" style="margin-bottom:0.75rem"><h3><svg class="ic"><use href="#ic-heart"/></svg> Santé</h3><p>${report.health_status || scan.health_status || "N/A"}</p></div>
        <div class="result-section" style="margin-bottom:0.75rem"><h3><svg class="ic"><use href="#ic-bowl"/></svg> Comestibilité</h3><p>${report.edible_details || "N/A"}</p></div>
        <div class="result-section" style="margin-bottom:0.75rem"><h3><svg class="ic"><use href="#ic-mortar"/></svg> Médicinal</h3><p>${report.medicinal_details || "N/A"}</p></div>
        <div class="result-section" style="margin-bottom:0.75rem"><h3><svg class="ic"><use href="#ic-mushroom"/></svg> Toxicité</h3><p>${report.toxic_details || "N/A"}</p></div>
        <div class="result-section"><h3><svg class="ic"><use href="#ic-globe"/></svg> Environnement</h3><p>${report.environmental_impact || "N/A"}</p></div>
        <p style="color:var(--text-muted);font-size:0.8rem;margin-top:1rem">Scanné le ${formatDate(scan.created_at)}</p>
      </div>
    </div>`;
  modal.addEventListener("click", e => { if (e.target === modal) modal.remove(); });
  document.body.appendChild(modal);
}

window.openScanModal = openScanModal;
