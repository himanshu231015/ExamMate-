/* =====================================================
   Swift-Prep – App JavaScript
   Authentication (Admin: Admin123 / dj1234 & Student)
   Complete SPA View Routing & Interactive Modals
   ===================================================== */

const API_BASE = window.location.origin.includes(':8000')
  ? window.location.origin
  : 'http://127.0.0.1:8000';

const AUTH_TOKEN_KEY = 'swiftprep_token';
const AUTH_USER_KEY = 'swiftprep_user';

// ── Toast Notification Helper ──
function showToast(message, duration = 3200) {
  const toast = document.getElementById('toast');
  if (!toast) return;
  toast.textContent = message;
  toast.classList.add('show');
  clearTimeout(toast._timeout);
  toast._timeout = setTimeout(() => {
    toast.classList.remove('show');
  }, duration);
}

// ── Auth Alert Helper ──
function showAuthAlert(message, type = 'error') {
  const alertEl = document.getElementById('auth-alert');
  if (!alertEl) return;
  alertEl.textContent = message;
  alertEl.className = `auth-alert ${type}`;
  alertEl.style.display = 'flex';
}

function clearAuthAlert() {
  const alertEl = document.getElementById('auth-alert');
  if (alertEl) {
    alertEl.style.display = 'none';
    alertEl.textContent = '';
  }
}

// ── Authentication State Manager ──
let currentUser = null;
let currentRoleScope = 'student'; // 'student' or 'admin'

function getStoredSession() {
  try {
    const token = localStorage.getItem(AUTH_TOKEN_KEY);
    const userStr = localStorage.getItem(AUTH_USER_KEY);
    if (token && userStr) {
      return { token, user: JSON.parse(userStr) };
    }
  } catch (err) {
    console.error('Error parsing stored session:', err);
  }
  return null;
}

function saveSession(token, user) {
  try {
    localStorage.setItem(AUTH_TOKEN_KEY, token);
    localStorage.setItem(AUTH_USER_KEY, JSON.stringify(user));
  } catch (err) {
    console.error('Error saving session:', err);
  }
}

function clearSession() {
  try {
    localStorage.removeItem(AUTH_TOKEN_KEY);
    localStorage.removeItem(AUTH_USER_KEY);
  } catch (err) {
    console.error('Error clearing session:', err);
  }
  currentUser = null;
}

// ── View Renderers: Gate Dashboard Behind Login ──
function renderAuthenticatedView(user) {
  currentUser = user;
  const authSection = document.getElementById('auth-section');
  const dashboardWrapper = document.getElementById('dashboard-wrapper');

  if (authSection) authSection.style.display = 'none';
  if (dashboardWrapper) {
    dashboardWrapper.classList.remove('dashboard-hidden');
    dashboardWrapper.classList.add('dashboard-visible');
  }

  // Update User Initial & Names
  const initial = (user.full_name || user.email || 'U').charAt(0).toUpperCase();
  const roleName = (user.role || 'student').toLowerCase();
  const isAdmin = roleName === 'admin' || (user.email && user.email.toLowerCase().includes('admin'));

  // Identify user roles
  const isContributor = roleName === 'contributor';
  const isReviewer = roleName === 'reviewer';
  const isStudent = !isAdmin && !isContributor && !isReviewer;

  // Sidebar badge
  const sidebarInitial = document.getElementById('sidebar-user-initial');
  if (sidebarInitial) sidebarInitial.textContent = initial;

  // Topbar role badge
  const roleBadge = document.getElementById('topbar-role-badge');
  if (roleBadge) {
    if (isAdmin) {
      roleBadge.textContent = 'ADMINISTRATOR';
      roleBadge.className = 'user-role-badge role-admin';
    } else if (isContributor) {
      roleBadge.textContent = 'CONTRIBUTOR';
      roleBadge.className = 'user-role-badge role-contributor';
    } else if (isReviewer) {
      roleBadge.textContent = 'REVIEWER';
      roleBadge.className = 'user-role-badge role-reviewer';
    } else {
      roleBadge.textContent = 'STUDENT';
      roleBadge.className = 'user-role-badge role-student';
    }
  }

  // Topbar avatar & name
  const topbarInitial = document.getElementById('topbar-avatar-initial');
  if (topbarInitial) topbarInitial.textContent = initial;

  const compactName = document.getElementById('profile-compact-name');
  if (compactName) compactName.textContent = user.full_name ? user.full_name.split(' ')[0] : (isAdmin ? 'Admin' : (isContributor ? 'Contributor' : (isReviewer ? 'Reviewer' : 'Student')));

  // Dropdown info
  const pdmAvatar = document.getElementById('pdm-avatar');
  if (pdmAvatar) pdmAvatar.textContent = initial;

  const pdmName = document.getElementById('pdm-name');
  if (pdmName) pdmName.textContent = user.full_name || (isAdmin ? 'RGPV Administrator' : `${roleName.toUpperCase()} Member`);

  const pdmEmail = document.getElementById('pdm-email');
  if (pdmEmail) pdmEmail.textContent = user.email || (isAdmin ? 'Admin123' : '');

  const pdmRole = document.getElementById('pdm-role-tag');
  if (pdmRole) pdmRole.textContent = isAdmin ? 'PORTAL ADMINISTRATOR' : `${roleName.toUpperCase()} ACCOUNT`;

  const pdmAdminLink = document.getElementById('pdm-admin-link');
  if (pdmAdminLink) pdmAdminLink.style.display = isAdmin ? 'flex' : 'none';

  // Admin Banner Card
  const adminBanner = document.getElementById('admin-banner');
  if (adminBanner) {
    adminBanner.style.display = isAdmin ? 'flex' : 'none';
  }

  // Hero greeting personalized
  const greetingEl = document.getElementById('greeting-h1');
  if (greetingEl) {
    const firstName = user.full_name ? user.full_name.split(' ')[0] : (isAdmin ? 'Administrator' : (isContributor ? 'Contributor' : (isReviewer ? 'Reviewer' : 'there')));
    const h = new Date().getHours();
    const timeWord = (h >= 5 && h < 12) ? 'Good morning' : (h >= 12 && h < 17) ? 'Good afternoon' : 'Good evening';
    greetingEl.textContent = `${timeWord}, ${firstName}! 👋`;
  }

  const heroLevelDisplay = document.getElementById('hero-level-display');
  const heroRoleSub = document.getElementById('hero-role-sub');
  if (heroLevelDisplay && heroRoleSub) {
    if (isAdmin) {
      heroRoleSub.textContent = 'Governance';
      heroLevelDisplay.innerHTML = 'Admin<span class="level-accent">istrator</span>';
      const greetingP = document.getElementById('greeting-p');
      if (greetingP) greetingP.textContent = 'Platform analytics, registered student statistics, and 4-year curriculum oversight.';
    } else if (isContributor) {
      heroRoleSub.textContent = 'Role Scope';
      heroLevelDisplay.innerHTML = 'Contrib<span class="level-accent">utor</span>';
      const greetingP = document.getElementById('greeting-p');
      if (greetingP) greetingP.textContent = 'Submit and manage previous year exam question papers for university verification.';
    } else if (isReviewer) {
      heroRoleSub.textContent = 'Role Scope';
      heroLevelDisplay.innerHTML = 'Rev<span class="level-accent">iewer</span>';
      const greetingP = document.getElementById('greeting-p');
      if (greetingP) greetingP.textContent = 'Inspect incoming question papers, verify syllabus fidelity, and approve publications.';
    } else {
      heroRoleSub.textContent = 'Access Level';
      heroLevelDisplay.innerHTML = 'Intermed<span class="level-accent">iate</span>';
      const greetingP = document.getElementById('greeting-p');
      if (greetingP) greetingP.textContent = "Ah, we meet again. That syllabus isn't going to read itself, apparently.";
    }
  }

  // Toggle role-scoped Dashboard Home Content
  const studentHome = document.getElementById('student-home-content');
  const contribHome = document.getElementById('contributor-home-content');
  const reviewerHome = document.getElementById('reviewer-home-content');
  const adminHome = document.getElementById('admin-home-content');

  if (studentHome) studentHome.style.display = isStudent ? 'block' : 'none';
  if (contribHome) contribHome.style.display = isContributor ? 'block' : 'none';
  if (reviewerHome) reviewerHome.style.display = isReviewer ? 'block' : 'none';
  if (adminHome) adminHome.style.display = isAdmin ? 'block' : 'none';

  // Load initial role-based data
  if (isContributor) {
    loadContributorDashboard();
  } else if (isReviewer) {
    loadReviewerDashboard();
  } else if (isAdmin) {
    loadAdminOverview();
  }

  // Ensure default view is Home
  switchDashboardPage('home');
}

function renderUnauthenticatedView() {
  const authSection = document.getElementById('auth-section');
  const dashboardWrapper = document.getElementById('dashboard-wrapper');

  if (dashboardWrapper) {
    dashboardWrapper.classList.remove('dashboard-visible');
    dashboardWrapper.classList.add('dashboard-hidden');
  }
  if (authSection) authSection.style.display = 'flex';

  clearAuthAlert();
}

// ── Check Auth on Startup ──
function initAuthCheck() {
  const session = getStoredSession();
  if (session && session.token && session.user) {
    renderAuthenticatedView(session.user);
    fetch(`${API_BASE}/api/v1/auth/me`, {
      headers: { 'Authorization': `Bearer ${session.token}` }
    })
    .then(res => {
      if (res.ok) return res.json();
      throw new Error('Token expired');
    })
    .then(freshUser => {
      saveSession(session.token, freshUser);
      renderAuthenticatedView(freshUser);
    })
    .catch(() => {
      // Keep session for offline resilience
    });
  } else {
    renderUnauthenticatedView();
  }
}

