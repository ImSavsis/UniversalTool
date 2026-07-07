requestAnimationFrame(() => document.body.classList.add("loaded"));

// --- tabs ---
function crossfade(fromPanel, toPanel) {
  if (fromPanel === toPanel) return;
  if (fromPanel) {
    fromPanel.classList.add("fade-out");
    setTimeout(() => {
      fromPanel.classList.remove("active", "fade-out");
    }, 170);
  }
  setTimeout(() => {
    toPanel.classList.add("active", "fade-in");
    setTimeout(() => toPanel.classList.remove("fade-in"), 380);
  }, fromPanel ? 140 : 0);
}

document.querySelectorAll(".tab-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    if (btn.classList.contains("active")) return;
    document.querySelectorAll(".tab-btn").forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");
    const current = document.querySelector(".tab-panel.active");
    const next = document.getElementById(`tab-${btn.dataset.tab}`);
    crossfade(current, next);
  });
});

function switchMode(switchEl, panelPrefix, attr) {
  switchEl.querySelectorAll(".mode-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      if (btn.classList.contains("active")) return;
      switchEl.querySelectorAll(".mode-btn").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      const val = btn.dataset[attr];
      const current = switchEl.parentElement.querySelector(".mode-panel.active");
      const next = document.getElementById(`${panelPrefix}-${val}`);
      crossfade(current, next);
      return val;
    });
  });
}

document.querySelectorAll(".mode-switch").forEach((sw) => {
  if (sw.querySelector("[data-mode]")) switchMode(sw, "mode", "mode");
  if (sw.querySelector("[data-meta-mode]")) switchMode(sw, "meta", "metaMode");
});

// =================== DOWNLOADER ===================

const dlUrl = document.getElementById("dl-url");
const dlFormat = document.getElementById("dl-format");
const dlQuality = document.getElementById("dl-quality");
const dlGo = document.getElementById("dl-go");
const dlProgress = document.getElementById("dl-progress");
const dlProgressBar = document.getElementById("dl-progress-bar");
const dlProgressText = document.getElementById("dl-progress-text");

const AUDIO_QUALITIES = [
  ["320", "320 kbps"],
  ["256", "256 kbps"],
  ["192", "192 kbps"],
  ["128", "128 kbps"],
];
const VIDEO_QUALITIES = [
  ["best", "лучшее"],
  ["2160", "2160p (4K)"],
  ["1440", "1440p"],
  ["1080", "1080p"],
  ["720", "720p"],
  ["480", "480p"],
  ["360", "360p"],
];

function refreshQualityOptions() {
  const isVideo = dlFormat.value === "mp4";
  const list = isVideo ? VIDEO_QUALITIES : AUDIO_QUALITIES;
  dlQuality.innerHTML = list.map(([v, label]) => `<option value="${v}">${label}</option>`).join("");
}
dlFormat.addEventListener("change", refreshQualityOptions);
refreshQualityOptions();

function startDownload(url, fmt, quality) {
  dlProgress.classList.remove("hidden");
  dlProgressBar.style.width = "0%";
  dlProgressText.textContent = "запускаю...";

  fetch("/api/download", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url, format: fmt, quality }),
  })
    .then((r) => r.json())
    .then((data) => {
      if (data.error) {
        dlProgressText.textContent = "ошибка: " + data.error;
        return;
      }
      pollJob(data.job_id);
    })
    .catch((e) => (dlProgressText.textContent = "ошибка: " + e));
}

function pollJob(jobId) {
  const iv = setInterval(() => {
    fetch(`/api/job/${jobId}`)
      .then((r) => r.json())
      .then((job) => {
        if (job.error) {
          clearInterval(iv);
          dlProgressText.textContent = "ошибка: " + job.error;
          return;
        }
        dlProgressBar.style.width = (job.progress || 0) + "%";

        if (job.status === "downloading") {
          dlProgressText.textContent = `скачиваю... ${job.progress || 0}% ${job.speed || ""}`;
        } else if (job.status === "processing") {
          dlProgressText.textContent = "обрабатываю...";
        } else if (job.status === "done") {
          clearInterval(iv);
          dlProgressText.textContent = "готово ✓";
          loadHistory();
        } else if (job.status === "error") {
          clearInterval(iv);
          dlProgressText.textContent = "ошибка: " + job.error;
        }
      })
      .catch(() => clearInterval(iv));
  }, 800);
}

