import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";

const here = dirname(fileURLToPath(import.meta.url));
const html = readFileSync(resolve(here, "../../frontend/index.html"), "utf-8");
// Use the real markup so every querySelector in app.js resolves, but drop the
// <script> tag — we import the module ourselves with a mocked fetch.
const bodyHtml = html.match(/<body>([\s\S]*)<\/body>/)[1].replace(/<script[\s\S]*?<\/script>/g, "");

const flush = () => new Promise((r) => setTimeout(r, 0));

function jsonResponse(data, { ok = true, status = 200, statusText = "OK" } = {}) {
  return {
    ok,
    status,
    statusText,
    text: async () => (data === undefined ? "" : JSON.stringify(data)),
  };
}

/** Default router: empty person list, generic OK for everything else. */
function defaultFetch(url, opts = {}) {
  const method = opts.method || "GET";
  if (url === "/persons" && method === "GET") return Promise.resolve(jsonResponse([]));
  return Promise.resolve(jsonResponse({}));
}

/** Reset the DOM + fetch mock, then (re)import app.js so its top-level code runs. */
async function loadApp(fetchImpl = defaultFetch) {
  document.body.innerHTML = bodyHtml;
  global.fetch = vi.fn(fetchImpl);
  vi.resetModules();
  const mod = await import("../../frontend/app.js");
  await flush();
  return mod;
}

function fetchCalls() {
  return global.fetch.mock.calls.map(([url, opts = {}]) => ({ url, method: opts.method || "GET", opts }));
}

afterEach(() => {
  vi.restoreAllMocks();
});

describe("pure helpers", () => {
  it("statusClass maps HTTP status to a css class", async () => {
    const { statusClass } = await loadApp();
    expect(statusClass(200)).toBe("ok");
    expect(statusClass(204)).toBe("ok");
    expect(statusClass(400)).toBe("warn");
    expect(statusClass(404)).toBe("warn");
    expect(statusClass(500)).toBe("err");
  });

  it("escapeHtml neutralises HTML-special characters", async () => {
    const { escapeHtml } = await loadApp();
    expect(escapeHtml(`<b>&"'`)).toBe("&lt;b&gt;&amp;&quot;&#39;");
    expect(escapeHtml(42)).toBe("42");
  });
});

describe("initial load", () => {
  it("shows the empty state when there are no persons", async () => {
    await loadApp();
    expect(fetchCalls()[0]).toMatchObject({ url: "/persons", method: "GET" });
    expect(document.getElementById("persons-empty").classList.contains("hidden")).toBe(false);
    expect(document.querySelectorAll("#persons-table tbody tr").length).toBe(0);
  });

  it("renders a row per person and escapes user content", async () => {
    await loadApp((url, opts) =>
      url === "/persons" && (!opts || opts.method === undefined || opts.method === "GET")
        ? Promise.resolve(jsonResponse([{ id: 1, name: "<script>", age: 30, language: "fr" }]))
        : defaultFetch(url, opts)
    );

    const rows = document.querySelectorAll("#persons-table tbody tr");
    expect(rows.length).toBe(1);
    expect(document.getElementById("persons-empty").classList.contains("hidden")).toBe(true);
    // name cell is escaped, not interpreted as a tag
    expect(rows[0].children[1].innerHTML).toBe("&lt;script&gt;");
  });
});

describe("tab navigation", () => {
  it("activates the persons panel when its tab is clicked", async () => {
    await loadApp();
    document.querySelector('.tab[data-tab="persons"]').click();
    expect(document.getElementById("persons").classList.contains("active")).toBe(true);
    expect(document.getElementById("greetings").classList.contains("active")).toBe(false);
  });
});

describe("greeting actions", () => {
  it("hello-world button calls GET /hello-world and renders an ok status", async () => {
    await loadApp((url) =>
      url === "/hello-world"
        ? Promise.resolve(jsonResponse({ message: "Hello World." }))
        : defaultFetch(url)
    );

    document.getElementById("hello-world-btn").click();
    await flush();

    expect(fetchCalls().some((c) => c.url === "/hello-world" && c.method === "GET")).toBe(true);
    expect(document.getElementById("status-pill").classList.contains("ok")).toBe(true);
    expect(document.getElementById("output").textContent).toContain("Hello World.");
  });

  it("submitting the greeting form POSTs the serialised payload", async () => {
    await loadApp((url, opts) =>
      url === "/greetings" && opts.method === "POST"
        ? Promise.resolve(jsonResponse({ message: "Salut Bob!" }))
        : defaultFetch(url, opts)
    );

    const form = document.getElementById("greeting-form");
    form.querySelector('[name="name"]').value = "Bob";
    form.querySelector('[name="language"]').value = "fr";
    form.querySelector('[name="audience"]').value = "casual";
    form.querySelector('[name="excited"]').checked = true;
    form.dispatchEvent(new Event("submit", { cancelable: true, bubbles: true }));
    await flush();

    const post = fetchCalls().find((c) => c.url === "/greetings" && c.method === "POST");
    expect(post).toBeTruthy();
    expect(JSON.parse(post.opts.body)).toEqual({
      name: "Bob",
      language: "fr",
      audience: "casual",
      excited: true,
    });
  });

  it("the languages and stats buttons hit their endpoints", async () => {
    await loadApp();
    document.getElementById("languages-btn").click();
    document.getElementById("greeting-stats-btn").click();
    await flush();

    const urls = fetchCalls().map((c) => c.url);
    expect(urls).toContain("/greetings/languages");
    expect(urls).toContain("/greetings/stats");
  });
});