// ── Interactive Auth Form Controls ──
function initAuthControls() {
  const tabLogin = document.getElementById('tab-login');
  const tabRegister = document.getElementById('tab-register');
  const authTabsWrap = document.getElementById('auth-tabs-wrap');
  const loginContainer = document.getElementById('login-container');
  const registerContainer = document.getElementById('register-container');
  const goToRegister = document.getElementById('go-to-register');
  const goToLogin = document.getElementById('go-to-login');
  const authSwitchWrap = document.getElementById('auth-switch-to-reg-wrap');

  function switchToLogin() {
    clearAuthAlert();
    tabLogin?.classList.add('active');
    tabRegister?.classList.remove('active');
    if (loginContainer) loginContainer.style.display = 'block';
    if (registerContainer) registerContainer.style.display = 'none';
  }

  function switchToRegister() {
    // Admin cannot register; only student/contributor
    if (currentRoleScope === 'admin') {
      showToast('⚠️ Admin registration is disabled. Please use authorized Admin ID to sign in.');
      return;
    }
    clearAuthAlert();
    tabRegister?.classList.add('active');
    tabLogin?.classList.remove('active');
    if (registerContainer) registerContainer.style.display = 'block';
    if (loginContainer) loginContainer.style.display = 'none';
  }

  tabLogin?.addEventListener('click', switchToLogin);
  tabRegister?.addEventListener('click', switchToRegister);
  goToRegister?.addEventListener('click', switchToRegister);
  goToLogin?.addEventListener('click', switchToLogin);

  // Role Scope Switcher Pills (Student vs Administrator)
  const pillStudent = document.getElementById('pill-role-student');
  const pillAdmin = document.getElementById('pill-role-admin');
  const loginRoleHintText = document.getElementById('login-role-hint-text');
  const roleDot = document.getElementById('role-dot');
  const loginBtnText = document.getElementById('login-btn-text');
  const lblLoginId = document.getElementById('lbl-login-id');
  const emailInput = document.getElementById('login-email');
  const passInput = document.getElementById('login-password');
  const hintPassText = document.getElementById('hint-pass-text');

  function setRoleScope(role) {
    currentRoleScope = role;
    clearAuthAlert();
    switchToLogin();

    if (role === 'admin') {
      pillAdmin?.classList.add('active');
      pillStudent?.classList.remove('active');
      if (roleDot) roleDot.className = 'role-context-dot admin';

      // Hide Register tab for Admin
      if (tabRegister) tabRegister.style.display = 'none';
      if (authSwitchWrap) authSwitchWrap.style.display = 'none';

      if (loginRoleHintText) {
        loginRoleHintText.innerHTML = '🛡️ Administrator Mode: Enter Admin ID (<strong>Admin123</strong>) & Password (<strong>dj1234</strong>).';
      }
      if (lblLoginId) lblLoginId.textContent = 'Admin ID';
      if (emailInput) emailInput.placeholder = 'e.g. Admin123';
      if (passInput) passInput.placeholder = 'e.g. dj1234';
      if (hintPassText) hintPassText.textContent = 'Default: dj1234';
      if (loginBtnText) loginBtnText.textContent = 'Sign In as Administrator';
    } else {
      pillStudent?.classList.add('active');
      pillAdmin?.classList.remove('active');
      if (roleDot) roleDot.className = 'role-context-dot student';

      // Show Register tab for Students
      if (tabRegister) tabRegister.style.display = 'block';
      if (authSwitchWrap) authSwitchWrap.style.display = 'block';

      if (loginRoleHintText) {
        loginRoleHintText.innerHTML = '🎓 Signing in as <strong>Student</strong> to access study plans & PYQs.';
      }
      if (lblLoginId) lblLoginId.textContent = 'Email / ID';
      if (emailInput) emailInput.placeholder = 'e.g. student@rgpvexammate.edu';
      if (passInput) passInput.placeholder = '••••••••';
      if (hintPassText) hintPassText.textContent = 'Default: Student@123';
      if (loginBtnText) loginBtnText.textContent = 'Sign In to Dashboard';
    }
  }

  pillStudent?.addEventListener('click', () => setRoleScope('student'));
  pillAdmin?.addEventListener('click', () => setRoleScope('admin'));

  // Toggle Password Visibility
  const togglePassBtn = document.getElementById('toggle-login-pass');
  togglePassBtn?.addEventListener('click', () => {
    if (passInput) {
      passInput.type = passInput.type === 'password' ? 'text' : 'password';
    }
  });

  // Quick 1-Click Demo Logins
  const demoStudentBtn = document.getElementById('demo-student-btn');
  const demoAdminBtn = document.getElementById('demo-admin-btn');
  const demoContributorBtn = document.getElementById('demo-contributor-btn');
  const demoReviewerBtn = document.getElementById('demo-reviewer-btn');

  demoStudentBtn?.addEventListener('click', () => {
    setRoleScope('student');
    if (emailInput) emailInput.value = 'student@rgpvexammate.edu';
    if (passInput) passInput.value = 'Student@123';
    showToast('🎓 Student demo credentials loaded! Click Sign In.');
  });

  demoContributorBtn?.addEventListener('click', () => {
    setRoleScope('student');
    if (emailInput) emailInput.value = 'contributor@rgpvexammate.edu';
    if (passInput) passInput.value = 'Contrib@123';
    showToast('✍️ Contributor demo credentials loaded! Click Sign In.');
  });

  demoReviewerBtn?.addEventListener('click', () => {
    setRoleScope('student');
    if (emailInput) emailInput.value = 'reviewer@rgpvexammate.edu';
    if (passInput) passInput.value = 'Reviewer@123';
    showToast('🧑‍🏫 Reviewer demo credentials loaded! Click Sign In.');
  });

  demoAdminBtn?.addEventListener('click', () => {
    setRoleScope('admin');
    if (emailInput) emailInput.value = 'Admin123';
    if (passInput) passInput.value = 'dj1234';
    showToast('🛡️ Admin credentials (Admin123 / dj1234) loaded! Click Sign In.');
  });

  // Login Form Submission
  const loginForm = document.getElementById('login-form');
  const loginSpinner = document.getElementById('login-spinner');
  const btnSubmitLogin = document.getElementById('btn-submit-login');

  loginForm?.addEventListener('submit', async (e) => {
    e.preventDefault();
    clearAuthAlert();

    const email = emailInput?.value.trim() || '';
    const password = passInput?.value || '';

    if (!email || !password) {
      showAuthAlert('Please enter both ID/Email and password.');
      return;
    }

    // Check direct Admin123 / dj1234 match
    const isAdminId = email.toLowerCase() === 'admin123' || email.toLowerCase() === 'admin123@rgpvexammate.edu';
    if (isAdminId && password === 'dj1234') {
      const adminUser = {
        id: 1,
        full_name: 'RGPV Administrator',
        email: 'Admin123',
        role: 'admin',
        is_active: true,
        created_at: new Date().toISOString()
      };
      saveSession('admin-jwt-token-active', adminUser);
      renderAuthenticatedView(adminUser);
      showToast('🛡️ Administrator verified! Welcome to Central Control.');
      return;
    }

    if (loginSpinner) loginSpinner.style.display = 'inline-block';
    if (btnSubmitLogin) btnSubmitLogin.disabled = true;

    try {
      const response = await fetch(`${API_BASE}/api/v1/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (response.ok && data.access_token) {
        saveSession(data.access_token, data.user);
        renderAuthenticatedView(data.user);
        showToast(`🎉 Welcome back, ${data.user.full_name}! Dashboard ready.`);
      } else {
        const errorMsg = data.detail || 'Incorrect ID or password. Please verify credentials.';
        showAuthAlert(`⚠️ ${errorMsg}`);
      }
    } catch (err) {
      console.warn('Backend API connection error:', err);
      // Resilient fallback for testing
      handleOfflineLoginFallback(email, password);
    } finally {
      if (loginSpinner) loginSpinner.style.display = 'none';
      if (btnSubmitLogin) btnSubmitLogin.disabled = false;
    }
  });

  // Register Form Submission (Students & Contributors only)
  const regForm = document.getElementById('register-form');
  const regSpinner = document.getElementById('reg-spinner');
  const btnSubmitReg = document.getElementById('btn-submit-register');
  const regName = document.getElementById('reg-name');
  const regEmail = document.getElementById('reg-email');
  const regRoleSelect = document.getElementById('reg-role');
  const regPass = document.getElementById('reg-password');
  const regConfirmPass = document.getElementById('reg-confirm-password');

  regForm?.addEventListener('submit', async (e) => {
    e.preventDefault();
    clearAuthAlert();

    const fullName = regName?.value.trim() || '';
    const email = regEmail?.value.trim() || '';
    const role = regRoleSelect?.value || 'student';
    const password = regPass?.value || '';
    const confirmPass = regConfirmPass?.value || '';

    if (password !== confirmPass) {
      showAuthAlert('⚠️ Passwords do not match. Please re-enter carefully.');
      return;
    }

    if (password.length < 6) {
      showAuthAlert('⚠️ Password must be at least 6 characters long.');
      return;
    }

    if (regSpinner) regSpinner.style.display = 'inline-block';
    if (btnSubmitReg) btnSubmitReg.disabled = true;

    try {
      const response = await fetch(`${API_BASE}/api/v1/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          full_name: fullName,
          email: email,
          password: password,
          role: role,
        }),
      });

      const data = await response.json();

      if (response.ok && data.access_token) {
        saveSession(data.access_token, data.user);
        renderAuthenticatedView(data.user);
        showToast(`🚀 Account created! Welcome, ${data.user.full_name}!`);
      } else {
        const errorMsg = data.detail || 'Registration failed. Email might already be taken.';
        showAuthAlert(`⚠️ ${errorMsg}`);
      }
    } catch (err) {
      console.warn('Backend API connection error:', err);
      handleOfflineRegisterFallback(fullName, email, role);
    } finally {
      if (regSpinner) regSpinner.style.display = 'none';
      if (btnSubmitReg) btnSubmitReg.disabled = false;
    }
  });
}

function handleOfflineLoginFallback(email, password) {
  const isAdm = email.toLowerCase().includes('admin') || password === 'dj1234';
  const isReviewer = email.toLowerCase().includes('reviewer') || password === 'Reviewer@123';
  const isContributor = email.toLowerCase().includes('contributor') || password === 'Contrib@123';

  if (isAdm) {
    if (password !== 'dj1234') {
      showAuthAlert('⚠️ Incorrect Admin password. Required: dj1234');
      return;
    }
    const mockAdmin = {
      id: 1,
      full_name: 'RGPV Administrator',
      email: 'Admin123',
      role: 'admin',
      is_active: true,
      created_at: new Date().toISOString()
    };
    saveSession('mock-admin-token', mockAdmin);
    renderAuthenticatedView(mockAdmin);
    showToast('🛡️ Signed in as Administrator (Admin123)');
  } else if (isReviewer) {
    const mockReviewer = {
      id: 2,
      full_name: 'Prof. Sharma (Authorized Reviewer)',
      email: email,
      role: 'reviewer',
      is_active: true,
      created_at: new Date().toISOString()
    };
    saveSession('mock-reviewer-token', mockReviewer);
    renderAuthenticatedView(mockReviewer);
    showToast('🧑‍🏫 Signed in as Reviewer (Prof. Sharma)');
  } else if (isContributor) {
    const mockContrib = {
      id: 3,
      full_name: 'Aman Verma (Student Contributor)',
      email: email,
      role: 'contributor',
      is_active: true,
      created_at: new Date().toISOString()
    };
    saveSession('mock-contrib-token', mockContrib);
    renderAuthenticatedView(mockContrib);
    showToast('✍️ Signed in as Contributor (Aman Verma)');
  } else {
    const mockStudent = {
      id: 4,
      full_name: 'Priya Patel',
      email: email,
      role: 'student',
      is_active: true,
      created_at: new Date().toISOString()
    };
    saveSession('mock-student-token', mockStudent);
    renderAuthenticatedView(mockStudent);
    showToast('🎓 Signed in as Student');
  }
}

function handleOfflineRegisterFallback(fullName, email, role) {
  const mockUser = {
    id: Date.now(),
    full_name: fullName,
    email: email,
    role: role,
    is_active: true,
    created_at: new Date().toISOString()
  };
  saveSession('mock-token-' + Date.now(), mockUser);
  renderAuthenticatedView(mockUser);
  showToast(`✅ Welcome, ${fullName}! Account created.`);
}

// =====================================================
// DASHBOARD SPA PAGE ROUTER
// Switching between Home, Courses, Syllabus, Practice, PYQ, College, Analytics
// =====================================================
const PAGE_TITLES = {
  home: 'Home Dashboard',
  courses: 'Course Catalog',
  syllabus: 'Syllabus Explorer',
  practice: 'Practice & Diagnostic Arena',
  pyq: 'Previous Year Question Papers',
  college: 'RGPV University Portal',
  analytics: 'Academic Analytics'
};

function switchDashboardPage(pageId) {
  const pages = [
    'home', 'courses', 'syllabus', 'practice', 'pyq', 'college', 'analytics'
  ];

  if (!pages.includes(pageId)) pageId = 'home';

  // Hide all view sections
  pages.forEach(p => {
    const el = document.getElementById(`view-${p}`);
    if (el) el.style.display = 'none';
  });

  // Show target page
  const targetPage = document.getElementById(`view-${pageId}`);
  if (targetPage) {
    targetPage.style.display = 'block';
  }

  // Update Sidebar active state
  document.querySelectorAll('.sidebar-nav .sn-item').forEach(item => {
    const viewName = item.getAttribute('data-view');
    if (viewName === pageId) {
      item.classList.add('active');
    } else {
      item.classList.remove('active');
    }
  });

  // Update Topbar Title
  const subTitle = document.getElementById('topbar-section-title');
  if (subTitle && PAGE_TITLES[pageId]) {
    subTitle.textContent = PAGE_TITLES[pageId];
  }

  // Scroll to top of main container
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function initDashboardRouting() {
  // Sidebar navigation clicks
  document.querySelectorAll('.sidebar-nav .sn-item').forEach(item => {
    item.addEventListener('click', (e) => {
      e.preventDefault();
      const view = item.getAttribute('data-view') || 'home';
      switchDashboardPage(view);
    });
  });

  // Sidebar logo clicks
  document.getElementById('sn-logo-link')?.addEventListener('click', (e) => {
    e.preventDefault();
    switchDashboardPage('home');
  });

  // "View All Courses" button in Home panel
  document.getElementById('btn-goto-courses-tab')?.addEventListener('click', () => {
    switchDashboardPage('courses');
  });

  // Add course trigger
  document.getElementById('btn-add-course-trigger')?.addEventListener('click', () => {
    document.getElementById('file-input')?.click();
  });
}

// =====================================================
// INTERACTIVE QUIZ ENGINE
// =====================================================
const QUIZ_QUESTIONS = [
  {
    question: "What linear data structure operates on a Last-In-First-Out (LIFO) principle and is used in function call stacks?",
    options: ["Queue", "Stack", "Binary Search Tree", "Circular Linked List"],
    answerIndex: 1,
    explanation: "A Stack strictly enforces the LIFO principle where insertion (Push) and removal (Pop) occur at the Top node."
  },
  {
    question: "In an AVL Tree, what rotation is performed when an insertion occurs in the Right child of a Left sub-tree?",
    options: ["LL Rotation", "RR Rotation", "LR (Left-Right) Double Rotation", "RL (Right-Left) Double Rotation"],
    answerIndex: 2,
    explanation: "An LR rotation is performed by first doing a Left rotation on the left child, followed by a Right rotation on the root."
  },
  {
    question: "What is the worst-case time complexity of the Quick Sort algorithm when pivot selection is poor?",
    options: ["O(log n)", "O(n log n)", "O(n)", "O(n²)"],
    answerIndex: 3,
    explanation: "When the partition divides the array into 0 and n-1 elements repeatedly (e.g. sorted input with last element pivot), Quick Sort degrades to O(n²)."
  },
  {
    question: "Which algorithmic paradigm does the 0/1 Knapsack problem solve using a 2D memoization table?",
    options: ["Divide & Conquer", "Dynamic Programming", "Greedy Method", "Branch & Bound"],
    answerIndex: 1,
    explanation: "0/1 Knapsack exhibits optimal substructure and overlapping subproblems, making Dynamic Programming O(nW) the optimal solution."
  },
  {
    question: "Which graph traversal uses a FIFO Queue to visit all adjacent vertices level by level?",
    options: ["Breadth First Search (BFS)", "Depth First Search (DFS)", "Topological Sort", "Eulerian Walk"],
    answerIndex: 0,
    explanation: "BFS explores vertex frontiers uniformly using a FIFO Queue, resulting in O(V + E) complexity."
  }
];

let currentQuizIndex = 0;
let quizScore = 0;
let quizTimerInterval = null;

function openQuizModal(subjectName = 'RGPV Diagnostic Practice Exam') {
  const modal = document.getElementById('quiz-modal');
  const titleEl = document.getElementById('quiz-modal-title');
  if (titleEl) titleEl.textContent = subjectName;

  currentQuizIndex = 0;
  quizScore = 0;

  renderQuizQuestion();
  startQuizTimer();

  if (modal) modal.style.display = 'flex';
}

function closeQuizModal() {
  const modal = document.getElementById('quiz-modal');
  if (modal) modal.style.display = 'none';
  if (quizTimerInterval) clearInterval(quizTimerInterval);
}

function startQuizTimer() {
  let secondsLeft = 180;
  const timerEl = document.getElementById('quiz-timer');

  if (quizTimerInterval) clearInterval(quizTimerInterval);

  quizTimerInterval = setInterval(() => {
    secondsLeft--;
    if (secondsLeft <= 0) {
      clearInterval(quizTimerInterval);
      showToast('⏰ Time is up! Evaluating answers.');
      return;
    }
    const mins = String(Math.floor(secondsLeft / 60)).padStart(2, '0');
    const secs = String(secondsLeft % 60).padStart(2, '0');
    if (timerEl) timerEl.textContent = `⏱️ ${mins}:${secs}`;
  }, 1000);
}

function renderQuizQuestion() {
  const q = QUIZ_QUESTIONS[currentQuizIndex];
  const qText = document.getElementById('quiz-q-text');
  const counter = document.getElementById('quiz-question-counter');
  const optionsContainer = document.getElementById('quiz-options-container');
  const feedbackBox = document.getElementById('quiz-feedback');
  const btnNext = document.getElementById('btn-quiz-next');
  const scoreHint = document.getElementById('quiz-score-hint');

  if (!qText || !optionsContainer) return;

  if (feedbackBox) feedbackBox.style.display = 'none';
  if (btnNext) btnNext.style.display = 'none';
  if (scoreHint) scoreHint.textContent = `Score: ${quizScore} / ${QUIZ_QUESTIONS.length}`;

  counter.textContent = `Question ${currentQuizIndex + 1} of ${QUIZ_QUESTIONS.length}`;
  qText.textContent = q.question;

  const letters = ['A', 'B', 'C', 'D'];
  optionsContainer.innerHTML = q.options.map((opt, i) => `
    <button type="button" class="quiz-opt-btn" data-index="${i}">
      <span class="opt-letter">${letters[i]}</span>
      <span class="opt-text">${escapeHtml(opt)}</span>
    </button>
  `).join('');

  optionsContainer.querySelectorAll('.quiz-opt-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const selectedIndex = parseInt(btn.getAttribute('data-index'), 10);
      evaluateAnswer(selectedIndex, q, btn, optionsContainer);
    });
  });
}

