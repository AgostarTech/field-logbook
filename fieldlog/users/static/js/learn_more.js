document.addEventListener('DOMContentLoaded', () => {
  const heading = document.querySelector('.learn-heading');
  heading.addEventListener('mouseover', () => {
    heading.style.color = '#29b6f6';
  });
  heading.addEventListener('mouseout', () => {
    heading.style.color = '#80d8ff';
  });

  const listItems = document.querySelectorAll('.passion-section li');
  listItems.forEach(item => {
    item.addEventListener('mouseover', () => {
      item.style.transform = 'scale(1.05)';
      item.style.transition = '0.3s ease';
    });
    item.addEventListener('mouseout', () => {
      item.style.transform = 'scale(1)';
    });
  });
});
