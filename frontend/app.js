/* =====================================================
   Swift-Prep – App JavaScript
   Faceted Polygon Canvas · Interactive Controls
   ===================================================== */

const API_BASE = 'http://127.0.0.1:8000';

// ── Toast Notification Helper ──
function showToast(message, duration = 3000) {
  const toast = document.getElementById('toast');
  if (!toast) return;
  toast.textContent = message;
  toast.classList.add('show');
  clearTimeout(toast._timeout);
  toast._timeout = setTimeout(() => {
    toast.classList.remove('show');
  }, duration);
}

// ── Smart Dynamic Greeting ──
(function initGreeting() {
  const h = new Date().getHours();
  const greetingEl = document.getElementById('greeting-h1');
  const subEl = document.getElementById('greeting-p');

  if (!greetingEl) return;

  if (h >= 5 && h < 12) {
    greetingEl.textContent = 'Good morning, there! ☀️';
    subEl.textContent = "Rise and grind — that syllabus isn't going to read itself, apparently.";
  } else if (h >= 12 && h < 17) {
    greetingEl.textContent = 'Good afternoon, there! 👋';
    subEl.textContent = "Ah, we meet again. That syllabus isn't going to read itself, apparently.";
  } else if (h >= 17 && h < 22) {
    greetingEl.textContent = 'Good evening, there! 👋';
    subEl.textContent = "Ah, we meet again. That syllabus isn't going to read itself, apparently.";
  } else {
    greetingEl.textContent = 'Burning midnight oil! 🌙';
    subEl.textContent = "Night cram mode activated. That syllabus isn't going to read itself, apparently.";
  }
})();

// ── Low-Poly Faceted Geometric Polygon Background ──
(function initPolygonBackground() {
  const canvas = document.getElementById('bg-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  let width, height;
  let points = [];
  let triangles = [];

  // Dark deep navy facet shades matching Swift-Prep screenshot
  const FACET_COLORS = [
    [7, 18, 42],    // #07122a
    [10, 24, 54],   // #0a1836
    [13, 31, 68],   // #0d1f44
    [16, 38, 82],   // #102652
    [9, 21, 48],    // #091530
    [18, 44, 96],   // #122c60
    [6, 15, 34],    // #060f22
    [14, 33, 72],   // #0e2148
  ];

  function resize() {
    width = canvas.width = window.innerWidth;
    height = canvas.height = window.innerHeight;
    generateMesh();
  }

  function generateMesh() {
    // Generate jittered grid of points
    const spacing = 180;
    const cols = Math.ceil(width / spacing) + 2;
    const rows = Math.ceil(height / spacing) + 2;
    points = [];

    for (let r = 0; r <= rows; r++) {
      for (let c = 0; c <= cols; c++) {
        const baseX = (c - 0.5) * spacing;
        const baseY = (r - 0.5) * spacing;
        // Jitter interior points
        const jitterX = (Math.random() - 0.5) * spacing * 0.75;
        const jitterY = (Math.random() - 0.5) * spacing * 0.75;
        points.push({
          x: baseX + jitterX,
          y: baseY + jitterY,
          originX: baseX,
          originY: baseY,
          vx: (Math.random() - 0.5) * 0.15,
          vy: (Math.random() - 0.5) * 0.15,
          r, c
        });
      }
    }

    // Build triangular facets (2 per grid quad)
    triangles = [];
    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
        const i0 = r * (cols + 1) + c;
        const i1 = i0 + 1;
        const i2 = (r + 1) * (cols + 1) + c;
        const i3 = i2 + 1;

        const colorIndex1 = (r * 3 + c * 5) % FACET_COLORS.length;
        const colorIndex2 = (r * 7 + c * 2 + 1) % FACET_COLORS.length;

        // Diagonal split
        if ((r + c) % 2 === 0) {
          triangles.push({ p1: i0, p2: i1, p3: i2, colorIdx: colorIndex1 });
          triangles.push({ p1: i1, p2: i3, p3: i2, colorIdx: colorIndex2 });
        } else {
          triangles.push({ p1: i0, p2: i1, p3: i3, colorIdx: colorIndex1 });
          triangles.push({ p1: i0, p2: i3, p3: i2, colorIdx: colorIndex2 });
        }
      }
    }
  }

  function render() {
    ctx.fillStyle = '#050d1e';
    ctx.fillRect(0, 0, width, height);

    // Gently drift points within bounded jitter
    for (const p of points) {
      p.x += p.vx;
      p.y += p.vy;
      if (Math.abs(p.x - p.originX) > 40) p.vx *= -1;
      if (Math.abs(p.y - p.originY) > 40) p.vy *= -1;
    }

    // Render shaded facets
    for (const t of triangles) {
      const p1 = points[t.p1];
      const p2 = points[t.p2];
      const p3 = points[t.p3];
      if (!p1 || !p2 || !p3) continue;

      const rgb = FACET_COLORS[t.colorIdx];
      ctx.beginPath();
      ctx.moveTo(p1.x, p1.y);
      ctx.lineTo(p2.x, p2.y);
      ctx.lineTo(p3.x, p3.y);
      ctx.closePath();

      ctx.fillStyle = `rgb(${rgb[0]}, ${rgb[1]}, ${rgb[2]})`;
      ctx.fill();

      // Subtle edge line for polygon wireframe effect
      ctx.strokeStyle = `rgba(50, 100, 200, 0.08)`;
      ctx.lineWidth = 0.8;
      ctx.stroke();
    }

    requestAnimationFrame(render);
  }

  window.addEventListener('resize', resize);
  resize();
  requestAnimationFrame(render);
})();