function evaluateAnswer(selectedIndex, q, chosenBtn, container) {
  // Disable options once selected
  container.querySelectorAll('.quiz-opt-btn').forEach(b => b.disabled = true);

  const feedbackBox = document.getElementById('quiz-feedback');
  const btnNext = document.getElementById('btn-quiz-next');
  const scoreHint = document.getElementById('quiz-score-hint');

  const isCorrect = selectedIndex === q.answerIndex;

  if (isCorrect) {
    quizScore++;
    chosenBtn.classList.add('correct');
    if (feedbackBox) {
      feedbackBox.className = 'quiz-feedback-box correct';
      feedbackBox.innerHTML = `<strong>✅ Correct Answer!</strong> ${q.explanation}`;
      feedbackBox.style.display = 'block';
    }
  } else {
    chosenBtn.classList.add('wrong');
    // Highlight correct one
    const correctBtn = container.querySelector(`[data-index="${q.answerIndex}"]`);
    if (correctBtn) correctBtn.classList.add('correct');

    if (feedbackBox) {
      feedbackBox.className = 'quiz-feedback-box wrong';
      feedbackBox.innerHTML = `<strong>❌ Incorrect.</strong> ${q.explanation}`;
      feedbackBox.style.display = 'block';
    }
  }

  if (scoreHint) scoreHint.textContent = `Score: ${quizScore} / ${QUIZ_QUESTIONS.length}`;

  if (btnNext) {
    btnNext.style.display = 'inline-flex';
    btnNext.textContent = currentQuizIndex === QUIZ_QUESTIONS.length - 1 ? 'Finish Quiz' : 'Next Question →';
  }
}

function initQuizModalEvents() {
  document.getElementById('btn-close-quiz-modal')?.addEventListener('click', closeQuizModal);

  document.getElementById('btn-quiz-next')?.addEventListener('click', () => {
    if (currentQuizIndex < QUIZ_QUESTIONS.length - 1) {
      currentQuizIndex++;
      renderQuizQuestion();
    } else {
      // Quiz finished
      if (quizTimerInterval) clearInterval(quizTimerInterval);
      showToast(`🏆 Quiz Completed! Your Score: ${quizScore} / ${QUIZ_QUESTIONS.length}`);
      closeQuizModal();
    }
  });

  // Quick Action "Take Random Quiz" button
  document.getElementById('btn-random-quiz')?.addEventListener('click', () => {
    openQuizModal('RGPV 10-Question Random Diagnostic Quiz');
  });

  // Practice page test buttons
  document.getElementById('btn-practice-quick')?.addEventListener('click', () => {
    openQuizModal('5-Question Diagnostic Sprint');
  });

  document.getElementById('btn-practice-avl')?.addEventListener('click', () => {
    openQuizModal('Trees & AVL Tree Rotations Practice');
  });

  document.getElementById('btn-practice-ada')?.addEventListener('click', () => {
    openQuizModal('Algorithms & Dynamic Programming Quiz');
  });

  // Course card quiz buttons
  document.querySelectorAll('.btn-quiz').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const subject = btn.getAttribute('data-subject') || 'RGPV Exam Quiz';
      openQuizModal(subject);
    });
  });
}

// =====================================================
// INTERACTIVE STUDY SESSION MODAL
// =====================================================
const STUDY_CARDS = [
  {
    title: "Stack ADT & Applications (CS-301)",
    desc: "A Stack is a linear data structure following LIFO (Last In First Out). Fundamental operations are Push(x) and Pop(), both executing in O(1) time.",
    formula: "Infix to Postfix Precedence: ^ (Right to Left) > * / (Left to Right) > + - (Left to Right)",
    highlight: "Common RGPV Exam Question: Convert (A + B * C) / (D - E) into postfix step-by-step using stack."
  },
  {
    title: "AVL Trees & Balance Factors (CS-301)",
    desc: "An AVL Tree is a self-balancing Binary Search Tree where the Balance Factor (Height of Left Subtree - Height of Right Subtree) for every node must be -1, 0, or +1.",
    formula: "Balance Factor = Height(Left_Child) - Height(Right_Child) ∈ {-1, 0, 1}",
    highlight: "Rotations: LL (Single Right), RR (Single Left), LR (Left then Right), RL (Right then Left)."
  },
  {
    title: "Master Theorem for Recurrence Relations (CS-402)",
    desc: "Solves recurrence relations of the form T(n) = aT(n/b) + f(n) where a ≥ 1 and b > 1.",
    formula: "Compare f(n) with n^(log_b(a)): Case 1: O(n^(log_b a - ε)), Case 2: Θ(n^(log_b a) * log^k n), Case 3: Ω(n^(log_b a + ε)).",
    highlight: "Example: T(n) = 3T(n/4) + n log n has a=3, b=4. Since log_4(3) ≈ 0.79 < 1, Case 3 applies -> T(n) = Θ(n log n)."
  },
  {
    title: "0/1 Knapsack Problem (CS-402)",
    desc: "Given weights w[1..n] and values v[1..n] and capacity W, maximize total value without exceeding W, choosing each item at most once.",
    formula: "V[i, w] = max(V[i-1, w], v[i] + V[i-1, w - w[i]]) if w >= w[i]",
    highlight: "Time Complexity: O(n × W), Space Complexity: O(n × W) using dynamic programming tabulation matrix."
  }
];

let currentStudyIndex = 0;

function openStudyModal(subjectName = 'Study Session') {
  const modal = document.getElementById('study-modal');
  const titleEl = document.getElementById('study-modal-title');
  if (titleEl) titleEl.textContent = `AI Study Reader: ${subjectName}`;

  currentStudyIndex = 0;
  renderStudyCard();

  if (modal) modal.style.display = 'flex';
}

function closeStudyModal() {
  const modal = document.getElementById('study-modal');
  if (modal) modal.style.display = 'none';
}

function renderStudyCard() {
  const card = STUDY_CARDS[currentStudyIndex];
  const container = document.getElementById('study-card-content');
  const indicator = document.getElementById('study-card-indicator');

  if (!container) return;

  container.innerHTML = `
    <h3>${escapeHtml(card.title)}</h3>
    <p>${escapeHtml(card.desc)}</p>
    <div class="study-formula-box">${escapeHtml(card.formula)}</div>
    <p style="color:#f59e0b; font-size:0.84rem; line-height:1.5;">💡 <strong>RGPV Exam Tip:</strong> ${escapeHtml(card.highlight)}</p>
  `;

  if (indicator) {
    indicator.textContent = `Card ${currentStudyIndex + 1} of ${STUDY_CARDS.length}`;
  }
}

function initStudyModalEvents() {
  document.getElementById('btn-close-study-modal')?.addEventListener('click', closeStudyModal);

  document.getElementById('btn-study-prev')?.addEventListener('click', () => {
    if (currentStudyIndex > 0) {
      currentStudyIndex--;
      renderStudyCard();
    }
  });

  document.getElementById('btn-study-next')?.addEventListener('click', () => {
    if (currentStudyIndex < STUDY_CARDS.length - 1) {
      currentStudyIndex++;
      renderStudyCard();
    }
  });

  // Launch buttons
  document.getElementById('btn-start-study')?.addEventListener('click', () => {
    openStudyModal('RGPV Core Engineering Modules');
  });

  document.querySelectorAll('.btn-study').forEach(btn => {
    btn.addEventListener('click', () => {
      const subject = btn.getAttribute('data-subject') || 'RGPV Syllabus';
      openStudyModal(subject);
    });
  });
}

// =====================================================
// INTERACTIVE AI TUTOR CHAT DRAWER
// =====================================================
function initChatDrawer() {
  const fab = document.getElementById('chat-fab');
  const backdrop = document.getElementById('chat-backdrop');
  const btnClose = document.getElementById('btn-close-chat');
  const chatForm = document.getElementById('chat-form');
  const chatInput = document.getElementById('chat-input-text');
  const chatMessages = document.getElementById('chat-messages');

  function openChat() {
    if (backdrop) backdrop.style.display = 'flex';
    chatInput?.focus();
  }

  function closeChat() {
    if (backdrop) backdrop.style.display = 'none';
  }

  fab?.addEventListener('click', openChat);
  btnClose?.addEventListener('click', closeChat);

  backdrop?.addEventListener('click', (e) => {
    if (e.target === backdrop) closeChat();
  });

  // Suggestion chips
  document.querySelectorAll('.chat-suggestion-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      const text = chip.textContent.trim();
      handleUserSendMessage(text);
    });
  });

  chatForm?.addEventListener('submit', (e) => {
    e.preventDefault();
    const query = chatInput?.value.trim();
    if (!query) return;
    chatInput.value = '';
    handleUserSendMessage(query);
  });

  function handleUserSendMessage(text) {
    appendChatMessage('user', text);

    // AI thinking indicator
    const typingId = 'typing-' + Date.now();
    appendChatMessage('ai', 'Thinking…', typingId);

    setTimeout(() => {
      const response = generateAIAnswer(text);
      const typingEl = document.getElementById(typingId);
      if (typingEl) {
        typingEl.querySelector('.msg-bubble').innerHTML = response;
      }
      chatMessages.scrollTop = chatMessages.scrollHeight;
    }, 600);
  }

  function appendChatMessage(sender, text, id = null) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `chat-msg ${sender}`;
    if (id) msgDiv.id = id;

    msgDiv.innerHTML = `<div class="msg-bubble">${escapeHtml(text)}</div>`;
    chatMessages.appendChild(msgDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  function generateAIAnswer(prompt) {
    const p = prompt.toLowerCase();
    if (p.includes('master theorem') || p.includes('recurrence')) {
      return `<strong>Master Theorem:</strong> Solves recurrences $T(n) = aT(n/b) + f(n)$.<br>• Compare $f(n)$ with $n^{\\log_b a}$.<br>• Case 1: If $f(n) = O(n^{\\log_b a - \\varepsilon}) \\Rightarrow T(n) = \\Theta(n^{\\log_b a})$.<br>• Case 2: If $f(n) = \\Theta(n^{\\log_b a} \\log^k n) \\Rightarrow T(n) = \\Theta(n^{\\log_b a} \\log^{k+1} n)$.`;
    }
    if (p.includes('avl') || p.includes('rotation') || p.includes('tree')) {
      return `<strong>AVL Trees:</strong> Every node has Balance Factor $BF = H_{left} - H_{right} \\in \\{-1, 0, 1\\}$.<br>When $|BF| > 1$, rebalance via 4 rotation types:<br>1. <strong>LL Rotation:</strong> Single right rotate at node.<br>2. <strong>RR Rotation:</strong> Single left rotate.<br>3. <strong>LR Rotation:</strong> Left rotate left child, then right rotate node.<br>4. <strong>RL Rotation:</strong> Right rotate right child, then left rotate node.`;
    }
    if (p.includes('linked list') || p.includes('reverse')) {
      return `<strong>In-Place Singly Linked List Reversal:</strong><br>Use three pointers: <code>prev = NULL, curr = head, next = NULL</code>.<br>Loop: <code>next = curr->next; curr->next = prev; prev = curr; curr = next;</code><br>Returns <code>prev</code> as new head in $O(n)$ time and $O(1)$ memory!`;
    }
    if (p.includes('knapsack')) {
      return `<strong>0/1 Knapsack:</strong> Uses Dynamic Programming matrix $V[i, w]$ where item $i$ can either be included ($v_i + V[i-1, w-w_i]$) or excluded ($V[i-1, w]$). Time: $O(n \\times W)$.`;
    }
    return `In RGPV B.Tech exams, examiners award maximum step-marks when you state the algorithm's time complexity, draw illustrative diagrams (like tree rotations or recursion trees), and write clear comments. How else can I guide your preparation?`;
  }
}

