// Runs before first paint so the page never flashes the wrong theme. Follows the OS only until the person chooses.
// Uses the same storage key as the Cyber Toolkit, so one choice applies across u51.org.
(function () {
  var d = document.documentElement, t = null;
  d.classList.remove('no-js');
  try { t = localStorage.getItem('ctk-theme'); } catch (e) {}
  if (t !== 'dark' && t !== 'light') t = window.matchMedia && matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  d.setAttribute('data-theme', t);
})();
