import { API } from "./api.js";

const root = document.getElementById("view-root");
const searchInput = document.getElementById("search-input");
const addBtn = document.getElementById("add-btn");
const modal = document.getElementById("bookmark-modal");
const modalForm = document.getElementById("bookmark-form");
const modalUrl = document.getElementById("modal-url");
const modalCancel = document.getElementById("modal-cancel");

let currentView = null;
let searchTimer = null;

export const state = {
  filterTags: [],
  searchQuery: "",
};

function setActiveNav(view) {
  document.querySelectorAll(".nav-link").forEach((a) => {
    a.classList.toggle("active", a.dataset.view === view);
  });
}

async function loadView(hash) {
  const view = hash === "#graph" ? "graph" : "list";
  setActiveNav(view);

  if (view === "graph") {
    root.className = "graph-mode";
    const mod = await import("./views/graph.js");
    currentView = mod;
    mod.mount(root);
  } else {
    root.className = "";
    const mod = await import("./views/list.js");
    currentView = mod;
    mod.mount(root, state);
  }
}

window.addEventListener("hashchange", () => loadView(location.hash));

searchInput.addEventListener("input", (e) => {
  clearTimeout(searchTimer);
  state.searchQuery = e.target.value.trim();
  searchTimer = setTimeout(() => {
    if (location.hash !== "#graph" && currentView?.refresh) {
      currentView.refresh(state);
    }
  }, 300);
});

addBtn.addEventListener("click", () => {
  modalUrl.value = "";
  modal.showModal();
  modalUrl.focus();
});

modalCancel.addEventListener("click", () => modal.close());

modalForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const url = modalUrl.value.trim();
  if (!url) return;
  try {
    await API.createBookmark(url);
    modal.close();
    if (currentView?.refresh) currentView.refresh(state);
  } catch (err) {
    alert(err.message);
  }
});

loadView(location.hash || "#list");
