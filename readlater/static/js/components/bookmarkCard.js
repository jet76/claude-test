export function renderCard(bookmark, onTagClick, onAction) {
  const card = document.createElement("div");
  card.className = "bookmark-card" + (bookmark.is_read ? " is-read" : "");
  card.dataset.id = bookmark.id;

  const favicon = document.createElement("img");
  favicon.className = "favicon";
  favicon.src = bookmark.favicon_url || "";
  favicon.alt = "";
  favicon.onerror = () => { favicon.style.display = "none"; };

  const body = document.createElement("div");
  body.className = "card-body";

  const titleEl = document.createElement("div");
  titleEl.className = "card-title";
  const link = document.createElement("a");
  link.href = bookmark.url;
  link.target = "_blank";
  link.rel = "noopener";
  link.textContent = bookmark.title || bookmark.url;
  titleEl.appendChild(link);

  const urlEl = document.createElement("div");
  urlEl.className = "card-url";
  urlEl.textContent = bookmark.url;

  const descEl = document.createElement("div");
  descEl.className = "card-desc";
  descEl.textContent = bookmark.description || "";

  const tagsEl = document.createElement("div");
  tagsEl.className = "card-tags";
  (bookmark.tags || []).forEach((tag) => {
    const pill = document.createElement("span");
    pill.className = "tag-pill";
    pill.textContent = tag.name;
    pill.addEventListener("click", () => onTagClick(tag.slug));
    tagsEl.appendChild(pill);
  });

  body.append(titleEl, urlEl, descEl, tagsEl);

  const actions = document.createElement("div");
  actions.className = "card-actions";

  const readBtn = document.createElement("button");
  readBtn.className = "card-action-btn";
  readBtn.textContent = bookmark.is_read ? "Unread" : "Mark read";
  readBtn.addEventListener("click", () => onAction("read", bookmark));

  const archiveBtn = document.createElement("button");
  archiveBtn.className = "card-action-btn";
  archiveBtn.textContent = "Archive";
  archiveBtn.addEventListener("click", () => onAction("archive", bookmark));

  const deleteBtn = document.createElement("button");
  deleteBtn.className = "card-action-btn danger";
  deleteBtn.textContent = "Delete";
  deleteBtn.addEventListener("click", () => onAction("delete", bookmark));

  actions.append(readBtn, archiveBtn, deleteBtn);
  card.append(favicon, body, actions);
  return card;
}