// ── Dropzone & Upload Handler ──
(function initDropzone() {
  const dropzone = document.getElementById('dropzone');
  const fileInput = document.getElementById('file-input');
  const uploadProgress = document.getElementById('upload-progress');
  const uploadFill = document.getElementById('upload-fill');
  const uploadLbl = document.getElementById('upload-lbl');

  if (!dropzone || !fileInput) return;

  dropzone.addEventListener('click', () => fileInput.click());

  ['dragenter', 'dragover'].forEach(name => {
    dropzone.addEventListener(name, (e) => {
      e.preventDefault();
      dropzone.classList.add('drag-over');
    });
  });

  ['dragleave', 'drop'].forEach(name => {
    dropzone.addEventListener(name, (e) => {
      e.preventDefault();
      dropzone.classList.remove('drag-over');
    });
  });

  dropzone.addEventListener('drop', (e) => {
    const file = e.dataTransfer?.files?.[0];
    if (file) handleUpload(file);
  });

  fileInput.addEventListener('change', () => {
    const file = fileInput.files?.[0];
    if (file) handleUpload(file);
  });

  function handleUpload(file) {
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      showToast('⚠️ Please upload a valid PDF file.');
      return;
    }

    if (uploadProgress && uploadFill && uploadLbl) {
      uploadProgress.style.display = 'block';
      uploadFill.style.width = '0%';
      uploadLbl.textContent = `Uploading ${file.name}…`;

      let progress = 0;
      const interval = setInterval(() => {
        progress += Math.floor(Math.random() * 25) + 15;
        if (progress >= 100) {
          progress = 100;
          clearInterval(interval);
          uploadFill.style.width = '100%';
          uploadLbl.textContent = 'Analyzing Syllabus with AI…';
          setTimeout(() => {
            uploadProgress.style.display = 'none';
            showToast(`✅ "${file.name}" processed! New course added.`);
          }, 900);
        } else {
          uploadFill.style.width = progress + '%';
        }
      }, 150);
    }
  }
})();

// ── Course Actions (Study, Quiz, Delete) ──
(function initCourseActions() {
  document.querySelectorAll('.btn-study').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const card = e.currentTarget.closest('.course-card');
      const name = card?.querySelector('.course-name')?.textContent || 'Course';
      showToast(`🚀 Starting Study Session for ${name}!`);
    });
  });

  document.querySelectorAll('.btn-quiz').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const card = e.currentTarget.closest('.course-card');
      const name = card?.querySelector('.course-name')?.textContent || 'Course';
      showToast(`🧠 Generating Quiz questions for ${name}…`);
    });
  });

  document.querySelectorAll('.trash-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const card = e.currentTarget.closest('.course-card');
      const name = card?.querySelector('.course-name')?.textContent || 'Course';
      if (confirm(`Remove "${name}" from your active courses?`)) {
        card.style.opacity = '0';
        card.style.transform = 'scale(0.9)';
        setTimeout(() => {
          card.remove();
          showToast(`🗑️ ${name} removed.`);
        }, 250);
      }
    });
  });
})();

// ── Quick Actions ──
(function initQuickActions() {
  const btnStudy = document.getElementById('btn-start-study');
  const btnQuiz = document.getElementById('btn-random-quiz');
  const btnUpload = document.getElementById('btn-upload-materials');

  if (btnStudy) {
    btnStudy.addEventListener('click', () => {
      showToast('📖 Opening Study Session dashboard…');
    });
  }

  if (btnQuiz) {
    btnQuiz.addEventListener('click', () => {
      showToast('🎯 Starting 10-Question Random Diagnostic Quiz…');
    });
  }

  if (btnUpload) {
    btnUpload.addEventListener('click', () => {
      document.getElementById('file-input')?.click();
    });
  }
})();

// ── Floating Chat FAB ──
(function initChatFAB() {
  const fab = document.getElementById('chat-fab');
  if (fab) {
    fab.addEventListener('click', () => {
      showToast('💬 AI Tutor: How can I help you prepare for your exams today?');
    });
  }
})();

// ── Navigation active indicator ──
document.querySelectorAll('.sn-item').forEach(item => {
  item.addEventListener('click', (e) => {
    e.preventDefault();
    document.querySelectorAll('.sn-item').forEach(i => i.classList.remove('active'));
    item.classList.add('active');
    const title = item.getAttribute('title');
    if (title && title !== 'Home') {
      showToast(`Navigating to ${title}…`);
    }
  });
});
