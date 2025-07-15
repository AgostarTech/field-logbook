// =========================
// BASE.JS - UI INTERACTIONS
// =========================

// Run when DOM is fully loaded
window.addEventListener('DOMContentLoaded', () => {
  initNavbarToggle();
  initRippleEffect();
  initScrollToTop();
  initFadeIn();
  initDismissMessages();
  initKeyboardShortcuts();
  initTextareaCounter();
  initEnterSubmit();
});

// ======================
// Navbar Mobile Toggle
// ======================
function initNavbarToggle() {
  const toggle = document.getElementById('nav-toggle');
  const nav = document.querySelector('.nav-right');
  if (!toggle || !nav) return;

  toggle.addEventListener('click', () => nav.classList.toggle('active'));

  nav.querySelectorAll('.nav-link, .logout-btn').forEach(link =>
    link.addEventListener('click', () => nav.classList.remove('active'))
  );
}

// ===================
// Ripple Effect
// ===================
function initRippleEffect() {
  document.querySelectorAll('.ripple-container').forEach(container => {
    container.addEventListener('click', e => {
      const ripple = document.createElement('span');
      ripple.className = 'ripple';

      const rect = container.getBoundingClientRect();
      const size = Math.max(rect.width, rect.height);
      ripple.style.width = ripple.style.height = `${size}px`;
      ripple.style.left = `${e.clientX - rect.left - size / 2}px`;
      ripple.style.top = `${e.clientY - rect.top - size / 2}px`;

      container.appendChild(ripple);
      setTimeout(() => ripple.remove(), 600);
    });
  });
}

// ===================
// Scroll To Top
// ===================
function initScrollToTop() {
  const btn = document.createElement('button');
  btn.innerHTML = '↑';
  btn.className = 'scroll-top-btn';
  btn.title = 'Back to top';
  document.body.appendChild(btn);

  btn.style.cssText = `
    position: fixed;
    bottom: 30px;
    right: 30px;
    z-index: 9999;
    background: #1de9b6;
    color: #0f2027;
    border: none;
    border-radius: 50%;
    width: 48px;
    height: 48px;
    font-size: 1.5rem;
    display: none;
    box-shadow: 0 0 12px #1de9b6;
    cursor: pointer;
    transition: transform 0.2s ease;
  `;

  btn.addEventListener('mouseenter', () => btn.style.transform = 'scale(1.1)');
  btn.addEventListener('mouseleave', () => btn.style.transform = 'scale(1)');
  btn.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));

  window.addEventListener('scroll', () => {
    btn.style.display = window.scrollY > 400 ? 'block' : 'none';
  });
}

// ===================
// Fade In Page
// ===================
function initFadeIn() {
  document.body.style.opacity = 0;
  document.body.style.transition = 'opacity 1s ease';
  setTimeout(() => document.body.style.opacity = 1, 50);
}

// ========================
// Auto Dismiss Messages
// ========================
function initDismissMessages() {
  document.querySelectorAll('.message').forEach(msg => {
    setTimeout(() => {
      msg.style.transition = 'opacity 0.5s ease';
      msg.style.opacity = 0;
      setTimeout(() => msg.remove(), 600);
    }, 5000);
  });
}

// ========================
// Keyboard Shortcuts
// ========================
function initKeyboardShortcuts() {
  document.addEventListener('keydown', e => {
    if (e.key === '/') {
      const search = document.getElementById('search');
      if (search) {
        e.preventDefault();
        search.focus();
      }
    }

    if (e.key === 'Escape') {
      document.activeElement.blur();
    }
  });
}

// =============================
// Textarea Character Counter
// =============================
function initTextareaCounter() {
  document.querySelectorAll('textarea[maxlength]').forEach(textarea => {
    const counter = document.createElement('div');
    counter.className = 'char-count';
    textarea.parentElement.appendChild(counter);

    const update = () => {
      const max = textarea.getAttribute('maxlength');
      const val = textarea.value.length;
      counter.textContent = `${val}/${max} characters`;
    };

    textarea.addEventListener('input', update);
    update();
  });
}

// =============================
// Press Enter on Last Input = Submit
// =============================
function initEnterSubmit() {
  document.querySelectorAll('form').forEach(form => {
    const inputs = form.querySelectorAll('input');
    inputs.forEach((input, i) => {
      input.addEventListener('keydown', e => {
        if (e.key === 'Enter' && i === inputs.length - 1) {
          e.preventDefault();
          form.submit();
        }
      });
    });
  });
}
