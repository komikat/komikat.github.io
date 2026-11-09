(() => {
  const system = matchMedia('(prefers-color-scheme: dark)');
  let preference;
  let button;
  try { preference = localStorage.getItem('theme'); } catch {}
  if (!['light', 'dark'].includes(preference)) preference = null;

  function apply() {
    const theme = preference || (system.matches ? 'dark' : 'light');
    document.documentElement.dataset.theme = theme;
    if (button) button.textContent = theme === 'dark' ? 'Light mode' : 'Dark mode';
  }

  apply();
  system.addEventListener('change', apply);
  document.addEventListener('DOMContentLoaded', () => {
    button = document.getElementById('theme-toggle');
    if (!button) return;
    button.hidden = false;
    apply();
    button.addEventListener('click', () => {
      preference = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
      try { localStorage.setItem('theme', preference); } catch {}
      apply();
    });
  });
})();
