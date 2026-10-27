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
const languageSelect = document.getElementById('language-select');
if (languageSelect) {
  const current = document.documentElement.lang.toLowerCase();
  languageSelect.value = current.startsWith('zh-hant') ? 'zh-hant' : current.startsWith('id') ? 'id' : 'en';
}
const allProofs = document.getElementById('select-all-proofs');
const proofBoxes = Array.from(document.querySelectorAll('[data-proof-amount]'));
const proofTotal = document.getElementById('proof-total');
function updateProofTotal() {
  if (!proofTotal) return;
  const total = proofBoxes.filter(box => box.checked).reduce((sum, box) => sum + Number(box.dataset.proofAmount), 0);
  proofTotal.textContent = 'Total dipilih: Rp ' + new Intl.NumberFormat('id-ID').format(total);
}
if (allProofs) allProofs.addEventListener('change', () => { proofBoxes.forEach(box => { box.checked = allProofs.checked; }); updateProofTotal(); });
proofBoxes.forEach(box => box.addEventListener('change', updateProofTotal));
