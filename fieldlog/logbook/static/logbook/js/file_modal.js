function openModal(url, type) {
  const modal = document.getElementById('fileModal');
  const modalContent = document.getElementById('modalContent');
  modalContent.innerHTML = ''; // Clear previous content

  if (type === 'image') {
    const img = document.createElement('img');
    img.src = url;
    img.alt = 'File preview';
    img.style.maxWidth = '100%';
    img.style.height = 'auto';
    modalContent.appendChild(img);

  } else if (type === 'doc') {
    const ext = url.split('.').pop().toLowerCase();
    if (['pdf', 'txt', 'xml', 'html'].includes(ext)) {
      const iframe = document.createElement('iframe');
      iframe.src = url;
      iframe.frameBorder = 0;
      iframe.style.width = '100%';
      iframe.style.height = '500px';
      modalContent.appendChild(iframe);
    } else {
      const p = document.createElement('p');
      p.textContent = `Preview not supported for this file type (${ext}). Please download it to view.`;
      
      const a = document.createElement('a');
      a.href = url;
      a.textContent = 'Download file';
      a.setAttribute('download', '');
      a.style.display = 'block';
      a.style.marginTop = '10px';

      modalContent.appendChild(p);
      modalContent.appendChild(a);
    }
  }

  modal.style.display = 'block';
}

function closeModal() {
  const modal = document.getElementById('fileModal');
  modal.style.display = 'none';
}

// Close modal if clicked outside the content
window.onclick = function(event) {
  const modal = document.getElementById('fileModal');
  if (event.target === modal) {
    closeModal();
  }
};
