// ============================================================
// CAAI Upload pages — dropzone behavior + client-side preview.
// Actual upload happens via normal form POST (multipart/form-data).
// ============================================================

document.addEventListener("DOMContentLoaded", () => {
  const dropzone = document.getElementById("dropzone");
  const fileInput = document.getElementById("fileInput");
  const previewList = document.getElementById("filePreviewList");

  if (!dropzone || !fileInput) return;

  // Keep our own list of File objects so "remove" can work before submit.
  let currentFiles = [];

  function renderPreview() {
    previewList.innerHTML = "";
    currentFiles.forEach((file, index) => {
      const li = document.createElement("li");
      li.className = "file-preview-item";

      const sizeKb = (file.size / 1024).toFixed(0);
      li.innerHTML = `
        <span>📎</span>
        <span>${file.name}</span>
        <span style="color:var(--grey-400); font-size:0.75rem;">${sizeKb} KB</span>
        <button type="button" class="remove-file" data-index="${index}">✕</button>
      `;
      previewList.appendChild(li);
    });

    // Sync the hidden input's file list to match currentFiles
    const dataTransfer = new DataTransfer();
    currentFiles.forEach((file) => dataTransfer.items.add(file));
    fileInput.files = dataTransfer.files;
  }

  function addFiles(fileListLike) {
    const incoming = Array.from(fileListLike);
    currentFiles = currentFiles.concat(incoming).slice(0, 5); // cap at 5, matches server limit
    renderPreview();
  }

  fileInput.addEventListener("change", (e) => addFiles(e.target.files));

  previewList.addEventListener("click", (e) => {
    if (e.target.classList.contains("remove-file")) {
      const idx = parseInt(e.target.getAttribute("data-index"), 10);
      currentFiles.splice(idx, 1);
      renderPreview();
    }
  });

  ["dragenter", "dragover"].forEach((evt) => {
    dropzone.addEventListener(evt, (e) => {
      e.preventDefault();
      dropzone.classList.add("dragover");
    });
  });

  ["dragleave", "drop"].forEach((evt) => {
    dropzone.addEventListener(evt, (e) => {
      e.preventDefault();
      dropzone.classList.remove("dragover");
    });
  });

  dropzone.addEventListener("drop", (e) => {
    if (e.dataTransfer && e.dataTransfer.files.length) {
      addFiles(e.dataTransfer.files);
    }
  });
});