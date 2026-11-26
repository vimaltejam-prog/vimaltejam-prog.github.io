async function showScholarMetrics() {
  const metrics = document.querySelectorAll('[data-scholar-metric]');
  if (!metrics.length) return;

  const dataUrl = 'https://raw.githubusercontent.com/vimaltejam-prog/vimaltejam-prog.github.io/scholar-metrics/scholar-metrics.json';
  const refreshWindow = Math.floor(Date.now() / 60000);
  try {
    const response = await fetch(`${dataUrl}?minute=${refreshWindow}`, { cache: 'no-store' });
    if (!response.ok) return;

    const snapshot = await response.json();
    const date = new Date(snapshot.updated_at);
    const values = Array.from(metrics, element => snapshot.metrics?.[element.dataset.scholarMetric]);
    if (!Number.isFinite(date.getTime()) || values.some(value => !Number.isSafeInteger(value) || value < 0)) return;

    const number = new Intl.NumberFormat('en-US');
    metrics.forEach((element, index) => {
      element.textContent = number.format(values[index]);
    });
    document.querySelectorAll('[data-scholar-results]').forEach(element => {
      element.hidden = false;
    });
    const updated = document.querySelector('[data-scholar-updated]');
    if (updated) {
      updated.dateTime = snapshot.updated_at;
      updated.textContent = new Intl.DateTimeFormat('en-US', {
        dateStyle: 'medium',
        timeStyle: 'short',
        timeZone: 'America/New_York',
      }).format(date) + ' ET';
    }
  } catch {
    // The direct Google Scholar link remains available.
  }
}

showScholarMetrics();