// =====================================================
// PROFILE & USERS MODAL HANDLERS
// =====================================================
function initProfileAndAdminModals() {
  const profileBtn = document.getElementById('profile-btn');
  const dropdownMenu = document.getElementById('profile-dropdown-menu');
  const pdmLogoutBtn = document.getElementById('pdm-logout-btn');
  const sidebarLogoutBtn = document.getElementById('sidebar-logout-btn');
  const pdmProfileLink = document.getElementById('pdm-profile-link');
  const pdmAdminLink = document.getElementById('pdm-admin-link');
  const profileModal = document.getElementById('profile-modal');
  const btnCloseProfile = document.getElementById('btn-close-profile-modal');

  profileBtn?.addEventListener('click', (e) => {
    e.stopPropagation();
    dropdownMenu?.classList.toggle('show');
  });

  document.addEventListener('click', (e) => {
    if (!dropdownMenu?.contains(e.target) && !profileBtn?.contains(e.target)) {
      dropdownMenu?.classList.remove('show');
    }
  });

  function doSignOut() {
    dropdownMenu?.classList.remove('show');
    clearSession();
    renderUnauthenticatedView();
    showToast('👋 You have been safely signed out.');
  }

  pdmLogoutBtn?.addEventListener('click', doSignOut);
  sidebarLogoutBtn?.addEventListener('click', doSignOut);

  pdmProfileLink?.addEventListener('click', () => {
    dropdownMenu?.classList.remove('show');
    openProfileModal();
  });

  btnCloseProfile?.addEventListener('click', () => {
    if (profileModal) profileModal.style.display = 'none';
  });

  // Admin users modal
  const usersModal = document.getElementById('users-modal');
  const btnOpenUsers = document.getElementById('btn-admin-manage-users');
  const btnCloseUsers = document.getElementById('btn-close-users-modal');

  btnOpenUsers?.addEventListener('click', openUsersModal);
  pdmAdminLink?.addEventListener('click', () => {
    dropdownMenu?.classList.remove('show');
    openUsersModal();
  });
  btnCloseUsers?.addEventListener('click', () => {
    if (usersModal) usersModal.style.display = 'none';
  });

  usersModal?.addEventListener('click', (e) => {
    if (e.target === usersModal) usersModal.style.display = 'none';
  });
}

function openProfileModal() {
  const modal = document.getElementById('profile-modal');
  const content = document.getElementById('profile-modal-content');
  if (!modal || !content) return;

  if (!currentUser) {
    const session = getStoredSession();
    currentUser = session?.user || {
      id: 1,
      full_name: 'Himanshu',
      email: 'himanshu@rgpvexammate.edu',
      role: 'student'
    };
  }

  const role = currentUser.role || 'student';
  const isAdmin = role === 'admin' || (currentUser.email && currentUser.email.toLowerCase().includes('admin'));

  content.innerHTML = `
    <div class="pm-row"><span>Full Name</span><strong>${escapeHtml(currentUser.full_name || (isAdmin ? 'RGPV Administrator' : 'Himanshu'))}</strong></div>
    <div class="pm-row"><span>ID / Email</span><strong>${escapeHtml(currentUser.email || (isAdmin ? 'Admin123' : 'himanshu@rgpvexammate.edu'))}</strong></div>
    <div class="pm-row"><span>Role</span><strong><span class="user-role-badge role-${isAdmin ? 'admin' : role}">${isAdmin ? 'ADMINISTRATOR' : role.toUpperCase()}</span></strong></div>
    <div class="pm-row"><span>Account Status</span><strong style="color:#10b981;">● Active Verified</strong></div>
    <div class="pm-row"><span>University</span><strong>Rajiv Gandhi Proudyogiki Vishwavidyalaya</strong></div>
    <div class="pm-row"><span>Curriculum</span><strong>B.Tech CBGS-2024 Scheme</strong></div>
    <div class="pm-row"><span>Current Streak</span><strong style="color:#f59e0b;">🔥 6 Days Active</strong></div>
  `;
  modal.style.display = 'flex';
}

function closeProfileModal() {
  const modal = document.getElementById('profile-modal');
  if (modal) modal.style.display = 'none';
}

async function openUsersModal() {
  const modal = document.getElementById('users-modal');
  const modalBody = document.getElementById('users-modal-body');
  if (!modal || !modalBody) return;

  modal.style.display = 'flex';
  modalBody.innerHTML = `
    <div class="modal-loader">
      <div class="loader-spinner"></div>
      <span>Querying database for registered users…</span>
    </div>
  `;

  const session = getStoredSession();
  const token = session?.token || '';

  try {
    const res = await fetch(`${API_BASE}/api/v1/auth/users`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });

    if (res.ok) {
      const users = await res.json();
      renderUsersTable(users, modalBody);
    } else {
      renderUsersTable(getMockUsersList(), modalBody);
    }
  } catch (err) {
    renderUsersTable(getMockUsersList(), modalBody);
  }
}

function renderUsersTable(users, container) {
  if (!users || !users.length) {
    container.innerHTML = '<p style="text-align:center; color:#8fa3bf; padding:30px;">No registered users found.</p>';
    return;
  }

  let rows = users.map(u => {
    const roleTagClass = u.role === 'admin' ? 'admin' : (u.role === 'contributor' ? 'contributor' : 'student');
    const createdDate = u.created_at ? new Date(u.created_at).toLocaleDateString() : 'Active';
    return `
      <tr>
        <td>#${u.id}</td>
        <td><strong>${escapeHtml(u.full_name)}</strong></td>
        <td>${escapeHtml(u.email)}</td>
        <td><span class="badge-tag ${roleTagClass}">${u.role}</span></td>
        <td><span style="color: ${u.is_active ? '#34d399' : '#f87171'}">● ${u.is_active ? 'Active' : 'Deactivated'}</span></td>
        <td>${createdDate}</td>
      </tr>
    `;
  }).join('');

  container.innerHTML = `
    <div style="overflow-x:auto;">
      <table class="users-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Email</th>
            <th>Role</th>
            <th>Status</th>
            <th>Joined</th>
          </tr>
        </thead>
        <tbody>
          ${rows}
        </tbody>
      </table>
    </div>
  `;
}

function getMockUsersList() {
  return [
    { id: 1, full_name: 'RGPV Administrator (Admin123)', email: 'Admin123', role: 'admin', is_active: true, created_at: '2024-01-10' },
    { id: 2, full_name: 'Prof. Sharma (Reviewer)', email: 'reviewer@rgpvexammate.edu', role: 'reviewer', is_active: true, created_at: '2024-01-12' },
    { id: 3, full_name: 'Aman Verma (Contributor)', email: 'contributor@rgpvexammate.edu', role: 'contributor', is_active: true, created_at: '2024-02-01' },
    { id: 4, full_name: 'Priya Patel (Student)', email: 'student@rgpvexammate.edu', role: 'student', is_active: true, created_at: '2024-02-15' },
  ];
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str).replace(/[&<>"']/g, (m) => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;',
  }[m]));
}

// ── Low-Poly Faceted Geometric Polygon Background ──
(function initPolygonBackground() {
  const canvas = document.getElementById('bg-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  let width, height;
  let points = [];
  let triangles = [];

  const FACET_COLORS = [
    [7, 18, 42],
    [10, 24, 54],
    [13, 31, 68],
    [16, 38, 82],
    [9, 21, 48],
    [18, 44, 96],
    [6, 15, 34],
    [14, 33, 72],
  ];

  function resize() {
    width = canvas.width = window.innerWidth;
    height = canvas.height = window.innerHeight;
    generateMesh();
  }

  function generateMesh() {
    const spacing = 180;
    const cols = Math.ceil(width / spacing) + 2;
    const rows = Math.ceil(height / spacing) + 2;
    points = [];

    for (let r = 0; r <= rows; r++) {
      for (let c = 0; c <= cols; c++) {
        const baseX = (c - 0.5) * spacing;
        const baseY = (r - 0.5) * spacing;
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

    triangles = [];
    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
        const i0 = r * (cols + 1) + c;
        const i1 = i0 + 1;
        const i2 = (r + 1) * (cols + 1) + c;
        const i3 = i2 + 1;

        const colorIndex1 = (r * 3 + c * 5) % FACET_COLORS.length;
        const colorIndex2 = (r * 7 + c * 2 + 1) % FACET_COLORS.length;

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

    for (const p of points) {
      p.x += p.vx;
      p.y += p.vy;
      if (Math.abs(p.x - p.originX) > 40) p.vx *= -1;
      if (Math.abs(p.y - p.originY) > 40) p.vy *= -1;
    }

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
      showToast('⚠️ Please upload a valid PDF syllabus file.');
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
          uploadLbl.textContent = 'Parsing RGPV units & topics with AI…';
          setTimeout(() => {
            uploadProgress.style.display = 'none';
            showToast(`✅ "${file.name}" indexed! New syllabus units added.`);
          }, 900);
        } else {
          uploadFill.style.width = progress + '%';
        }
      }, 150);
    }
  }
})();

// ── Upload Materials quick action button ──
document.getElementById('btn-upload-materials')?.addEventListener('click', () => {
  document.getElementById('file-input')?.click();
});

// ── Expose Modal Functions to Window for direct onclick access ──
window.openQuizModal = openQuizModal;
window.closeQuizModal = closeQuizModal;
window.openStudyModal = openStudyModal;
window.closeStudyModal = closeStudyModal;
window.openProfileModal = openProfileModal;
window.closeProfileModal = closeProfileModal;
window.openUsersModal = openUsersModal;

// ── Global Click Delegator (Failsafe across all dynamic elements) ──
document.addEventListener('click', (e) => {
  // 1. Profile clicks (top bar button, avatar, name, sidebar badge, dropdown item)
  if (e.target.closest('#profile-btn, #topbar-avatar, #profile-compact-name, #sidebar-user-badge, #pdm-profile-link, [data-action="profile"]')) {
    e.preventDefault();
    openProfileModal();
    return;
  }

  // 2. Quiz clicks
  const quizBtn = e.target.closest('.btn-quiz, #btn-random-quiz, #quiz-ds, #quiz-ada, #btn-practice-quick, #btn-practice-avl, #btn-practice-ada, [data-action="quiz"]');
  if (quizBtn) {
    e.preventDefault();
    const subject = quizBtn.getAttribute('data-subject') || 'RGPV Exam Quiz';
    openQuizModal(subject);
    return;
  }

  // 3. Study clicks
  const studyBtn = e.target.closest('.btn-study, #btn-start-study, #study-ds, #study-ada, [data-action="study"]');
  if (studyBtn) {
    if (studyBtn.id === 'btn-study-prev' || studyBtn.id === 'btn-study-next') {
      return; // handled by study reader navigation
    }
    e.preventDefault();
    const subject = studyBtn.getAttribute('data-subject') || 'RGPV Core Modules';
    openStudyModal(subject);
    return;
  }

  // 4. Close buttons
  if (e.target.closest('.modal-close-btn, #btn-close-profile-modal, #btn-close-quiz-modal, #btn-close-study-modal, #btn-close-users-modal')) {
    e.preventDefault();
    closeProfileModal();
    closeQuizModal();
    closeStudyModal();
    const usersModal = document.getElementById('users-modal');
    if (usersModal) usersModal.style.display = 'none';
    return;
  }

  // 5. Click outside modal-card on modal backdrop closes it
  if (e.target.classList.contains('modal-backdrop')) {
    e.target.style.display = 'none';
    if (quizTimerInterval) clearInterval(quizTimerInterval);
  }
});

// ── Admin Year Tabs Switcher ──
function initAdminYearTabs() {
  document.querySelectorAll('#admin-year-tabs .year-tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const year = btn.getAttribute('data-year');
      document.querySelectorAll('#admin-year-tabs .year-tab-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      document.querySelectorAll('.admin-year-content').forEach(content => {
        content.style.display = 'none';
      });

      const activeYearContent = document.getElementById(`ayc-year-${year}`);
      if (activeYearContent) activeYearContent.style.display = 'block';
    });
  });
}

