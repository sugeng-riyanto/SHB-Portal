(() => {
  const root = document.documentElement;
  const button = document.querySelector('[data-theme-toggle]');
  if (!button) return;
  const apply = (theme) => {
    root.dataset.theme = theme;
    const dark = theme === 'dark';
    button.setAttribute('aria-pressed', String(dark));
    button.textContent = dark ? '☀ Mode terang' : '☾ Mode gelap';
  };
  let saved = null;
  try { saved = localStorage.getItem('shb-theme'); } catch (_) {}
  apply(saved === 'dark' ? 'dark' : 'light');
  button.addEventListener('click', () => {
    const theme = root.dataset.theme === 'dark' ? 'light' : 'dark';
    apply(theme);
    try { localStorage.setItem('shb-theme', theme); } catch (_) {}
  });
})();
document.querySelectorAll('[data-password-target]').forEach((button) => {
  button.addEventListener('click', () => {
    const field = document.getElementById(button.dataset.passwordTarget);
    if (!field) return;
    const show = field.type === 'password';
    field.type = show ? 'text' : 'password';
    button.setAttribute('aria-pressed', String(show));
    button.textContent = show ? '◉ Sembunyikan password' : '👁 Tampilkan password';
  });
});