describe("person actions", () => {
  it("creating a person POSTs then reloads the list", async () => {
    await loadApp((url, opts) =>
      url === "/persons" && opts.method === "POST"
        ? Promise.resolve(jsonResponse({ id: 1, name: "Alice", age: 30, language: "fr" }, { status: 201 }))
        : defaultFetch(url, opts)
    );

    const form = document.getElementById("person-form");
    form.querySelector('[name="name"]').value = "Alice";
    form.querySelector('[name="age"]').value = "30";
    form.querySelector('[name="language"]').value = "fr";
    form.dispatchEvent(new Event("submit", { cancelable: true, bubbles: true }));
    await flush();

    const post = fetchCalls().find((c) => c.url === "/persons" && c.method === "POST");
    expect(JSON.parse(post.opts.body)).toEqual({ name: "Alice", age: 30, language: "fr" });
    // a GET /persons reload happens after the POST
    expect(fetchCalls().filter((c) => c.url === "/persons" && c.method === "GET").length).toBeGreaterThanOrEqual(2);
    // form is reset
    expect(document.getElementById("person-submit").textContent).toBe("Créer");
  });

  it("editing prefills the form and submits a PUT", async () => {
    await loadApp((url, opts) =>
      url === "/persons" && (!opts.method || opts.method === "GET")
        ? Promise.resolve(jsonResponse([{ id: 7, name: "Bob", age: 45, language: "en" }]))
        : defaultFetch(url, opts)
    );

    document.querySelector('#persons-table [data-act="edit"]').click();
    const form = document.getElementById("person-form");
    expect(form.querySelector('[name="name"]').value).toBe("Bob");
    expect(document.getElementById("person-id").value).toBe("7");
    expect(document.getElementById("person-submit").textContent).toContain("#7");

    form.querySelector('[name="age"]').value = "46";
    form.dispatchEvent(new Event("submit", { cancelable: true, bubbles: true }));
    await flush();

    const put = fetchCalls().find((c) => c.method === "PUT");
    expect(put.url).toBe("/persons/7");
    expect(JSON.parse(put.opts.body).age).toBe(46);
  });

  it("the cancel button clears an in-progress edit", async () => {
    await loadApp((url, opts) =>
      url === "/persons" && (!opts.method || opts.method === "GET")
        ? Promise.resolve(jsonResponse([{ id: 7, name: "Bob", age: 45, language: "en" }]))
        : defaultFetch(url, opts)
    );

    document.querySelector('#persons-table [data-act="edit"]').click();
    expect(document.getElementById("person-id").value).toBe("7");

    document.getElementById("person-reset").click();
    expect(document.getElementById("person-id").value).toBe("");
    expect(document.getElementById("person-submit").textContent).toBe("Créer");
  });

  it("deleting a person sends DELETE then reloads", async () => {
    await loadApp((url, opts) =>
      url === "/persons" && (!opts.method || opts.method === "GET")
        ? Promise.resolve(jsonResponse([{ id: 3, name: "Carlos", age: 50, language: "es" }]))
        : defaultFetch(url, opts)
    );

    document.querySelector('#persons-table [data-act="delete"]').click();
    await flush();

    expect(fetchCalls().some((c) => c.url === "/persons/3" && c.method === "DELETE")).toBe(true);
  });

  it("the greet button calls the greet endpoint", async () => {
    await loadApp((url, opts) =>
      url === "/persons" && (!opts.method || opts.method === "GET")
        ? Promise.resolve(jsonResponse([{ id: 9, name: "Dora", age: 30, language: "fr" }]))
        : defaultFetch(url, opts)
    );

    document.querySelector('#persons-table [data-act="greet"]').click();
    await flush();

    expect(fetchCalls().some((c) => c.url === "/persons/9/greet")).toBe(true);
  });

  it("the refresh and stats buttons hit their endpoints", async () => {
    await loadApp();
    document.getElementById("person-refresh-btn").click();
    document.getElementById("person-stats-btn").click();
    await flush();

    expect(fetchCalls().some((c) => c.url === "/persons/stats")).toBe(true);
  });
});

describe("response rendering", () => {
  it("renders a warn status and detail for a 4xx response", async () => {
    await loadApp((url) =>
      url === "/greetings/stats"
        ? Promise.resolve(jsonResponse({ detail: "nope" }, { ok: false, status: 400, statusText: "Bad Request" }))
        : defaultFetch(url)
    );

    document.getElementById("greeting-stats-btn").click();
    await flush();

    expect(document.getElementById("status-pill").classList.contains("warn")).toBe(true);
    expect(document.getElementById("output").textContent).toContain("nope");
  });

  it("shows raw text when the body is not JSON", async () => {
    await loadApp((url) =>
      url === "/hello-world"
        ? Promise.resolve({ ok: true, status: 200, statusText: "OK", text: async () => "plain text" })
        : defaultFetch(url)
    );

    document.getElementById("hello-world-btn").click();
    await flush();

    expect(document.getElementById("output").textContent).toContain("plain text");
  });

  it("shows '(corps vide)' for an empty response body", async () => {
    await loadApp((url) =>
      url === "/hello-world"
        ? Promise.resolve(jsonResponse(undefined, { status: 204, statusText: "No Content" }))
        : defaultFetch(url)
    );

    document.getElementById("hello-world-btn").click();
    await flush();

    expect(document.getElementById("output").textContent).toContain("(corps vide)");
  });

  it("reports a network error when fetch rejects", async () => {
    await loadApp((url) =>
      url === "/hello-world" ? Promise.reject(new Error("boom")) : defaultFetch(url)
    );

    document.getElementById("hello-world-btn").click();
    await flush();

    expect(document.getElementById("status-pill").classList.contains("err")).toBe(true);
    expect(document.getElementById("output").textContent).toContain("boom");
  });
});
