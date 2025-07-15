document.addEventListener('DOMContentLoaded', () => {
  const buttons = document.querySelectorAll('.account-type-list a');

  // Ripple effect on click
  buttons.forEach(btn => {
    btn.addEventListener('click', e => {
      const ripple = document.createElement('span');
      ripple.classList.add('ripple');
      btn.appendChild(ripple);

      const rect = btn.getBoundingClientRect();
      ripple.style.left = `${e.clientX - rect.left}px`;
      ripple.style.top = `${e.clientY - rect.top}px`;

      setTimeout(() => {
        ripple.remove();
      }, 600);
      
      console.log(`User clicked: ${btn.textContent.trim()}`);
    });

    // Keyboard focus styling
    btn.addEventListener('focus', () => {
      btn.classList.add('keyboard-focus');
    });

    btn.addEventListener('blur', () => {
      btn.classList.remove('keyboard-focus');
    });
  });

  // Particle background (canvas-based simple floating dots)
  const container = document.querySelector('.signup-select-container');
  const canvas = document.createElement('canvas');
  canvas.style.position = 'absolute';
  canvas.style.top = 0;
  canvas.style.left = 0;
  canvas.style.width = '100%';
  canvas.style.height = '100%';
  canvas.style.zIndex = -1;
  container.style.position = 'relative';
  container.appendChild(canvas);

  const ctx = canvas.getContext('2d');
  let width, height, particles;

  function init() {
    resize();
    particles = [];
    for (let i = 0; i < 30; i++) {
      particles.push({
        x: Math.random() * width,
        y: Math.random() * height,
        radius: Math.random() * 2 + 1,
        speedX: (Math.random() - 0.5) * 0.5,
        speedY: (Math.random() - 0.5) * 0.5,
      });
    }
    animate();
  }

  function resize() {
    width = canvas.width = container.offsetWidth;
    height = canvas.height = container.offsetHeight;
  }

  window.addEventListener('resize', resize);

  function animate() {
    ctx.clearRect(0, 0, width, height);
    particles.forEach(p => {
      p.x += p.speedX;
      p.y += p.speedY;

      if (p.x < 0 || p.x > width) p.speedX *= -1;
      if (p.y < 0 || p.y > height) p.speedY *= -1;

      ctx.beginPath();
      ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
      ctx.fillStyle = 'rgba(98, 218, 251, 0.7)';
      ctx.fill();
    });
    requestAnimationFrame(animate);
  }

  init();
});