dlGo.addEventListener("click", () => {
  const url = dlUrl.value.trim();
  if (!url) return;
  startDownload(url, dlFormat.value, dlQuality.value);
});

// --- search ---

const searchQ = document.getElementById("search-q");
const searchPlatform = document.getElementById("search-platform");
const searchGo = document.getElementById("search-go");
const searchResults = document.getElementById("search-results");

function renderResultCard(item, delayIndex = 0) {
  const div = document.createElement("div");
  div.className = "result-card";
  div.style.animationDelay = `${Math.min(delayIndex * 35, 300)}ms`;
  div.innerHTML = `
    <img src="${item.cover_url || ""}" onerror="this.style.opacity=0">
    <div class="meta">
      <div class="title">${escapeHtml(item.title)}</div>
      <div class="artist">${escapeHtml(item.artist)} ${item.duration ? "· " + item.duration : ""}</div>
    </div>
    <button class="dl-btn">скачать</button>
  `;
  div.querySelector(".dl-btn").addEventListener("click", () => {
    startDownload(item.url, dlFormat.value, dlQuality.value);
  });
  return div;
}

function escapeHtml(s) {
  const d = document.createElement("div");
  d.textContent = s || "";
  return d.innerHTML;
}

searchGo.addEventListener("click", () => {
  const q = searchQ.value.trim();
  if (!q) return;
  searchResults.innerHTML = '<div class="progress-text">ищу...</div>';
  fetch(`/api/search?platform=${searchPlatform.value}&q=${encodeURIComponent(q)}`)
    .then((r) => r.json())
    .then((data) => {
      searchResults.innerHTML = "";
      if (data.error || !data.results || !data.results.length) {
        searchResults.innerHTML = '<div class="progress-text">ничего не найдено</div>';
        return;
      }
      data.results.forEach((item, i) => searchResults.appendChild(renderResultCard(item, i)));
    });
});

// --- history ---

const historyList = document.getElementById("history-list");

function loadHistory() {
  fetch("/api/history")
    .then((r) => r.json())
    .then((data) => {
      historyList.innerHTML = "";
      (data.history || []).forEach((item, i) => {
        const div = document.createElement("div");
        div.className = "result-card";
        div.style.animationDelay = `${Math.min(i * 35, 300)}ms`;
        div.innerHTML = `
          <img src="${item.cover_url || ""}" onerror="this.style.opacity=0">
          <div class="meta">
            <div class="title">${escapeHtml(item.title)}</div>
            <div class="artist">${escapeHtml(item.artist)} · ${item.format.toUpperCase()}</div>
          </div>
        `;
        historyList.appendChild(div);
      });
    });
}

document.getElementById("history-clear").addEventListener("click", () => {
  fetch("/api/history/clear", { method: "POST" }).then(loadHistory);
});

loadHistory();

// =================== CONVERTER ===================

const dropZone = document.getElementById("drop-zone");
const convFile = document.getElementById("conv-file");
const convResult = document.getElementById("conv-result");
const convFileInfo = document.getElementById("conv-file-info");
const convTarget = document.getElementById("conv-target");
const convGo = document.getElementById("conv-go");
const convOutput = document.getElementById("conv-output");

let currentUpload = null;

["dragover", "dragenter"].forEach((ev) =>
  dropZone.addEventListener(ev, (e) => {
    e.preventDefault();
    dropZone.classList.add("dragover");
  })
);
["dragleave", "drop"].forEach((ev) =>
  dropZone.addEventListener(ev, (e) => {
    e.preventDefault();
    dropZone.classList.remove("dragover");
  })
);
dropZone.addEventListener("drop", (e) => {
  const file = e.dataTransfer.files[0];
  if (file) uploadForConvert(file);
});
convFile.addEventListener("change", () => {
  if (convFile.files[0]) uploadForConvert(convFile.files[0]);
});

