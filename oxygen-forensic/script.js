// script.js – логика прототипа Oxygen Forensic Detective
// Обработчик загрузки файлов, вывод метаданных, имитация AI‑анализа и генерация PDF‑отчёта

// Utility: вычисление SHA‑256 через SubtleCrypto
async function computeHash(file) {
  const arrayBuffer = await file.arrayBuffer();
  const hashBuffer = await crypto.subtle.digest('SHA-256', arrayBuffer);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
}

function formatSize(bytes) {
  const units = ['B', 'KB', 'MB', 'GB', 'TB'];
  let i = 0;
  while (bytes >= 1024 && i < units.length - 1) {
    bytes /= 1024;
    i++;
  }
  return `${bytes.toFixed(1)} ${units[i]}`;
}

// Добавление строки в таблицу метаданных
function addRow(file, hash) {
  const tbody = document.querySelector('#metadataTable tbody');
  const tr = document.createElement('tr');
  tr.innerHTML = `
    <td>${file.name}</td>
    <td>${formatSize(file.size)}</td>
    <td>${file.type || 'unknown'}</td>
    <td>${new Date(file.lastModified).toLocaleString()}</td>
    <td>${hash}</td>
  `;
  tbody.appendChild(tr);
}

// Обработчик выбора файлов
document.getElementById('fileInput').addEventListener('change', async (e) => {
  const files = Array.from(e.target.files);
  // Очищаем таблицу
  document.querySelector('#metadataTable tbody').innerHTML = '';
  for (const f of files) {
    const hash = await computeHash(f);
    addRow(f, hash);
  }
  // Включаем кнопки после загрузки
  document.getElementById('analyzeBtn').disabled = false;
  document.getElementById('reportBtn').disabled = false;
});

// ---------- Симуляция AI‑анализа ----------
function simulateAI(file) {
  return new Promise((resolve) => {
    setTimeout(() => {
      // Жёстко прописанный результат – найдено 3 лица
      resolve(`AI‑анализ завершён. Обнаружено 3 лица с уровнями уверенности: 92%, 87%, 78%.`);
    }, 1500); // имитация задержки
  });
}

document.getElementById('analyzeBtn').addEventListener('click', async () => {
  const fileInput = document.getElementById('fileInput');
  if (!fileInput.files.length) {
    alert('Сначала загрузите файл изображения.');
    return;
  }
  const imgFile = fileInput.files[0];
  document.getElementById('aiResult').textContent = 'Анализируется...';
  const result = await simulateAI(imgFile);
  document.getElementById('aiResult').textContent = result;
});

// ---------- Генерация отчёта (PDF) ----------
function generateReportData() {
  const rows = Array.from(document.querySelectorAll('#metadataTable tbody tr'));
  const metadata = rows.map(tr => {
    const cells = tr.querySelectorAll('td');
    return {
      name: cells[0].textContent,
      size: cells[1].textContent,
      type: cells[2].textContent,
      modified: cells[3].textContent,
      hash: cells[4].textContent,
    };
  });
  return {
    deviceInfo: 'Смартфон (модель условная)',
    topContacts: ['+7 999 123‑45‑67', '+7 999 765‑43‑21', '+7 999 111‑22‑33', '+7 999 222‑33‑44', '+7 999 333‑44‑55'],
    deletedMessages: [
      { from: 'Alice', text: 'Привет', time: '2023‑01‑10 12:34' },
      { from: 'Bob', text: 'Как дела?', time: '2023‑02‑15 09:12' },
      { from: 'Charlie', text: 'Встречаемся?', time: '2023‑03‑20 18:45' },
    ],
    metadata,
  };
}

async function createPDF(report) {
  // Используем библиотеку jsPDF (подключаем её через CDN в index.html) – если библиотека не найдена, просто создаём blob‑текст.
  if (window.jspdf) {
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();
    doc.setFontSize(14);
    doc.text('Отчёт по расследованию', 10, 20);
    doc.setFontSize(11);
    doc.text(`Устройство: ${report.deviceInfo}`, 10, 30);
    doc.text('Топ‑5 контактов:', 10, 40);
    report.topContacts.forEach((c, i) => doc.text(`${i + 1}. ${c}`, 15, 48 + i * 6);
    doc.text('Восстановленные сообщения:', 10, 80);
    report.deletedMessages.forEach((m, i) => {
      doc.text(`${i + 1}. ${m.time} – ${m.from}: ${m.text}`, 15, 88 + i * 6);
    });
    doc.text('Метаданные файлов:', 10, 120);
    report.metadata.forEach((m, i) => {
      const y = 128 + i * 6;
      doc.text(`${i + 1}. ${m.name} | ${m.size} | ${m.type} | ${m.modified} | ${m.hash}`, 15, y);
    });
    return doc.output('blob');
  } else {
    // fallback – простой текстовый файл
    const lines = [];
    lines.push('Отчёт по расследованию');
    lines.push(`Устройство: ${report.deviceInfo}`);
    lines.push('Топ‑5 контактов:');
    report.topContacts.forEach((c, i) => lines.push(`${i + 1}. ${c}`));
    lines.push('Восстановленные сообщения:');
    report.deletedMessages.forEach((m, i) => lines.push(`${i + 1}. ${m.time} – ${m.from}: ${m.text}`));
    lines.push('Метаданные файлов:');
    report.metadata.forEach((m, i) => lines.push(`${i + 1}. ${m.name} | ${m.size} | ${m.type} | ${m.modified} | ${m.hash}`));
    const blob = new Blob([lines.join('\n')], { type: 'text/plain' });
    return blob;
  }
}

document.getElementById('reportBtn').addEventListener('click', async () => {
  const data = generateReportData();
  const blob = await createPDF(data);
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'report.pdf';
  a.click();
  URL.revokeObjectURL(url);
});

        opt.value = d.id;
        opt.textContent = `${d.id} (${d.type})`;
        select.appendChild(opt);
      });
      select.disabled = false;
      document.getElementById('filePathInput').disabled = false;
      document.getElementById('pullBtn').disabled = false;
      // Hide manual connect button because device is auto‑detected
      const connectBtn = document.getElementById('connectBtn');
      if (connectBtn) connectBtn.style.display = 'none';
    }
  } catch (e) {
    console.error('Auto‑detect error:', e);
  }
}

// Periodically check for connected devices (every 3 seconds)
setInterval(autoDetectDevices, 3000);
// Initial check on page load
autoDetectDevices();

// ---------- jsPDF loader (unchanged) ----------
(function loadJsPdf() {
  if (!window.jspdf) {
    const script = document.createElement('script');
    script.src = 'https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js';
    document.head.appendChild(script);
  }
})();
