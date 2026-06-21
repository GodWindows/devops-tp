// API base: the frontend is served by the same FastAPI app, so we hit absolute
// paths from the origin root (e.g. "/persons"), independent of where the UI is mounted.
const API = "";

const output = document.getElementById("output");
const statusPill = document.getElementById("status-pill");

/** Perform a fetch and render the result in the console panel. */
async function call(method, path, body) {
  setStatus("…", "");
  output.textContent = `${method} ${path}\n\nRequête en cours…`;
  try {
    const opts = { method, headers: {} };
    if (body !== undefined) {
      opts.headers["Content-Type"] = "application/json";
      opts.body = JSON.stringify(body);
    }
    const res = await fetch(API + path, opts);
    const text = await res.text();
    let parsed;
    try { parsed = text ? JSON.parse(text) : null; } catch { parsed = text; }

    setStatus(`${res.status} ${res.statusText}`, statusClass(res.status));
    const pretty = parsed === null ? "(corps vide)" : JSON.stringify(parsed, null, 2);
    output.textContent = `${method} ${path}\n\n${pretty}`;
    return { ok: res.ok, status: res.status, data: parsed };
  } catch (err) {
    setStatus("Erreur réseau", "err");
    output.textContent = `${method} ${path}\n\n${err}`;
    return { ok: false, status: 0, data: null };
  }
}

function setStatus(label, cls) {
  statusPill.textContent = label;
  statusPill.className = "pill" + (cls ? " " + cls : "");
}

function statusClass(status) {
  if (status >= 200 && status < 300) return "ok";
  if (status >= 400 && status < 500) return "warn";
  return "err";
}

// ---------------------------------------------------------------- Tabs
document.querySelectorAll(".tab").forEach((tab) => {
  tab.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach((t) => t.classList.remove("active"));
    document.querySelectorAll(".panel").forEach((p) => p.classList.remove("active"));
    tab.classList.add("active");
    document.getElementById(tab.dataset.tab).classList.add("active");
  });
});

// ---------------------------------------------------------------- Greetings
document.getElementById("hello-world-btn").addEventListener("click", () =>
  call("GET", "/hello-world")
);
document.getElementById("languages-btn").addEventListener("click", () =>
  call("GET", "/greetings/languages")
);
document.getElementById("greeting-stats-btn").addEventListener("click", () =>
  call("GET", "/greetings/stats")
);

document.getElementById("greeting-form").addEventListener("submit", (e) => {
  e.preventDefault();
  const f = e.target;
  call("POST", "/greetings", {
    name: f.name.value,
    language: f.language.value,
    audience: f.audience.value,
    excited: f.excited.checked,
  });
});

// ---------------------------------------------------------------- Persons
const personForm = document.getElementById("person-form");
const personIdField = document.getElementById("person-id");
const personSubmit = document.getElementById("person-submit");

async function loadPersons() {
  const res = await call("GET", "/persons");
  const tbody = document.querySelector("#persons-table tbody");
  const empty = document.getElementById("persons-empty");
  tbody.innerHTML = "";
  if (!res.ok || !Array.isArray(res.data) || res.data.length === 0) {
    empty.classList.remove("hidden");
    return;
  }
  empty.classList.add("hidden");
  for (const p of res.data) {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${p.id}</td>
      <td>${escapeHtml(p.name)}</td>
      <td>${p.age}</td>
      <td>${escapeHtml(p.language)}</td>
      <td class="actions-col">
        <div class="row">
          <button data-act="greet" data-id="${p.id}" class="ghost">Saluer</button>
          <button data-act="edit" data-id="${p.id}" class="ghost">Éditer</button>
          <button data-act="delete" data-id="${p.id}" class="ghost">Suppr.</button>
        </div>
      </td>`;
    tr.querySelector('[data-act="greet"]').onclick = () => call("GET", `/persons/${p.id}/greet`);
    tr.querySelector('[data-act="edit"]').onclick = () => startEdit(p);
    tr.querySelector('[data-act="delete"]').onclick = async () => {
      await call("DELETE", `/persons/${p.id}`);
      loadPersons();
    };
    tbody.appendChild(tr);
  }
}

function startEdit(p) {
  personIdField.value = p.id;
  personForm.name.value = p.name;
  personForm.age.value = p.age;
  personForm.language.value = p.language;
  personSubmit.textContent = `Mettre à jour #${p.id}`;
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function resetForm() {
  personIdField.value = "";
  personForm.reset();
  personSubmit.textContent = "Créer";
}

personForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const id = personIdField.value;
  const payload = {
    name: personForm.name.value,
    age: Number(personForm.age.value),
    language: personForm.language.value,
  };
  if (id) {
    await call("PUT", `/persons/${id}`, payload);
  } else {
    await call("POST", "/persons", payload);
  }
  resetForm();
  loadPersons();
});

document.getElementById("person-reset").addEventListener("click", resetForm);
document.getElementById("person-refresh-btn").addEventListener("click", loadPersons);
document.getElementById("person-stats-btn").addEventListener("click", () =>
  call("GET", "/persons/stats")
);

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c])
  );
}

// Initial load (top-level await — app.js is loaded as an ES module)
await loadPersons();
