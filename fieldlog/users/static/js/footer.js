document.addEventListener('DOMContentLoaded', () => {
  const container = document.querySelector('.footer-container');
  const sections = Array.from(document.querySelectorAll('.footer-section'));
  const buttons = document.querySelectorAll('.read-more-btn');

  // Toggle Expand/Collapse content smoothly
  buttons.forEach((btn, idx) => {
    const section = sections[idx];
    const extra = section.querySelector('.extra-content');
    const snippet = section.querySelector('.content-snippet ul');

    btn.addEventListener('click', () => {
      const expanded = extra.classList.contains('expanded');
      if (!expanded) {
        extra.classList.add('expanded');
        btn.classList.add('active');
        btn.innerHTML = `Show Less <i class="fas fa-chevron-up"></i>`;
        snippet.style.maxHeight = '1000px';
      } else {
        extra.classList.remove('expanded');
        btn.classList.remove('active');
        btn.innerHTML = `Read More <i class="fas fa-chevron-down"></i>`;
        snippet.style.maxHeight = '140px';
      }
    });
  });

  // Drag to scroll horizontally
  let isDown = false;
  let startX, scrollLeft;

  container.addEventListener('mousedown', (e) => {
    isDown = true;
    container.classList.add('dragging');
    startX = e.pageX - container.offsetLeft;
    scrollLeft = container.scrollLeft;
  });
  container.addEventListener('mouseleave', () => {
    isDown = false;
    container.classList.remove('dragging');
  });
  container.addEventListener('mouseup', () => {
    isDown = false;
    container.classList.remove('dragging');
  });
  container.addEventListener('mousemove', (e) => {
    if (!isDown) return;
    e.preventDefault();
    const x = e.pageX - container.offsetLeft;
    const walk = (x - startX) * 2; // scroll speed factor
    container.scrollLeft = scrollLeft - walk;
  });

  // Keyboard horizontal navigation with arrow keys
  document.addEventListener('keydown', (e) => {
    if (['INPUT','TEXTAREA'].includes(document.activeElement.tagName)) return;
    if (e.key === 'ArrowRight') {
      container.scrollBy({ left: 320, behavior: 'smooth' });
    } else if (e.key === 'ArrowLeft') {
      container.scrollBy({ left: -320, behavior: 'smooth' });
    }
  });

  // Auto fade out scroll hint after 12 seconds
  const hint = document.querySelector('.scroll-hint');
  if (hint) {
    setTimeout(() => {
      hint.style.transition = 'opacity 1.5s ease';
      hint.style.opacity = '0';
    }, 12000);
  }
});