// =====================================================
// CONTRIBUTOR DASHBOARD CONTROLLER
// =====================================================
function loadContributorDashboard() {
  const session = getStoredSession();
  if (!session || !session.token) return;

  // 1. Fetch contributor stats
  fetch(`${API_BASE}/api/v1/submissions/stats/contributor`, {
    headers: { 'Authorization': `Bearer ${session.token}` }
  })
    .then(res => res.ok ? res.json() : null)
    .then(stats => {
      if (stats) {
        const setVal = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val; };
        setVal('contrib-val-total', stats.total_submissions);
        setVal('contrib-val-pending', stats.pending);
        setVal('contrib-val-inreview', stats.in_review);
        setVal('contrib-val-approved', stats.approved);
        setVal('contrib-val-rejected', (stats.rejected || 0) + (stats.changes_requested || 0));
      }
    })
    .catch(err => console.error('Contributor stats error:', err));

  // 2. Fetch subject list for dropdown
  fetch(`${API_BASE}/api/v1/academic/subjects`, {
    headers: { 'Authorization': `Bearer ${session.token}` }
  })
    .then(res => res.ok ? res.json() : [])
    .then(subjects => {
      const select = document.getElementById('contrib-subject-id');
      if (select && subjects.length > 0) {
        select.innerHTML = '<option value="">Select RGPV Subject...</option>' +
          subjects.map(s => `<option value="${s.id}">${s.code} - ${s.name} (Sem ${s.semester_number})</option>`).join('');
      }
    })
    .catch(err => console.error('Subjects fetch error:', err));

  // 3. Fetch personal submissions
  fetch(`${API_BASE}/api/v1/submissions/mine`, {
    headers: { 'Authorization': `Bearer ${session.token}` }
  })
    .then(res => res.ok ? res.json() : [])
    .then(submissions => {
      const tbody = document.getElementById('contrib-submissions-tbody');
      if (!tbody) return;
      if (submissions.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" style="text-align:center; padding:20px; color:#8fa3bf;">No submissions yet. Submit your first question paper above!</td></tr>';
        return;
      }
      tbody.innerHTML = submissions.map(s => {
        const statusClass = `status-${s.status}`;
        const canResubmit = s.status === 'returned_for_correction' || s.status === 'rejected';
        return `
          <tr>
            <td>#${s.id}</td>
            <td><strong>${s.subject ? s.subject.code : ('Subj #' + s.subject_id)}</strong></td>
            <td>${s.exam_year} ${s.exam_session} (${s.exam_type})</td>
            <td><span class="status-badge ${statusClass}">${s.status.replace(/_/g, ' ')}</span></td>
            <td>${s.reviewer_notes ? `<span style="color:#fbbf24;">${s.reviewer_notes}</span>` : '<span style="color:#64748b;">No feedback yet</span>'}</td>
            <td>${new Date(s.created_at).toLocaleDateString()}</td>
            <td>
              <div style="display:flex; gap:6px;">
                <button type="button" class="action-btn-sm btn-edit" onclick="viewSubmissionPDF(${s.id})">PDF</button>
                ${canResubmit ? `<button type="button" class="action-btn-sm btn-publish" onclick="openContributorResubmitModal(${s.id})">Resubmit</button>` : ''}
              </div>
            </td>
          </tr>
        `;
      }).join('');
    })
    .catch(err => {
      console.error('My submissions error:', err);
      const tbody = document.getElementById('contrib-submissions-tbody');
      if (tbody) tbody.innerHTML = '<tr><td colspan="7" style="text-align:center; padding:20px; color:#f87171;">Failed to load submissions.</td></tr>';
    });
}

function viewSubmissionPDF(submissionId) {
  const session = getStoredSession();
  if (!session || !session.token) return;
  window.open(`${API_BASE}/api/v1/submissions/${submissionId}/file`, '_blank');
}

function openContributorResubmitModal(subId) {
  const modal = document.getElementById('contributor-resubmit-modal');
  const inputId = document.getElementById('crm-submission-id');
  if (inputId) inputId.value = subId;
  if (modal) modal.style.display = 'flex';
}

function closeContributorResubmitModal() {
  const modal = document.getElementById('contributor-resubmit-modal');
  if (modal) modal.style.display = 'none';
}

function submitPaperResubmission() {
  const session = getStoredSession();
  const subId = document.getElementById('crm-submission-id')?.value;
  const notes = document.getElementById('crm-notes')?.value || '';
  if (!session || !subId) return;

  const formData = new FormData();
  formData.append('notes', notes);

  fetch(`${API_BASE}/api/v1/submissions/${subId}/resubmit`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${session.token}` },
    body: formData
  })
    .then(res => {
      if (res.ok) return res.json();
      return res.json().then(e => { throw new Error(e.detail || 'Resubmission failed'); });
    })
    .then(data => {
      showToast(data.message || 'Paper resubmitted successfully!');
      closeContributorResubmitModal();
      loadContributorDashboard();
    })
    .catch(err => {
      showToast(`Error: ${err.message}`);
    });
}

// =====================================================
// REVIEWER DASHBOARD CONTROLLER
// =====================================================
function loadReviewerDashboard() {
  const session = getStoredSession();
  if (!session || !session.token) return;

  // 1. Fetch reviewer stats
  fetch(`${API_BASE}/api/v1/submissions/stats/reviewer`, {
    headers: { 'Authorization': `Bearer ${session.token}` }
  })
    .then(res => res.ok ? res.json() : null)
    .then(stats => {
      if (stats) {
        const setVal = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val; };
        setVal('rev-val-pending', stats.pending_review);
        setVal('rev-val-inreview', stats.in_review);
        setVal('rev-val-approved', stats.approved);
        setVal('rev-val-flagged', stats.flagged);
        setVal('rev-val-turnaround', `${stats.avg_turnaround_hours || 12.5} hrs`);
      }
    })
    .catch(err => console.error('Reviewer stats error:', err));

  // 2. Fetch review queue
  fetch(`${API_BASE}/api/v1/submissions/pending`, {
    headers: { 'Authorization': `Bearer ${session.token}` }
  })
    .then(res => res.ok ? res.json() : [])
    .then(queue => {
      const tbody = document.getElementById('reviewer-queue-tbody');
      if (!tbody) return;
      if (queue.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" style="text-align:center; padding:20px; color:#8fa3bf;">🎉 All caught up! No submissions waiting in review queue.</td></tr>';
        return;
      }
      tbody.innerHTML = queue.map(item => `
        <tr>
          <td>#${item.id}</td>
          <td>${item.submitter ? item.submitter.full_name : ('User #' + item.user_id)}</td>
          <td><strong>${item.subject ? item.subject.code : ('Subj #' + item.subject_id)}</strong></td>
          <td>${item.exam_year} ${item.exam_session} (${item.exam_type})</td>
          <td><span class="status-badge status-${item.status}">${item.status.replace(/_/g, ' ')}</span></td>
          <td>${item.is_flagged ? '🚩 Yes' : 'No'}</td>
          <td>${new Date(item.created_at).toLocaleDateString()}</td>
          <td>
            <button type="button" class="action-btn grad-cyan" style="padding:4px 10px; font-size:0.75rem;" onclick="openReviewerWorkspace(${item.id})">Inspect &amp; Review</button>
          </td>
        </tr>
      `).join('');
    })
    .catch(err => {
      console.error('Review queue error:', err);
      const tbody = document.getElementById('reviewer-queue-tbody');
      if (tbody) tbody.innerHTML = '<tr><td colspan="8" style="text-align:center; padding:20px; color:#f87171;">Failed to load review queue.</td></tr>';
    });
}

function openReviewerWorkspace(submissionId) {
  const session = getStoredSession();
  if (!session || !session.token) return;

  fetch(`${API_BASE}/api/v1/submissions/${submissionId}`, {
    headers: { 'Authorization': `Bearer ${session.token}` }
  })
    .then(res => {
      if (res.ok) return res.json();
      throw new Error('Failed to load submission detail');
    })
    .then(data => {
      const modal = document.getElementById('reviewer-workspace-modal');
      const inputId = document.getElementById('rwm-submission-id');
      if (inputId) inputId.value = data.id;

      const subEl = document.getElementById('rwm-subject');
      if (subEl) subEl.textContent = `${data.subject_code} - ${data.subject_name}`;

      const sessEl = document.getElementById('rwm-session');
      if (sessEl) sessEl.textContent = `${data.exam_session} ${data.exam_year} (${data.exam_type}) • ${data.scheme_name}`;

      const contribEl = document.getElementById('rwm-contributor');
      if (contribEl) contribEl.textContent = data.submitter ? `${data.submitter.full_name} (${data.submitter.email})` : 'Unknown Contributor';

      const csEl = document.getElementById('rwm-checksum');
      if (csEl) csEl.textContent = `SHA-256 Checksum: ${data.checksum || 'N/A'}`;

      const pdfLink = document.getElementById('rwm-pdf-link');
      if (pdfLink) pdfLink.href = `${API_BASE}/api/v1/submissions/${data.id}/file`;

      const remarksEl = document.getElementById('rwm-remarks');
      if (remarksEl) remarksEl.value = data.reviewer_notes || '';

      if (modal) modal.style.display = 'flex';
    })
    .catch(err => showToast(`Error: ${err.message}`));
}

function closeReviewerWorkspace() {
  const modal = document.getElementById('reviewer-workspace-modal');
  if (modal) modal.style.display = 'none';
}

function submitReviewDecision(decision) {
  const session = getStoredSession();
  const subId = document.getElementById('rwm-submission-id')?.value;
  const remarks = document.getElementById('rwm-remarks')?.value.trim() || '';

  if (!session || !subId) return;

  if ((decision === 'rejected' || decision === 'returned_for_correction') && remarks.length < 3) {
    showToast('Decision feedback / reason is mandatory when requesting changes or rejecting.');
    return;
  }

  fetch(`${API_BASE}/api/v1/submissions/${subId}/review`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${session.token}`
    },
    body: JSON.stringify({
      decision: decision,
      remarks: remarks || 'Verified and approved for publication to question bank.'
    })
  })
    .then(res => {
      if (res.ok) return res.json();
      return res.json().then(e => { throw new Error(e.detail || 'Review submission failed'); });
    })
    .then(data => {
      showToast(data.message || 'Review decision submitted successfully!');
      closeReviewerWorkspace();
      loadReviewerDashboard();
    })
    .catch(err => showToast(`Error: ${err.message}`));
}

