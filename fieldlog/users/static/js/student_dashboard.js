// student_dashboard.js

document.addEventListener('DOMContentLoaded', () => {
  const welcomeText = document.querySelector('.container p');
  if (welcomeText) {
    welcomeText.classList.add('glow-text');
  }
});

// Optional: glowing animation class
const style = document.createElement('style');
style.innerHTML = `
  .glow-text {
    text-shadow: 0 0 5px #1de9b6, 0 0 10px #14a37f;
    animation: glowPulse 2.5s infinite;
  }

  @keyframes glowPulse {
    0%, 100% {
      text-shadow: 0 0 5px #1de9b6, 0 0 10px #14a37f;
    }
    50% {
      text-shadow: 0 0 10px #14a37f, 0 0 20px #1de9b6;
    }
  }
`;
document.head.appendChild(style);