function uploadForConvert(file) {
  const fd = new FormData();
  fd.append("file", file);
  convOutput.innerHTML = "";
  fetch("/api/convert/upload", { method: "POST", body: fd })
    .then((r) => r.json())
    .then((data) => {
      if (data.error) {
        convFileInfo.textContent = "ошибка: " + data.error;
        convResult.classList.remove("hidden");
        return;
      }
      currentUpload = data;
      convFileInfo.textContent = `${data.filename} · ${(data.size / 1024).toFixed(1)} KB · тип: ${data.type}`;
      convTarget.innerHTML = data.targets.map((t) => `<option value="${t}">${t.toUpperCase()}</option>`).join("");
      convResult.classList.remove("hidden");
    });
}

convGo.addEventListener("click", () => {
  if (!currentUpload) return;
  convOutput.textContent = "конвертирую...";
  fetch("/api/convert/run", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      id: currentUpload.id,
      saved: currentUpload.saved,
      filename: currentUpload.filename,
      target: convTarget.value,
    }),
  })
    .then((r) => r.json())
    .then((data) => {
      if (data.error) {
        convOutput.textContent = "ошибка: " + data.error;
        return;
      }
      convOutput.innerHTML = `<a href="/api/convert/download/${data.result}" download="${data.filename}">скачать ${data.filename}</a>`;
    });
});

// =================== METADATA ===================

const metaFile = document.getElementById("meta-file");
const metaForm = document.getElementById("meta-form");
const metaCoverPreview = document.getElementById("meta-cover-preview");
const metaCoverInput = document.getElementById("meta-cover-input");
const metaTitle = document.getElementById("meta-title");
const metaArtist = document.getElementById("meta-artist");
const metaAlbum = document.getElementById("meta-album");
const metaYear = document.getElementById("meta-year");
const metaTrack = document.getElementById("meta-track");
const metaSave = document.getElementById("meta-save");
const metaSaveResult = document.getElementById("meta-save-result");

let currentMetaFile = null;
let newCoverFile = null;

metaFile.addEventListener("change", () => {
  const file = metaFile.files[0];
  if (!file) return;
  const fd = new FormData();
  fd.append("file", file);
  fetch("/api/metadata/upload", { method: "POST", body: fd })
    .then((r) => r.json())
    .then((data) => {
      if (data.error) {
        alert(data.error);
        return;
      }
      currentMetaFile = data;
      newCoverFile = null;
      metaTitle.value = data.tags.title || "";
      metaArtist.value = data.tags.artist || "";
      metaAlbum.value = data.tags.album || "";
      metaYear.value = data.tags.year || "";
      metaTrack.value = data.tags.track_number || "";
      metaCoverPreview.src = data.tags.has_cover ? `/api/metadata/cover/${data.saved}?t=${Date.now()}` : "";
      metaForm.classList.remove("hidden");
      metaSaveResult.textContent = "";
    });
});

metaCoverInput.addEventListener("change", () => {
  const file = metaCoverInput.files[0];
  if (!file) return;
  newCoverFile = file;
  metaCoverPreview.src = URL.createObjectURL(file);
});

metaSave.addEventListener("click", () => {
  if (!currentMetaFile) return;
  const fd = new FormData();
  fd.append("saved", currentMetaFile.saved);
  fd.append("title", metaTitle.value);
  fd.append("artist", metaArtist.value);
  fd.append("album", metaAlbum.value);
  fd.append("year", metaYear.value);
  fd.append("track_number", metaTrack.value);
  if (newCoverFile) fd.append("cover", newCoverFile);

  fetch("/api/metadata/save", { method: "POST", body: fd })
    .then((r) => r.json())
    .then((data) => {
      if (data.error) {
        metaSaveResult.textContent = "ошибка: " + data.error;
        return;
      }
      metaSaveResult.innerHTML = `сохранено — <a href="/api/metadata/download/${data.download}" download>скачать</a>`;
    });
});

