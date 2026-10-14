"use strict";
const $ = (id) => document.getElementById(id);
const csrf = document.querySelector('meta[name="csrf-token"]').content;
const statusNames = {
  COMPLETE: "Đã xử lý",
  PROCESSING: "Đang xử lý",
  REJECTED: "Ảnh không hợp lệ",
  FAILED: "Xử lý lỗi",
};
const bytes = (n) => `${(Number(n) / 1024).toFixed(1)} KiB`;
let loading = false;
let timer;
let pendingKeys = new Map();
function node(tag, text, className) {
  const el = document.createElement(tag);
  if (text !== undefined) el.textContent = text;
  if (className) el.className = className;
  return el;
}
function detail(item) {
  $("detail-title").textContent = item.filename;
  const area = $("detail-content");
  area.replaceChildren();
  const variants = [...item.variants].sort((a, b) => a.size - b.size);
  const img = node("img");
  img.src = variants[variants.length - 1].url;
  img.alt = item.filename;
  area.append(
    img,
    node(
      "p",
      `Ảnh gốc: ${item.original.width} × ${item.original.height} px · ${bytes(item.original.bytes)} · Xử lý: ${item.processing_ms} ms`,
    ),
  );
  const links = node("div", undefined, "variant-links");
  for (const v of variants) {
    const a = node(
      "a",
      `${v.size}px: ${v.width} × ${v.height} · ${bytes(v.bytes)}`,
    );
    a.href = v.url;
    a.target = "_blank";
    a.rel = "noopener noreferrer";
    links.append(a);
  }
  area.append(
    links,
    node(
      "p",
      "Liên kết ảnh có thời hạn. Nếu hết hạn, đóng hộp thoại rồi bấm Làm mới.",
      "muted",
    ),
  );
  $("detail").showModal();
}
async function refresh() {
  if (loading || document.hidden) return;
  loading = true;
  try {
    const response = await fetch("/api/photos");
    if (response.status === 401) {
      location.href = "/login";
      return;
    }
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Không tải được thư viện.");
    $("gallery").replaceChildren();
    $("count").textContent = data.items.length;
    for (const item of data.items) {
      if (["COMPLETE", "REJECTED", "FAILED"].includes(item.status))
        pendingKeys.delete(item.source_key);
      const card = node("article", undefined, "photo-card");
      if (item.status === "COMPLETE" && item.variants.length) {
        const preview =
          item.variants.find((v) => v.size === 400) || item.variants[0];
        const img = node("img");
        img.src = preview.url;
        img.alt = item.filename;
        img.loading = "lazy";
        card.append(img);
      } else
        card.append(
          node("div", item.status === "PROCESSING" ? "…" : "!", "placeholder"),
        );
      const body = node("div", undefined, "card-body");
      body.append(
        node(
          "span",
          statusNames[item.status] || item.status,
          `status ${item.status}`,
        ),
        node("h3", item.filename),
      );
      body.append(node("p", new Date(item.created_at).toLocaleString("vi-VN")));
      if (item.original)
        body.append(
          node(
            "p",
            `${item.original.width} × ${item.original.height} px · ${bytes(item.original.bytes)}`,
          ),
        );
      if (item.error) body.append(node("p", item.error));
      if (item.status === "COMPLETE") {
        const button = node("button", "Xem 3 phiên bản", "quiet");
        button.type = "button";
        button.addEventListener("click", () => detail(item));
        body.append(button);
      }
      card.append(body);
      $("gallery").append(card);
    }
    const stale = [...pendingKeys.values()].some(
      (t) => Date.now() - t > 120000,
    );
    $("gallery-note").textContent = stale
      ? "Ảnh chưa có kết quả sau 2 phút. Hãy thử làm mới hoặc liên hệ người quản lý."
      : pendingKeys.size
        ? `Đang chờ kết quả của ${pendingKeys.size} ảnh…`
        : data.truncated
          ? "Thư viện lớn: đang hiển thị 60 ảnh từ tập dữ liệu đã tải."
          : data.items.length
            ? "Hiển thị tối đa 60 ảnh gần nhất. Tự làm mới mỗi 30 giây, hoặc 5 giây khi đang xử lý."
            : "Chưa có ảnh. Tải ảnh đầu tiên để bắt đầu.";
    clearTimeout(timer);
    const busy =
      pendingKeys.size || data.items.some((x) => x.status === "PROCESSING");
    timer = setTimeout(refresh, busy ? 5000 : 30000);
  } catch (error) {
    $("gallery-note").textContent = error.message;
    clearTimeout(timer);
    timer = setTimeout(refresh, 30000);
  } finally {
    loading = false;
  }
}
$("file").addEventListener("change", () => {
  $("selected-name").textContent = $("file").files[0]?.name || "Chưa chọn ảnh";
});
$("upload-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const file = $("file").files[0];
  if (!file) return;
  $("message").className = "";
  if (file.size > 10 * 1024 * 1024) {
    $("message").textContent = "Ảnh vượt quá 10 MiB.";
    return;
  }
  $("upload-button").disabled = true;
  $("message").textContent = "Đang tải ảnh…";
  try {
    const body = new FormData();
    body.append("file", file);
    const response = await fetch("/api/upload", {
      method: "POST",
      headers: { "X-CSRF-Token": csrf },
      body,
    });
    if (response.status === 401) {
      location.href = "/login";
      return;
    }
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Upload thất bại.");
    pendingKeys.set(data.source_key, Date.now());
    $("message").textContent = data.message;
    $("upload-form").reset();
    $("selected-name").textContent = "Chưa chọn ảnh";
    await refresh();
  } catch (error) {
    $("message").textContent = error.message;
    $("message").className = "error";
  } finally {
    $("upload-button").disabled = false;
  }
});
const zone = $("drop-zone");
for (const event of ["dragenter", "dragover"])
  zone.addEventListener(event, (e) => {
    e.preventDefault();
    zone.classList.add("dragging");
  });
for (const event of ["dragleave", "drop"])
  zone.addEventListener(event, (e) => {
    e.preventDefault();
    zone.classList.remove("dragging");
  });
zone.addEventListener("drop", (e) => {
  if (e.dataTransfer.files.length !== 1) {
    $("message").textContent = "Mỗi lần chọn một ảnh.";
    return;
  }
  $("file").files = e.dataTransfer.files;
  $("file").dispatchEvent(new Event("change"));
});
$("refresh").addEventListener("click", refresh);
$("close-detail").addEventListener("click", () => $("detail").close());
document.addEventListener("visibilitychange", () => {
  if (!document.hidden) refresh();
});
refresh();
