import { API } from "../api.js";
import { renderCard } from "../components/bookmarkCard.js";

const PAGE_SIZE = 20;
let container = null;
let listEl = null;
let offset = 0;
let total = 0;
let currentState = {};

export function mount(root, state) {
  currentState = state;
  offset = 0;
  container = document.createElement("div");
  root.innerHTML = "";
  root.appendChild(container);
  load(true);
}

export function refresh(state) {
  currentState = state;
  offset = 0;
  load(true);
}

async function load(reset) {
  if (reset) {
    container.innerHTML = '<div class="spinner">Loading…</div>';
  }

  try {
    const params = {
      limit: PAGE_SIZE,
      offset: reset ? 0 : offset,
      is_archived: false,
    };
    if (currentState.searchQuery) params.q = currentState.searchQuery;
    if (currentState.filterTags?.length) params.tags = currentState.filterTags.join(",");

    const data = await API.listBookmarks(params);
    total = data.total;

    if (reset) {
      offset = 0;
      container.innerHTML = "";
      listEl = document.createElement("div");
      listEl.className = "bookmark-list";
      container.appendChild(listEl);
    }

    if (total === 0) {
      listEl.innerHTML = '<p class="empty-state">No bookmarks yet. Add one!</p>';
      return;
    }

    data.items.forEach((b) => listEl.appendChild(renderCard(b, onTagClick, onAction)));
    offset += data.items.length;

    // Remove old load-more if present
    container.querySelector(".load-more-btn")?.remove();

    if (offset < total) {
      const btn = document.createElement("button");
      btn.className = "load-more-btn";
      btn.textContent = `Load more (${total - offset} remaining)`;
      btn.addEventListener("click", () => { btn.remove(); load(false); });
      container.appendChild(btn);
    }
  } catch {
    container.innerHTML = '<p class="empty-state">Failed to load bookmarks. Please try again.</p>';
  }
}

function onTagClick(slug) {
  currentState.filterTags = currentState.filterTags ?? [];
  const idx = currentState.filterTags.indexOf(slug);
  if (idx === -1) currentState.filterTags.push(slug);
  else currentState.filterTags.splice(idx, 1);
  offset = 0;
  load(true);
}

async function onAction(action, bookmark) {
  if (action === "read") {
    await API.patchBookmark(bookmark.id, { is_read: !bookmark.is_read });
  } else if (action === "archive") {
    await API.patchBookmark(bookmark.id, { is_archived: true });
  } else if (action === "delete") {
    if (!confirm("Delete this bookmark?")) return;
    await API.deleteBookmark(bookmark.id);
  }
  offset = 0;
  load(true);
}