function submitReviewFlag() {
  const session = getStoredSession();
  const subId = document.getElementById('rwm-submission-id')?.value;
  const remarks = document.getElementById('rwm-remarks')?.value.trim();

  if (!session || !subId) return;
  if (!remarks || remarks.length < 3) {
    showToast('Please enter the reason for flagging this submission in the feedback field.');
    return;
  }

  const formData = new FormData();
  formData.append('reason', remarks);

  fetch(`${API_BASE}/api/v1/submissions/${subId}/flag`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${session.token}` },
    body: formData
  })
    .then(res => {
      if (res.ok) return res.json();
      return res.json().then(e => { throw new Error(e.detail || 'Flagging failed'); });
    })
    .then(data => {
      showToast(data.message || 'Submission flagged for further investigation.');
      closeReviewerWorkspace();
      loadReviewerDashboard();
    })
    .catch(err => showToast(`Error: ${err.message}`));
}

// =====================================================
// ADMIN GOVERNANCE CONSOLE CONTROLLER
// =====================================================
function initAdminSubnav() {
  const pills = document.querySelectorAll('#admin-subnav-tabs .admin-subnav-pill');
  pills.forEach(pill => {
    pill.addEventListener('click', () => {
      pills.forEach(p => p.classList.remove('active'));
      pill.classList.add('active');

      const tab = pill.getAttribute('data-tab');
      document.querySelectorAll('.admin-subview').forEach(v => v.style.display = 'none');

      const targetView = document.getElementById(`admin-subview-${tab}`);
      if (targetView) targetView.style.display = 'block';

      // Load data corresponding to the selected tab
      switch (tab) {
        case 'overview': loadAdminOverview(); break;
        case 'users': loadAdminUsers(); break;
        case 'workload': loadAdminWorkload(); break;
        case 'papers': loadAdminPapers(); break;
        case 'subjects': loadAdminSubjects(); break;
        case 'moderation': loadAdminModeration(); break;
        case 'analytics': loadAdminAnalytics(); break;
        case 'announcements': loadAdminAnnouncements(); break;
        case 'audit': loadAdminAuditLogs(); break;
        case 'health': loadAdminHealth(); break;
      }
    });
  });

  // Admin Export CSV trigger
  const exportBtn = document.getElementById('btn-export-admin-csv');
  if (exportBtn) {
    exportBtn.addEventListener('click', () => {
      const session = getStoredSession();
      if (!session || !session.token) return;
      window.open(`${API_BASE}/api/v1/admin/analytics/export`, '_blank');
      showToast('Generating platform administrative CSV report...');
    });
  }

  // Bind Open Subject Modal Trigger
  const openSubjectBtn = document.getElementById('btn-open-add-subject-modal');
  if (openSubjectBtn) {
    openSubjectBtn.addEventListener('click', openAddSubjectModal);
  }

  // Bind Open Announcement Modal Trigger
  const openAnnBtn = document.getElementById('btn-open-create-announcement-modal');
  if (openAnnBtn) {
    openAnnBtn.addEventListener('click', openCreateAnnouncementModal);
  }

  // Refresh buttons
  const bindRefresh = (id, fn) => {
    const btn = document.getElementById(id);
    if (btn) btn.addEventListener('click', fn);
  };
  bindRefresh('btn-refresh-admin-users', loadAdminUsers);
  bindRefresh('btn-refresh-admin-reviewers', loadAdminWorkload);
  bindRefresh('btn-refresh-admin-contributors', loadAdminWorkload);
  bindRefresh('btn-refresh-admin-papers', loadAdminPapers);
  bindRefresh('btn-refresh-admin-coverage', loadAdminSubjects);
  bindRefresh('btn-refresh-admin-moderation', loadAdminModeration);
  bindRefresh('btn-refresh-admin-audit', loadAdminAuditLogs);
  bindRefresh('btn-refresh-admin-health', loadAdminHealth);
  bindRefresh('btn-refresh-contrib-submissions', loadContributorDashboard);
  bindRefresh('btn-refresh-review-queue', loadReviewerDashboard);

  // Forms
  const subjectForm = document.getElementById('form-admin-add-subject');
  if (subjectForm) {
    subjectForm.addEventListener('submit', (e) => {
      e.preventDefault();
      submitAddSubject();
    });
  }

  const annForm = document.getElementById('form-create-announcement');
  if (annForm) {
    annForm.addEventListener('submit', (e) => {
      e.preventDefault();
      submitCreateAnnouncement();
    });
  }

  const contribForm = document.getElementById('contrib-submission-form');
  if (contribForm) {
    contribForm.addEventListener('submit', handleContributorSubmission);
  }
}

function loadAdminOverview() {
  const session = getStoredSession();
  if (!session || !session.token) return;

  fetch(`${API_BASE}/api/v1/admin/overview`, {
    headers: { 'Authorization': `Bearer ${session.token}` }
  })
    .then(res => res.ok ? res.json() : null)
    .then(data => {
      if (!data) return;
      const setVal = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val; };
      setVal('adm-val-users', Number(data.total_users).toLocaleString());
      setVal('adm-val-active', Number(data.active_students).toLocaleString());
      setVal('adm-val-papers', `${data.approved_papers} Papers (${data.verified_questions} Questions)`);
      setVal('adm-val-pass', `${data.total_subjects} Subjects / ${data.total_units} Units`);
    })
    .catch(err => console.error('Admin overview error:', err));
}

function loadAdminUsers() {
  const session = getStoredSession();
  if (!session || !session.token) return;

  const search = document.getElementById('adm-users-search')?.value || '';
  const role = document.getElementById('adm-users-filter-role')?.value || '';

  let url = `${API_BASE}/api/v1/admin/users?`;
  if (search) url += `search=${encodeURIComponent(search)}&`;
  if (role) url += `role=${encodeURIComponent(role)}&`;

  fetch(url, { headers: { 'Authorization': `Bearer ${session.token}` } })
    .then(res => res.ok ? res.json() : [])
    .then(users => {
      const tbody = document.getElementById('adm-users-tbody');
      if (!tbody) return;
      if (users.length === 0) {
        tbody.innerHTML = '<tr><td colspan="9" style="text-align:center; padding:20px; color:#8fa3bf;">No users match your criteria.</td></tr>';
        return;
      }
      tbody.innerHTML = users.map(u => `
        <tr>
          <td>#${u.id}</td>
          <td><strong>${u.full_name}</strong></td>
          <td>${u.email}</td>
          <td>
            <select class="admin-filter-select" onchange="changeUserRole(${u.id}, this.value)" style="font-size:0.75rem; padding:3px 6px;">
              <option value="student" ${u.role === 'student' ? 'selected' : ''}>Student</option>
              <option value="contributor" ${u.role === 'contributor' ? 'selected' : ''}>Contributor</option>
              <option value="reviewer" ${u.role === 'reviewer' ? 'selected' : ''}>Reviewer</option>
              <option value="admin" ${u.role === 'admin' ? 'selected' : ''}>Admin</option>
            </select>
          </td>
          <td>
            <label style="display:inline-flex; align-items:center; gap:4px; cursor:pointer;">
              <input type="checkbox" ${u.is_active ? 'checked' : ''} onchange="toggleUserStatus(${u.id}, this.checked)" />
              <span style="font-size:0.75rem; color:${u.is_active ? '#34d399' : '#f87171'};">${u.is_active ? 'Active' : 'Disabled'}</span>
            </label>
          </td>
          <td>${u.submissions_count}</td>
          <td>${u.reviews_count}</td>
          <td>${new Date(u.created_at).toLocaleDateString()}</td>
          <td>
            <button type="button" class="action-btn-sm btn-edit" onclick="viewUserDetails(${u.id})">Profile</button>
          </td>
        </tr>
      `).join('');
    })
    .catch(err => {
      console.error('Admin users error:', err);
      const tbody = document.getElementById('adm-users-tbody');
      if (tbody) tbody.innerHTML = '<tr><td colspan="9" style="text-align:center; padding:20px; color:#f87171;">Failed to load user directory.</td></tr>';
    });
}

function changeUserRole(userId, newRole) {
  const session = getStoredSession();
  if (!session || !session.token) return;

  fetch(`${API_BASE}/api/v1/admin/users/${userId}/role`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${session.token}`
    },
    body: JSON.stringify({ role: newRole })
  })
    .then(res => {
      if (res.ok) return res.json();
      return res.json().then(e => { throw new Error(e.detail || 'Role update failed'); });
    })
    .then(data => {
      showToast(data.message || 'User role updated successfully.');
      loadAdminUsers();
    })
    .catch(err => {
      showToast(`Error: ${err.message}`);
      loadAdminUsers();
    });
}

function toggleUserStatus(userId, isActive) {
  const session = getStoredSession();
  if (!session || !session.token) return;

  fetch(`${API_BASE}/api/v1/admin/users/${userId}/status`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${session.token}`
    },
    body: JSON.stringify({ is_active: isActive })
  })
    .then(res => {
      if (res.ok) return res.json();
      return res.json().then(e => { throw new Error(e.detail || 'Status update failed'); });
    })
    .then(data => {
      showToast(data.message || 'Account status updated.');
      loadAdminUsers();
    })
    .catch(err => {
      showToast(`Error: ${err.message}`);
      loadAdminUsers();
    });
}

function viewUserDetails(userId) {
  const session = getStoredSession();
  if (!session || !session.token) return;

  fetch(`${API_BASE}/api/v1/admin/users/${userId}`, {
    headers: { 'Authorization': `Bearer ${session.token}` }
  })
    .then(res => res.ok ? res.json() : null)
    .then(user => {
      if (!user) return;
      alert(`User Profile: ${user.full_name}\nEmail: ${user.email}\nRole: ${user.role}\nActive: ${user.is_active}\nSubmissions: ${user.submissions.length}\nReviews Completed: ${user.reviews.length}`);
    })
    .catch(err => showToast(`Error: ${err.message}`));
}

function loadAdminWorkload() {
  const session = getStoredSession();
  if (!session || !session.token) return;

  // Reviewers workload
  fetch(`${API_BASE}/api/v1/admin/reviewers`, {
    headers: { 'Authorization': `Bearer ${session.token}` }
  })
    .then(res => res.ok ? res.json() : [])
    .then(reviewers => {
      const tbody = document.getElementById('adm-reviewers-tbody');
      if (!tbody) return;
      tbody.innerHTML = reviewers.map(r => `
        <tr>
          <td>#${r.user_id}</td>
          <td><strong>${r.full_name}</strong></td>
          <td>${r.email}</td>
          <td><span class="status-badge ${r.is_active ? 'status-approved' : 'status-rejected'}">${r.is_active ? 'Active' : 'Inactive'}</span></td>
          <td><strong style="color:#fbbf24;">${r.assigned_pending}</strong></td>
          <td>${r.completed_reviews}</td>
          <td><span style="color:#38bdf8;">${r.assigned_pending > 5 ? 'High Load' : 'Optimal'}</span></td>
        </tr>
      `).join('');
    });

  // Contributors quality
  fetch(`${API_BASE}/api/v1/admin/contributors`, {
    headers: { 'Authorization': `Bearer ${session.token}` }
  })
    .then(res => res.ok ? res.json() : [])
    .then(contributors => {
      const tbody = document.getElementById('adm-contributors-tbody');
      if (!tbody) return;
      tbody.innerHTML = contributors.map(c => `
        <tr>
          <td>#${c.user_id}</td>
          <td><strong>${c.full_name}</strong></td>
          <td>${c.email}</td>
          <td>${c.total_submissions}</td>
          <td><span style="color:#34d399;">${c.approved}</span></td>
          <td><span style="color:#f87171;">${c.rejected}</span></td>
          <td><span style="color:#fbbf24;">${c.pending}</span></td>
          <td><strong>${c.quality_score}%</strong></td>
        </tr>
      `).join('');
    });
}

function loadAdminPapers() {
  const session = getStoredSession();
  if (!session || !session.token) return;

  fetch(`${API_BASE}/api/v1/admin/question-papers`, {
    headers: { 'Authorization': `Bearer ${session.token}` }
  })
    .then(res => res.ok ? res.json() : [])
    .then(papers => {
      const tbody = document.getElementById('adm-papers-tbody');
      if (!tbody) return;
      if (papers.length === 0) {
        tbody.innerHTML = '<tr><td colspan="9" style="text-align:center; padding:20px; color:#8fa3bf;">No question papers found.</td></tr>';
        return;
      }
      tbody.innerHTML = papers.map(p => `
        <tr>
          <td>#${p.id}</td>
          <td><strong>${p.subject_code}</strong></td>
          <td>${p.subject_name}</td>
          <td>${p.exam_year} ${p.exam_session}</td>
          <td>${p.exam_type}</td>
          <td>${p.questions_count} Questions</td>
          <td><span class="status-badge status-${p.verification_status}">${p.verification_status}</span></td>
          <td><span class="status-badge ${p.is_published ? 'status-approved' : 'status-rejected'}">${p.is_published ? 'Published' : 'Hidden'}</span></td>
          <td>
            ${p.is_published
              ? `<button type="button" class="action-btn-sm btn-unpublish" onclick="togglePaperPublish(${p.id}, false)">Unpublish</button>`
              : `<button type="button" class="action-btn-sm btn-publish" onclick="togglePaperPublish(${p.id}, true)">Publish</button>`}
          </td>
        </tr>
      `).join('');
    });
}

function togglePaperPublish(paperId, shouldPublish) {
  const session = getStoredSession();
  if (!session || !session.token) return;
  const endpoint = shouldPublish ? 'publish' : 'unpublish';

  fetch(`${API_BASE}/api/v1/admin/question-papers/${paperId}/${endpoint}`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${session.token}` }
  })
    .then(res => res.ok ? res.json() : res.json().then(e => { throw new Error(e.detail); }))
    .then(data => {
      showToast(data.message || 'Question paper publication updated.');
      loadAdminPapers();
    })
    .catch(err => showToast(`Error: ${err.message}`));
}

function loadAdminSubjects() {
  const session = getStoredSession();
  if (!session || !session.token) return;

  fetch(`${API_BASE}/api/v1/admin/subjects`, {
    headers: { 'Authorization': `Bearer ${session.token}` }
  })
    .then(res => res.ok ? res.json() : [])
    .then(subjects => {
      const tbody = document.getElementById('adm-subjects-tbody');
      if (!tbody) return;
      tbody.innerHTML = subjects.map(s => `
        <tr>
          <td>#${s.id}</td>
          <td><strong>${s.code}</strong></td>
          <td>${s.name}</td>
          <td>Semester ${s.semester_number}</td>
          <td>${s.branch_code}</td>
          <td>${s.credits} Credits</td>
          <td>${s.linked_papers} Papers</td>
          <td>${s.syllabus_units} Units</td>
        </tr>
      `).join('');
    });

  // Syllabus Coverage
  fetch(`${API_BASE}/api/v1/admin/syllabus/coverage`, {
    headers: { 'Authorization': `Bearer ${session.token}` }
  })
    .then(res => res.ok ? res.json() : [])
    .then(coverage => {
      const tbody = document.getElementById('adm-coverage-tbody');
      if (!tbody) return;
      tbody.innerHTML = coverage.map(c => `
        <tr>
          <td><strong>${c.subject_code} - ${c.subject_name}</strong></td>
          <td>Sem ${c.semester}</td>
          <td>${c.units_count} / 5 Units</td>
          <td>${c.topics_count} Topics</td>
          <td>${c.papers_count} Papers</td>
          <td><span class="status-badge ${c.is_complete ? 'status-approved' : 'status-pending'}">${c.is_complete ? '100% Complete' : 'Incomplete'}</span></td>
        </tr>
      `).join('');
    });
}

function openAddSubjectModal() {
  const modal = document.getElementById('admin-add-subject-modal');
  if (modal) modal.style.display = 'flex';
}

function closeAddSubjectModal() {
  const modal = document.getElementById('admin-add-subject-modal');
  if (modal) modal.style.display = 'none';
}

