// 백엔드 API를 호출하고 그 결과를 화면에 보여주는 코드.
//
// 흐름: 화면 → fetch 요청 → 백엔드(FastAPI) → JSON 응답 → 화면 갱신

// 주소 뒤에 ?api=... 가 있으면 그 값을, 없으면 config.js 의 값을 쓴다.
const API_URL = (
  new URLSearchParams(location.search).get("api") || window.API_BASE_URL || ""
).replace(/\/+$/, "");   // 끝의 / 는 제거해 //entries 같은 주소가 되지 않게 한다

const $ = (id) => document.getElementById(id);

$("api-url").textContent = API_URL || "(설정되지 않음)";
$("docs-link").href = API_URL + "/docs";

// 서버는 시각을 UTC로 저장한다. 표준시 표시(Z, +09:00 등)가 없는 문자열이면
// UTC라는 뜻이므로 Z를 붙여, 브라우저가 한국 시간으로 바꿔 보여주게 한다.
function toLocalTime(iso) {
  const hasZone = /[Zz]$|[+-]\d{2}:\d{2}$/.test(iso);
  return new Date(hasZone ? iso : iso + "Z").toLocaleString("ko-KR");
}

// 요소 하나를 만들어 클래스와 글자를 채운다.
function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

// ── ① 서버 생존 확인 GET /health ─────────────────────────────────
async function checkHealth() {
  const badge = $("api-status");
  try {
    const res = await fetch(`${API_URL}/health`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    badge.textContent = `연결됨 (${data.status})`;
    badge.className = "badge ok";
  } catch (err) {
    badge.textContent = `연결 실패 — ${err.message}`;
    badge.className = "badge fail";
  }
}

// ── ② 소개 정보 GET /profile ─────────────────────────────────────
async function loadProfile() {
  const box = $("profile-view");
  try {
    const res = await fetch(`${API_URL}/profile`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const p = await res.json();

    const rows = [
      ["이름", p.name],
      ["전공", p.title],
      ["소속", p.organization],
      ["소개", p.summary],
      ["관심분야", (p.interests || []).join(", ")],
    ];
    box.replaceChildren(
      ...rows.flatMap(([label, value]) => [el("dt", null, label), el("dd", null, value)])
    );
  } catch (err) {
    box.replaceChildren(el("div", "error", `소개 정보를 불러오지 못했습니다 — ${err.message}`));
  }
}

// ── ③ 방명록 목록 GET /entries ───────────────────────────────────
async function loadEntries() {
  const list = $("entry-list");
  try {
    const res = await fetch(`${API_URL}/entries`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const entries = await res.json();

    if (entries.length === 0) {
      list.replaceChildren(el("li", "muted", "아직 남겨진 글이 없습니다. 첫 글을 남겨보세요."));
      return;
    }

    list.replaceChildren(...entries.map((entry) => {
      const body = el("div");
      body.append(
        el("strong", null, entry.name),
        el("span", "when", toLocalTime(entry.created_at)),
        el("p", null, entry.message),
      );

      const del = el("button", "del", "삭제");
      del.type = "button";
      del.addEventListener("click", () => deleteEntry(entry.id));

      const li = el("li", "entry");
      li.append(body, del);
      return li;
    }));
  } catch (err) {
    list.replaceChildren(el("li", "error", `목록을 불러오지 못했습니다 — ${err.message}`));
  }
}

// ── ④ 등록 POST /entries ─────────────────────────────────────────
$("entry-form").addEventListener("submit", async (e) => {
  e.preventDefault();

  const name = $("entry-name").value.trim();
  const message = $("entry-message").value.trim();
  const errorBox = $("form-error");
  errorBox.hidden = true;

  if (!name || !message) return;

  const btn = $("submit-btn");
  btn.disabled = true;
  btn.textContent = "등록 중…";

  try {
    const res = await fetch(`${API_URL}/entries`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, message }),   // JS 객체 → JSON 문자열
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);

    $("entry-name").value = "";
    $("entry-message").value = "";
    await loadEntries();          // 저장 결과를 서버에서 다시 받아 화면을 맞춘다
  } catch (err) {
    errorBox.textContent = `등록에 실패했습니다 — ${err.message}`;
    errorBox.hidden = false;
  } finally {
    btn.disabled = false;
    btn.textContent = "등록";
  }
});

// ── ⑤ 삭제 DELETE /entries/{id} ──────────────────────────────────
async function deleteEntry(id) {
  if (!confirm("이 글을 삭제할까요?")) return;

  const errorBox = $("form-error");
  errorBox.hidden = true;
  try {
    const res = await fetch(`${API_URL}/entries/${id}`, { method: "DELETE" });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    await loadEntries();
  } catch (err) {
    errorBox.textContent = `삭제에 실패했습니다 — ${err.message}`;
    errorBox.hidden = false;
  }
}

// 페이지가 열리면 세 가지를 한꺼번에 호출한다.
checkHealth();
loadProfile();
loadEntries();