// --- batch ---

const metaBatchFiles = document.getElementById("meta-batch-files");
const metaBatchList = document.getElementById("meta-batch-list");
const metaBatchForm = document.getElementById("meta-batch-form");
const metaBatchCoverPreview = document.getElementById("meta-batch-cover-preview");
const metaBatchCoverInput = document.getElementById("meta-batch-cover-input");
const metaBatchArtist = document.getElementById("meta-batch-artist");
const metaBatchAlbum = document.getElementById("meta-batch-album");
const metaBatchYear = document.getElementById("meta-batch-year");
const metaBatchSave = document.getElementById("meta-batch-save");
const metaBatchResult = document.getElementById("meta-batch-result");

let batchUploads = [];
let batchCoverSaved = null;

metaBatchFiles.addEventListener("change", async () => {
  batchUploads = [];
  metaBatchList.innerHTML = "";
  for (const file of metaBatchFiles.files) {
    const fd = new FormData();
    fd.append("file", file);
    const res = await fetch("/api/metadata/upload", { method: "POST", body: fd }).then((r) => r.json());
    if (!res.error) {
      batchUploads.push(res);
      const div = document.createElement("div");
      div.className = "batch-item";
      div.innerHTML = `<span>${escapeHtml(file.name)}</span><span class="ok">загружен</span>`;
      metaBatchList.appendChild(div);
    }
  }
  if (batchUploads.length) metaBatchForm.classList.remove("hidden");
});

metaBatchCoverInput.addEventListener("change", async () => {
  const file = metaBatchCoverInput.files[0];
  if (!file) return;
  metaBatchCoverPreview.src = URL.createObjectURL(file);
  const fd = new FormData();
  fd.append("file", file, "cover.jpg");
  // reuse the audio upload-like storage isn't right for images; store cover directly via convert upload endpoint instead
  const res = await fetch("/api/convert/upload", { method: "POST", body: fd }).then((r) => r.json());
  if (!res.error) batchCoverSaved = res.saved;
});

metaBatchSave.addEventListener("click", () => {
  fetch("/api/metadata/batch", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      saved_files: batchUploads.map((u) => u.saved),
      artist: metaBatchArtist.value,
      album: metaBatchAlbum.value,
      year: metaBatchYear.value,
      cover_saved: batchCoverSaved,
    }),
  })
    .then((r) => r.json())
    .then((data) => {
      metaBatchResult.innerHTML = `обновлено: ${data.updated.length}` + (data.errors.length ? `, ошибок: ${data.errors.length}` : "");
    });
});

// =================== SCRIPTS ===================

const scriptInput = document.getElementById("script-input");
const scriptOutput = document.getElementById("script-output");
const scriptFormat = document.getElementById("script-format");
const scriptDownload = document.getElementById("script-download");
const scriptError = document.getElementById("script-error");
let currentLang = "python";

document.querySelectorAll("[data-lang]").forEach((btn) => {
  btn.addEventListener("click", () => {
    currentLang = btn.dataset.lang;
  });
});

scriptFormat.addEventListener("click", () => {
  scriptError.classList.add("hidden");
  fetch("/api/scripts/format", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ code: scriptInput.value, language: currentLang }),
  })
    .then((r) => r.json())
    .then((data) => {
      scriptOutput.value = data.formatted || "";
      if (!data.ok) {
        scriptError.textContent = (data.line ? `строка ${data.line}: ` : "") + data.error;
        scriptError.classList.remove("hidden");
        scriptDownload.disabled = true;
      } else {
        scriptDownload.disabled = false;
      }
    });
});

scriptDownload.addEventListener("click", () => {
  const ext = currentLang === "python" ? "py" : "lua";
  const blob = new Blob([scriptOutput.value], { type: "text/plain" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = `formatted.${ext}`;
  a.click();
});