function submitAddSubject() {
  const session = getStoredSession();
  if (!session || !session.token) return;

  const payload = {
    code: document.getElementById('as-code')?.value || '',
    name: document.getElementById('as-name')?.value || '',
    semester_number: parseInt(document.getElementById('as-sem')?.value || '1', 10),
    branch_id: parseInt(document.getElementById('as-branch')?.value || '1', 10),
    scheme_id: parseInt(document.getElementById('as-scheme')?.value || '1', 10),
    credits: parseInt(document.getElementById('as-credits')?.value || '4', 10),
  };

  fetch(`${API_BASE}/api/v1/admin/subjects`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${session.token}`
    },
    body: JSON.stringify(payload)
  })
    .then(res => {
      if (res.ok) return res.json();
      return res.json().then(e => { throw new Error(e.detail || 'Failed to create subject'); });
    })
    .then(data => {
      showToast(data.message || 'Subject created successfully.');
      closeAddSubjectModal();
      loadAdminSubjects();
    })
    .catch(err => showToast(`Error: ${err.message}`));
}

function loadAdminModeration() {
  const session = getStoredSession();
  if (!session || !session.token) return;

  fetch(`${API_BASE}/api/v1/admin/moderation/queue`, {
    headers: { 'Authorization': `Bearer ${session.token}` }
  })
    .then(res => res.ok ? res.json() : [])
    .then(queue => {
      const tbody = document.getElementById('adm-moderation-tbody');
      if (!tbody) return;
      if (queue.length === 0) {
        tbody.innerHTML = '<tr><td colspan="9" style="text-align:center; padding:20px; color:#8fa3bf;">No pending moderation or disputed items.</td></tr>';
        return;
      }
      tbody.innerHTML = queue.map(q => `
        <tr>
          <td>#${q.id}</td>
          <td>${q.submitter_name}</td>
          <td><strong>${q.subject_code}</strong></td>
          <td>${q.exam_year} ${q.exam_session}</td>
          <td><span class="status-badge status-${q.status}">${q.status.replace(/_/g, ' ')}</span></td>
          <td>${q.is_flagged ? '<span style="color:#f87171;">🚩 ' + (q.flag_reason || 'Flagged') + '</span>' : 'No'}</td>
          <td>${q.assigned_reviewer} / ${q.reviewer_notes || 'None'}</td>
          <td>${new Date(q.created_at).toLocaleDateString()}</td>
          <td>
            <div style="display:flex; gap:6px;">
              <button type="button" class="action-btn-sm btn-edit" onclick="openAdminModerationModal(${q.id})">Resolve</button>
              <button type="button" class="action-btn-sm btn-publish" onclick="openAssignReviewerModal(${q.id})">Assign</button>
            </div>
          </td>
        </tr>
      `).join('');
    });
}

function openAdminModerationModal(submissionId) {
  const modal = document.getElementById('admin-moderation-modal');
  const inputId = document.getElementById('amm-submission-id');
  if (inputId) inputId.value = submissionId;
  if (modal) modal.style.display = 'flex';
}

function closeAdminModerationModal() {
  const modal = document.getElementById('admin-moderation-modal');
  if (modal) modal.style.display = 'none';
}

function submitAdminModerationResolution() {
  const session = getStoredSession();
  const subId = document.getElementById('amm-submission-id')?.value;
  const action = document.getElementById('amm-action')?.value;
  const reason = document.getElementById('amm-reason')?.value.trim();

  if (!session || !subId) return;
  if (!reason || reason.length < 3) {
    showToast('Mandatory reason required for administrative resolution.');
    return;
  }

  fetch(`${API_BASE}/api/v1/admin/moderation/${subId}/resolve`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${session.token}`
    },
    body: JSON.stringify({ action: action, reason: reason })
  })
    .then(res => {
      if (res.ok) return res.json();
      return res.json().then(e => { throw new Error(e.detail || 'Resolution failed'); });
    })
    .then(data => {
      showToast(data.message || 'Moderation resolution executed.');
      closeAdminModerationModal();
      loadAdminModeration();
    })
    .catch(err => showToast(`Error: ${err.message}`));
}

function openAssignReviewerModal(submissionId) {
  const modal = document.getElementById('admin-assign-reviewer-modal');
  const inputId = document.getElementById('arm-submission-id');
  if (inputId) inputId.value = submissionId;

  const session = getStoredSession();
  if (session && session.token) {
    fetch(`${API_BASE}/api/v1/admin/reviewers`, {
      headers: { 'Authorization': `Bearer ${session.token}` }
    })
      .then(res => res.ok ? res.json() : [])
      .then(reviewers => {
        const select = document.getElementById('arm-reviewer-select');
        if (select) {
          select.innerHTML = '<option value="">Select Reviewer...</option>' +
            reviewers.map(r => `<option value="${r.user_id}">${r.full_name} (${r.email}) - ${r.assigned_pending} pending</option>`).join('');
        }
      });
  }

  if (modal) modal.style.display = 'flex';
}

function closeAssignReviewerModal() {
  const modal = document.getElementById('admin-assign-reviewer-modal');
  if (modal) modal.style.display = 'none';
}

function submitReviewerAssignment() {
  const session = getStoredSession();
  const subId = parseInt(document.getElementById('arm-submission-id')?.value || '0', 10);
  const revId = parseInt(document.getElementById('arm-reviewer-select')?.value || '0', 10);

  if (!session || !subId || !revId) {
    showToast('Please select a valid reviewer.');
    return;
  }

  fetch(`${API_BASE}/api/v1/admin/reviews/assignments`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${session.token}`
    },
    body: JSON.stringify({ submission_id: subId, reviewer_id: revId })
  })
    .then(res => {
      if (res.ok) return res.json();
      return res.json().then(e => { throw new Error(e.detail || 'Assignment failed'); });
    })
    .then(data => {
      showToast(data.message || 'Reviewer assigned successfully.');
      closeAssignReviewerModal();
      loadAdminModeration();
    })
    .catch(err => showToast(`Error: ${err.message}`));
}

function loadAdminAnalytics() {
  const session = getStoredSession();
  if (!session || !session.token) return;

  fetch(`${API_BASE}/api/v1/admin/analytics/overview`, {
    headers: { 'Authorization': `Bearer ${session.token}` }
  })
    .then(res => res.ok ? res.json() : null)
    .then(data => {
      if (!data) return;
      const cards = document.getElementById('adm-analytics-cards');
      if (cards) {
        cards.innerHTML = `
          <div class="unit-card-mini"><div class="ucm-title">Total Papers In Bank</div><div style="font-size:1.4rem; font-weight:700; color:#fff;">${data.total_papers}</div></div>
          <div class="unit-card-mini"><div class="ucm-title">Verified Questions Indexed</div><div style="font-size:1.4rem; font-weight:700; color:#38bdf8;">${data.total_questions}</div></div>
          <div class="unit-card-mini"><div class="ucm-title">Students / Contributors</div><div style="font-size:1.4rem; font-weight:700; color:#10b981;">${data.user_roles.student || 0} / ${data.user_roles.contributor || 0}</div></div>
          <div class="unit-card-mini"><div class="ucm-title">Reviewers / Admins</div><div style="font-size:1.4rem; font-weight:700; color:#a855f7;">${data.user_roles.reviewer || 0} / ${data.user_roles.admin || 0}</div></div>
        `;
      }
      const tbody = document.getElementById('adm-branch-analytics-tbody');
      if (tbody && data.branch_distribution) {
        tbody.innerHTML = data.branch_distribution.map(b => `
          <tr>
            <td><strong>${b.branch_code}</strong></td>
            <td>${b.branch_name}</td>
            <td>${b.papers_count} Papers</td>
          </tr>
        `).join('');
      }
    });
}

function loadAdminAnnouncements() {
  const session = getStoredSession();
  if (!session || !session.token) return;

  fetch(`${API_BASE}/api/v1/admin/announcements`, {
    headers: { 'Authorization': `Bearer ${session.token}` }
  })
    .then(res => res.ok ? res.json() : [])
    .then(announcements => {
      const container = document.getElementById('adm-announcements-container');
      if (!container) return;
      if (announcements.length === 0) {
        container.innerHTML = '<div style="color:#8fa3bf; text-align:center; padding:20px;">No announcements posted yet. Click "+ Create Announcement" above.</div>';
        return;
      }
      container.innerHTML = announcements.map(a => `
        <div style="background:rgba(15,23,42,0.6); border:1px solid rgba(255,255,255,0.06); border-radius:8px; padding:12px 16px; display:flex; justify-content:space-between; align-items:flex-start;">
          <div>
            <div style="display:flex; align-items:center; gap:8px; margin-bottom:4px;">
              <strong style="color:#fff; font-size:0.9rem;">${a.title}</strong>
              <span class="status-badge status-in_review">${a.audience.toUpperCase()}</span>
            </div>
            <p style="font-size:0.8rem; color:#cbd5e1; margin-bottom:6px;">${a.content}</p>
            <span style="font-size:0.72rem; color:#64748b;">Published: ${new Date(a.published_at).toLocaleString()}</span>
          </div>
          <button type="button" class="trash-btn" onclick="deleteAnnouncement(${a.id})" title="Delete Notice">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/></svg>
          </button>
        </div>
      `).join('');
    });
}

function openCreateAnnouncementModal() {
  const modal = document.getElementById('admin-create-announcement-modal');
  if (modal) modal.style.display = 'flex';
}

function closeCreateAnnouncementModal() {
  const modal = document.getElementById('admin-create-announcement-modal');
  if (modal) modal.style.display = 'none';
}

function submitCreateAnnouncement() {
  const session = getStoredSession();
  if (!session || !session.token) return;

  const payload = {
    title: document.getElementById('ann-title')?.value || '',
    audience: document.getElementById('ann-audience')?.value || 'all',
    content: document.getElementById('ann-content')?.value || '',
  };

  fetch(`${API_BASE}/api/v1/admin/announcements`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${session.token}`
    },
    body: JSON.stringify(payload)
  })
    .then(res => {
      if (res.ok) return res.json();
      return res.json().then(e => { throw new Error(e.detail || 'Announcement creation failed'); });
    })
    .then(data => {
      showToast('Announcement broadcast successfully!');
      closeCreateAnnouncementModal();
      loadAdminAnnouncements();
    })
    .catch(err => showToast(`Error: ${err.message}`));
}

function deleteAnnouncement(annId) {
  const session = getStoredSession();
  if (!session || !session.token) return;

  fetch(`${API_BASE}/api/v1/admin/announcements/${annId}`, {
    method: 'DELETE',
    headers: { 'Authorization': `Bearer ${session.token}` }
  })
    .then(res => res.ok ? res.json() : null)
    .then(() => {
      showToast('Announcement removed.');
      loadAdminAnnouncements();
    });
}

function loadAdminAuditLogs() {
  const session = getStoredSession();
  if (!session || !session.token) return;

  const action = document.getElementById('adm-audit-filter-action')?.value || '';
  let url = `${API_BASE}/api/v1/admin/audit-logs?limit=50&`;
  if (action) url += `action=${encodeURIComponent(action)}&`;

  fetch(url, { headers: { 'Authorization': `Bearer ${session.token}` } })
    .then(res => res.ok ? res.json() : [])
    .then(logs => {
      const tbody = document.getElementById('adm-audit-tbody');
      if (!tbody) return;
      if (logs.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align:center; padding:20px; color:#8fa3bf;">No audit log records found.</td></tr>';
        return;
      }
      tbody.innerHTML = logs.map(l => `
        <tr>
          <td style="font-size:0.75rem; color:#8fa3bf;">${new Date(l.created_at).toLocaleString()}</td>
          <td><strong>${l.actor_name}</strong><br><span style="font-size:0.72rem; color:#64748b;">${l.actor_email}</span></td>
          <td><span class="status-badge status-in_review">${l.action}</span></td>
          <td>${l.entity_type}</td>
          <td>${l.entity_id ? '#' + l.entity_id : '-'}</td>
          <td style="font-size:0.78rem; color:#94a3b8;">${l.details || '-'}</td>
        </tr>
      `).join('');
    });
}

function loadAdminHealth() {
  const session = getStoredSession();
  if (!session || !session.token) return;

  fetch(`${API_BASE}/api/v1/admin/system/health`, {
    headers: { 'Authorization': `Bearer ${session.token}` }
  })
    .then(res => res.ok ? res.json() : null)
    .then(health => {
      const container = document.getElementById('adm-health-container');
      if (!container || !health) return;
      container.innerHTML = `
        <div class="units-grid" style="margin-bottom:16px;">
          <div class="unit-card-mini">
            <div class="ucm-title">Database Status</div>
            <div style="font-size:1.1rem; font-weight:700; color:#34d399;">Connected</div>
            <span style="font-size:0.74rem; color:#8fa3bf;">Latency: ${health.database.latency_ms} ms</span>
          </div>
          <div class="unit-card-mini">
            <div class="ucm-title">Storage & Uploads</div>
            <div style="font-size:1.1rem; font-weight:700; color:#38bdf8;">Max ${health.storage.max_upload_size_mb} MB</div>
            <span style="font-size:0.74rem; color:#8fa3bf;">Permitted: PDF Documents</span>
          </div>
          <div class="unit-card-mini">
            <div class="ucm-title">Access Control (RBAC)</div>
            <div style="font-size:1.1rem; font-weight:700; color:#10b981;">Strictly Enforced</div>
            <span style="font-size:0.74rem; color:#8fa3bf;">JWT Bearer Authentication</span>
          </div>
          <div class="unit-card-mini">
            <div class="ucm-title">Platform Runtime</div>
            <div style="font-size:1.1rem; font-weight:700; color:#fff;">RGPV v1.0.0</div>
            <span style="font-size:0.74rem; color:#8fa3bf;">Environment: ${health.application.environment}</span>
          </div>
        </div>
      `;
    });
}

function handleContributorSubmission(e) {
  e.preventDefault();
  const session = getStoredSession();
  if (!session || !session.token) {
    showToast('Please sign in as Contributor to upload papers.');
    return;
  }

  const subjectId = document.getElementById('contrib-subject-id')?.value;
  const schemeId = document.getElementById('contrib-scheme-id')?.value;
  const year = document.getElementById('contrib-year')?.value;
  const sess = document.getElementById('contrib-session')?.value;
  const type = document.getElementById('contrib-type')?.value;
  const fileInput = document.getElementById('contrib-file');

  if (!subjectId || !schemeId || !year || !sess || !type || !fileInput || !fileInput.files[0]) {
    showToast('Please fill all required fields and select a PDF file.');
    return;
  }

  const formData = new FormData();
  formData.append('subject_id', subjectId);
  formData.append('scheme_id', schemeId);
  formData.append('exam_year', year);
  formData.append('exam_session', sess);
  formData.append('exam_type', type);
  formData.append('file', fileInput.files[0]);

  const spinner = document.getElementById('contrib-submit-spinner');
  if (spinner) spinner.style.display = 'inline-block';

  fetch(`${API_BASE}/api/v1/submissions/`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${session.token}` },
    body: formData
  })
    .then(res => {
      if (spinner) spinner.style.display = 'none';
      if (res.ok) return res.json();
      return res.json().then(e => { throw new Error(e.detail || 'Submission failed'); });
    })
    .then(data => {
      showToast(`Paper submitted successfully! (ID: #${data.id}). Awaiting reviewer queue.`);
      document.getElementById('contrib-submission-form')?.reset();
      loadContributorDashboard();
    })
    .catch(err => {
      if (spinner) spinner.style.display = 'none';
      showToast(`Submission error: ${err.message}`);
    });
}

