const BASE = "";

async function request(method, path, body, params) {
  let url = BASE + path;
  if (params) {
    const q = new URLSearchParams(Object.entries(params).filter(([, v]) => v != null && v !== ""));
    if ([...q].length) url += "?" + q.toString();
  }
  const opts = { method, headers: {} };
  if (body !== undefined) {
    opts.headers["Content-Type"] = "application/json";
    opts.body = JSON.stringify(body);
  }
  const res = await fetch(url, opts);
  if (res.status === 204) return null;
  const data = await res.json();
  if (!res.ok) throw Object.assign(new Error(data.detail || "Request failed"), { status: res.status });
  return data;
}

export const API = {
  listBookmarks: (p) => request("GET", "/api/bookmarks", undefined, p),
  createBookmark: (url) => request("POST", "/api/bookmarks", { url }),
  getBookmark: (id) => request("GET", `/api/bookmarks/${id}`),
  patchBookmark: (id, data) => request("PATCH", `/api/bookmarks/${id}`, data),
  deleteBookmark: (id) => request("DELETE", `/api/bookmarks/${id}`),
  listTags: () => request("GET", "/api/tags"),
  createTag: (name) => request("POST", "/api/tags", { name }),
  deleteTag: (id) => request("DELETE", `/api/tags/${id}`),
  search: (q, limit = 20, offset = 0) => request("GET", "/api/search", undefined, { q, limit, offset }),
  graphData: (is_archived = false) => request("GET", "/api/bookmarks/graph", undefined, { is_archived }),
};
