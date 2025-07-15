document.addEventListener('DOMContentLoaded', () => {
  // You can add interactivity here if needed

  // Example: animate rainbow ring on hover
  const ring = document.querySelector('.rainbow-ring');
  if (ring) {
    ring.addEventListener('mouseenter', () => {
      ring.style.animationPlayState = 'paused';
    });
    ring.addEventListener('mouseleave', () => {
      ring.style.animationPlayState = 'running';
    });
  }
});