// ── Contributor Dashboard Controller ──
function loadContributorDashboard() {
  const session = getStoredSession();
  if (!session || !session.token) return;

  // 1. Load contributor metrics
  fetch(`${API_BASE}/api/v1/submissions/stats/contributor`, {
    headers: { 'Authorization': `Bearer ${session.token}` }
  })
    .then(res => res.ok ? res.json() : null)
    .then(stats => {
      if (!stats) return;
      const elTot = document.getElementById('contrib-val-total');
      const elPend = document.getElementById('contrib-val-pending');
      const elInRev = document.getElementById('contrib-val-inreview');
      const elAppr = document.getElementById('contrib-val-approved');
      const elRej = document.getElementById('contrib-val-rejected');

      if (elTot) elTot.textContent = stats.total_submissions;
      if (elPend) elPend.textContent = stats.pending;
      if (elInRev) elInRev.textContent = stats.in_review;
      if (elAppr) elAppr.textContent = stats.approved;
      if (elRej) elRej.textContent = stats.changes_requested + stats.rejected;
    });

  // 2. Populate subject select options if empty
  const subSelect = document.getElementById('contrib-subject-id');
  if (subSelect && subSelect.children.length <= 1) {
    fetch(`${API_BASE}/api/v1/academic/subjects`, {
      headers: { 'Authorization': `Bearer ${session.token}` }
    })
      .then(res => res.ok ? res.json() : [])
      .then(subjects => {
        subSelect.innerHTML = '<option value="">Select RGPV Subject...</option>' +
          subjects.map(s => `<option value="${s.id}">Semester ${s.semester_number} • ${s.code} - ${s.name}</option>`).join('');
      });
  }

  // 3. Load contributor's submissions
  fetch(`${API_BASE}/api/v1/submissions/mine`, {
    headers: { 'Authorization': `Bearer ${session.token}` }
  })
    .then(res => res.ok ? res.json() : [])
    .then(submissions => {
      const tbody = document.getElementById('contributor-submissions-tbody');
      if (!tbody) return;
      if (submissions.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" style="text-align:center; padding:24px; color:#8fa3bf;">No submissions yet. Use the form above to upload an RGPV PYQ.</td></tr>';
        return;
      }
      tbody.innerHTML = submissions.map(s => {
        const statusBadge = `<span class="status-badge status-${s.status}">${s.status.replace(/_/g, ' ').toUpperCase()}</span>`;
        const canResubmit = (s.status === 'returned_for_correction' || s.status === 'rejected');
        return `
          <tr>
            <td><strong>#${s.id}</strong></td>
            <td>Subj #${s.subject_id}</td>
            <td>${s.exam_session} ${s.exam_year}</td>
            <td>${s.exam_type}</td>
            <td>${statusBadge}</td>
            <td style="font-size:0.75rem; color:#8fa3bf;">${new Date(s.created_at).toLocaleDateString()}</td>
            <td>
              <div style="display:flex; gap:6px; flex-wrap:wrap;">
                <button type="button" class="action-btn-sm" style="background:rgba(56,189,248,0.15); color:#38bdf8;" onclick="viewSubmissionPDF(${s.id})">View PDF</button>
                ${canResubmit ? `<button type="button" class="action-btn-sm" style="background:rgba(245,158,11,0.15); color:#fbbf24;" onclick="openContributorResubmitModal(${s.id})">Resubmit</button>` : ''}
              </div>
            </td>
          </tr>
        `;
      }).join('');
    });
}

function viewSubmissionPDF(subId) {
  const session = getStoredSession();
  if (!session || !session.token) return;

  fetch(`${API_BASE}/api/v1/submissions/${subId}/file`, {
    headers: { 'Authorization': `Bearer ${session.token}` }
  })
    .then(res => {
      if (!res.ok) throw new Error('Failed to stream PDF');
      return res.blob();
    })
    .then(blob => {
      const url = URL.createObjectURL(blob);
      window.open(url, '_blank');
    })
    .catch(err => showToast(`Error opening PDF: ${err.message}`));
}

function openContributorResubmitModal(subId) {
  const modal = document.getElementById('contributor-resubmit-modal');
  const idInput = document.getElementById('crm-submission-id');
  if (idInput) idInput.value = subId;
  if (modal) modal.style.display = 'flex';
}

function closeContributorResubmitModal() {
  const modal = document.getElementById('contributor-resubmit-modal');
  if (modal) modal.style.display = 'none';
}

function submitPaperResubmission() {
  const session = getStoredSession();
  if (!session || !session.token) return;
  const subId = document.getElementById('crm-submission-id')?.value;
  const notes = document.getElementById('crm-notes')?.value || '';

  fetch(`${API_BASE}/api/v1/submissions/${subId}/resubmit`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${session.token}`
    },
    body: JSON.stringify({ notes })
  })
    .then(res => {
      if (res.ok) return res.json();
      return res.json().then(e => { throw new Error(e.detail || 'Resubmission failed'); });
    })
    .then(data => {
      showToast('Paper resubmitted successfully for review.');
      closeContributorResubmitModal();
      loadContributorDashboard();
    })
    .catch(err => showToast(`Resubmission error: ${err.message}`));
}

// ── Reviewer Dashboard Controller ──
let cachedReviewerQueue = [];

function loadReviewerDashboard() {
  const session = getStoredSession();
  if (!session || !session.token) return;

  // 1. Load reviewer stats
  fetch(`${API_BASE}/api/v1/submissions/stats/reviewer`, {
    headers: { 'Authorization': `Bearer ${session.token}` }
  })
    .then(res => res.ok ? res.json() : null)
    .then(stats => {
      if (!stats) return;
      const elPend = document.getElementById('rev-val-pending');
      const elInRev = document.getElementById('rev-val-inreview');
      const elAppr = document.getElementById('rev-val-approved');
      const elFlag = document.getElementById('rev-val-flagged');
      const elTurn = document.getElementById('rev-val-turnaround');

      if (elPend) elPend.textContent = stats.pending_review;
      if (elInRev) elInRev.textContent = stats.in_review;
      if (elAppr) elAppr.textContent = stats.approved;
      if (elFlag) elFlag.textContent = stats.flagged;
      if (elTurn) elTurn.textContent = `${stats.avg_turnaround_hours} hrs`;
    });

  // 2. Load pending queue
  fetch(`${API_BASE}/api/v1/submissions/pending`, {
    headers: { 'Authorization': `Bearer ${session.token}` }
  })
    .then(res => res.ok ? res.json() : [])
    .then(items => {
      cachedReviewerQueue = items;
      renderReviewerQueueTable(items);
    });
}

function renderReviewerQueueTable(items) {
  const tbody = document.getElementById('reviewer-queue-tbody');
  if (!tbody) return;

  if (items.length === 0) {
    tbody.innerHTML = '<tr><td colspan="8" style="text-align:center; padding:24px; color:#8fa3bf;">Queue clear! All submitted papers have been reviewed.</td></tr>';
    return;
  }

  tbody.innerHTML = items.map(sub => {
    const statusBadge = `<span class="status-badge status-${sub.status}">${sub.status.replace(/_/g, ' ').toUpperCase()}</span>`;
    const flagBadge = sub.is_flagged ? '<span class="status-badge status-flagged">🚩 FLAGGED</span>' : '<span style="color:#64748b; font-size:0.75rem;">Normal</span>';
    return `
      <tr>
        <td><strong>#${sub.id}</strong></td>
        <td>User #${sub.user_id}</td>
        <td>Subject #${sub.subject_id}</td>
        <td>${sub.exam_session} ${sub.exam_year} (${sub.exam_type})</td>
        <td>${statusBadge}</td>
        <td>${flagBadge}</td>
        <td style="font-size:0.75rem; color:#8fa3bf;">${new Date(sub.created_at).toLocaleString()}</td>
        <td>
          <button type="button" class="action-btn-sm" style="background:rgba(56,189,248,0.15); color:#38bdf8;" onclick="openReviewerWorkspace(${sub.id})">Inspect & Decide</button>
        </td>
      </tr>
    `;
  }).join('');
}

function openReviewerWorkspace(submissionId) {
  const session = getStoredSession();
  if (!session || !session.token) return;

  fetch(`${API_BASE}/api/v1/submissions/${submissionId}`, {
    headers: { 'Authorization': `Bearer ${session.token}` }
  })
    .then(res => {
      if (res.ok) return res.json();
      throw new Error('Failed to load submission details');
    })
    .then(sub => {
      const modal = document.getElementById('reviewer-workspace-modal');
      const subIdInput = document.getElementById('rwm-submission-id');
      const subEl = document.getElementById('rwm-subject');
      const sessEl = document.getElementById('rwm-session');
      const contribEl = document.getElementById('rwm-contributor');
      const checkEl = document.getElementById('rwm-checksum');
      const pdfLink = document.getElementById('rwm-pdf-link');
      const remarksInput = document.getElementById('rwm-remarks');

      if (subIdInput) subIdInput.value = sub.id;
      if (subEl) subEl.textContent = `${sub.subject_code} - ${sub.subject_name}`;
      if (sessEl) sessEl.textContent = `${sub.exam_session} ${sub.exam_year} • Scheme: ${sub.scheme_name} • Type: ${sub.exam_type}`;
      if (contribEl) contribEl.textContent = sub.submitter ? `${sub.submitter.full_name} (${sub.submitter.email})` : `User #${sub.user_id}`;
      if (checkEl) checkEl.textContent = `SHA-256: ${sub.checksum}`;
      if (remarksInput) remarksInput.value = sub.reviewer_notes || '';

      if (pdfLink) {
        pdfLink.onclick = (e) => {
          e.preventDefault();
          viewSubmissionPDF(sub.id);
        };
      }

      if (modal) modal.style.display = 'flex';
    })
    .catch(err => showToast(`Error: ${err.message}`));
}

function closeReviewerWorkspace() {
  const modal = document.getElementById('reviewer-workspace-modal');
  if (modal) modal.style.display = 'none';
}

function submitReviewDecision(decision) {
  const session = getStoredSession();
  if (!session || !session.token) return;

  const subId = document.getElementById('rwm-submission-id')?.value;
  const remarks = document.getElementById('rwm-remarks')?.value?.trim() || '';

  if ((decision === 'rejected' || decision === 'returned_for_correction') && !remarks) {
    showToast('Please enter mandatory feedback remarks for reject or change request.');
    return;
  }

  const payload = {
    decision: decision,
    remarks: remarks || (decision === 'approved' ? 'Verified RGPV exam syllabus alignment and legibility.' : 'Reviewed.')
  };

  fetch(`${API_BASE}/api/v1/submissions/${subId}/review`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${session.token}`
    },
    body: JSON.stringify(payload)
  })
    .then(res => {
      if (res.ok) return res.json();
      return res.json().then(e => { throw new Error(e.detail || 'Review action failed'); });
    })
    .then(data => {
      showToast(`Decision recorded: ${decision.replace(/_/g, ' ').toUpperCase()}`);
      closeReviewerWorkspace();
      loadReviewerDashboard();
    })
    .catch(err => showToast(`Error: ${err.message}`));
}

function submitReviewFlag() {
  const session = getStoredSession();
  if (!session || !session.token) return;

  const subId = document.getElementById('rwm-submission-id')?.value;
  const reason = document.getElementById('rwm-remarks')?.value?.trim();

  if (!reason) {
    showToast('Please provide a reason for flagging this submission.');
    return;
  }

  fetch(`${API_BASE}/api/v1/submissions/${subId}/flag`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${session.token}`
    },
    body: JSON.stringify({ reason })
  })
    .then(res => {
      if (res.ok) return res.json();
      return res.json().then(e => { throw new Error(e.detail || 'Flagging failed'); });
    })
    .then(data => {
      showToast('Submission flagged for administrative moderation.');
      closeReviewerWorkspace();
      loadReviewerDashboard();
    })
    .catch(err => showToast(`Error: ${err.message}`));
}

// ── App Bootstrapper (Fires immediately if DOM already loaded) ──
function bootApp() {
  initAuthControls();
  initDashboardRouting();
  initQuizModalEvents();
  initStudyModalEvents();
  initChatDrawer();
  initProfileAndAdminModals();
  initAdminYearTabs();
  initAdminSubnav();

  // Contributor form listener
  const contribForm = document.getElementById('contrib-submission-form');
  if (contribForm) {
    contribForm.addEventListener('submit', handleContributorSubmission);
  }

  // Reviewer search filter
  const revSearch = document.getElementById('rev-queue-search');
  if (revSearch) {
    revSearch.addEventListener('input', (e) => {
      const q = e.target.value.toLowerCase();
      const filtered = cachedReviewerQueue.filter(item =>
        String(item.id).includes(q) ||
        String(item.exam_year).includes(q) ||
        String(item.exam_session).toLowerCase().includes(q)
      );
      renderReviewerQueueTable(filtered);
    });
  }

  const btnRefreshRev = document.getElementById('btn-refresh-review-queue');
  if (btnRefreshRev) {
    btnRefreshRev.addEventListener('click', loadReviewerDashboard);
  }

  initAuthCheck();
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', bootApp);
} else {
  bootApp();
}

