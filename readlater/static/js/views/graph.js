import { API } from "../api.js";

let animFrame = null;

export function mount(root) {
  if (animFrame) { cancelAnimationFrame(animFrame); animFrame = null; }
  root.innerHTML = '<div id="graph-canvas-wrap"></div><div id="graph-tooltip"></div>';
  const wrap = root.querySelector("#graph-canvas-wrap");
  const tooltip = root.querySelector("#graph-tooltip");

  API.graphData(false).then((data) => {
    if (!data.nodes.length) {
      wrap.innerHTML = '<p class="empty-state" style="padding-top:80px">No bookmarks to graph yet.</p>';
      return;
    }
    initScene(wrap, tooltip, data);
  });
}

function forceLayout(nodes, edges, iterations = 150) {
  const k = Math.sqrt((800 * 600) / (nodes.length || 1));
  nodes.forEach((n, i) => {
    n.x = Math.cos((i / nodes.length) * Math.PI * 2) * 200;
    n.y = Math.sin((i / nodes.length) * Math.PI * 2) * 200;
    n.z = (Math.random() - 0.5) * 100;
    n.vx = n.vy = n.vz = 0;
  });

  const idxMap = {};
  nodes.forEach((n, i) => { idxMap[n.id] = i; });

  for (let iter = 0; iter < iterations; iter++) {
    const temp = k * (1 - iter / iterations);

    // Repulsion
    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        const dx = nodes[i].x - nodes[j].x;
        const dy = nodes[i].y - nodes[j].y;
        const dist = Math.sqrt(dx * dx + dy * dy) || 0.01;
        const force = (k * k) / dist;
        const fx = (dx / dist) * force;
        const fy = (dy / dist) * force;
        nodes[i].vx += fx; nodes[i].vy += fy;
        nodes[j].vx -= fx; nodes[j].vy -= fy;
      }
    }

    // Attraction
    edges.forEach((e) => {
      const a = nodes[idxMap[e.source]];
      const b = nodes[idxMap[e.target]];
      if (!a || !b) return;
      const dx = b.x - a.x;
      const dy = b.y - a.y;
      const dist = Math.sqrt(dx * dx + dy * dy) || 0.01;
      const force = (dist * dist) / k;
      const fx = (dx / dist) * force;
      const fy = (dy / dist) * force;
      a.vx += fx; a.vy += fy;
      b.vx -= fx; b.vy -= fy;
    });

    nodes.forEach((n) => {
      const speed = Math.sqrt(n.vx * n.vx + n.vy * n.vy) || 1;
      const capped = Math.min(speed, temp);
      n.x += (n.vx / speed) * capped;
      n.y += (n.vy / speed) * capped;
      n.vx = n.vy = 0;
    });
  }
}

async function initScene(wrap, tooltip, data) {
  // Dynamically load Three.js — fall back gracefully if not available
  let THREE, OrbitControls;
  try {
    THREE = await import("/static/js/vendor/three.module.min.js");
    const oc = await import("/static/js/vendor/OrbitControls.js");
    OrbitControls = oc.OrbitControls;
  } catch {
    wrap.innerHTML = '<p class="empty-state" style="padding-top:80px">Three.js not found. Run: <code>npm run vendor</code></p>';
    return;
  }

  const { nodes, edges } = data;
  forceLayout(nodes, edges);

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x0f1117);

  const w = wrap.clientWidth || window.innerWidth;
  const h = wrap.clientHeight || (window.innerHeight - 56);
  const camera = new THREE.PerspectiveCamera(60, w / h, 0.1, 5000);
  camera.position.set(0, 0, 400);

  const renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setPixelRatio(window.devicePixelRatio);
  renderer.setSize(w, h);
  wrap.appendChild(renderer.domElement);

  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;

  // Ambient + directional light
  scene.add(new THREE.AmbientLight(0xffffff, 0.6));
  const dir = new THREE.DirectionalLight(0xffffff, 0.8);
  dir.position.set(1, 2, 3);
  scene.add(dir);

  // Nodes
  const meshes = [];
  const nodeMats = {
    unread: new THREE.MeshStandardMaterial({ color: 0x6366f1 }),
    read: new THREE.MeshStandardMaterial({ color: 0x4b5563 }),
  };

  nodes.forEach((n) => {
    const r = 5 + Math.min(n.tags.length * 1.5, 8);
    const geo = new THREE.SphereGeometry(r, 24, 24);
    const mesh = new THREE.Mesh(geo, n.is_read ? nodeMats.read : nodeMats.unread);
    mesh.position.set(n.x, n.y, n.z || 0);
    mesh.userData = n;
    scene.add(mesh);
    meshes.push(mesh);
  });

  // Edges as a single LineSegments
  const edgePositions = [];
  const idxMap = {};
  nodes.forEach((n, i) => { idxMap[n.id] = i; });

  edges.forEach((e) => {
    const a = nodes[idxMap[e.source]];
    const b = nodes[idxMap[e.target]];
    if (!a || !b) return;
    edgePositions.push(a.x, a.y, a.z || 0, b.x, b.y, b.z || 0);
  });

  if (edgePositions.length) {
    const edgeGeo = new THREE.BufferGeometry();
    edgeGeo.setAttribute("position", new THREE.Float32BufferAttribute(edgePositions, 3));
    const edgeMat = new THREE.LineBasicMaterial({ color: 0x2a2d3e, transparent: true, opacity: 0.5 });
    scene.add(new THREE.LineSegments(edgeGeo, edgeMat));
  }

  // Raycasting
  const raycaster = new THREE.Raycaster();
  const mouse = new THREE.Vector2();
  let hoveredMesh = null;

  renderer.domElement.addEventListener("mousemove", (e) => {
    const rect = renderer.domElement.getBoundingClientRect();
    mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
    mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
    raycaster.setFromCamera(mouse, camera);
    const hits = raycaster.intersectObjects(meshes);
    if (hits.length) {
      const n = hits[0].object.userData;
      hoveredMesh = hits[0].object;
      tooltip.style.display = "block";
      tooltip.style.left = e.clientX + 12 + "px";
      tooltip.style.top = e.clientY + 12 + "px";
      tooltip.innerHTML = `<strong>${n.title || n.url}</strong><br/><small>${n.tags.join(", ") || "no tags"}</small>`;
      renderer.domElement.style.cursor = "pointer";
    } else {
      hoveredMesh = null;
      tooltip.style.display = "none";
      renderer.domElement.style.cursor = "";
    }
  });

  renderer.domElement.addEventListener("click", () => {
    if (hoveredMesh) {
      window.open(hoveredMesh.userData.url, "_blank", "noopener");
    }
  });

  // Resize
  window.addEventListener("resize", () => {
    const w2 = wrap.clientWidth;
    const h2 = wrap.clientHeight;
    camera.aspect = w2 / h2;
    camera.updateProjectionMatrix();
    renderer.setSize(w2, h2);
  });

  function animate() {
    animFrame = requestAnimationFrame(animate);
    controls.update();
    renderer.render(scene, camera);
  }
  animate();
}
