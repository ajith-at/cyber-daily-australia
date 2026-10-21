// Dark mode switch. The sun and moon icons swap in CSS from [data-theme].
(function () {
  var d = document.documentElement;
  function sync() {
    var dark = d.getAttribute('data-theme') === 'dark';
    document.querySelectorAll('[data-theme-toggle]').forEach(function (b) { b.setAttribute('aria-checked', String(dark)); });
  }
  document.querySelectorAll('[data-theme-toggle]').forEach(function (b) {
    b.addEventListener('click', function () {
      var t = d.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      d.setAttribute('data-theme', t);
      try { localStorage.setItem('ctk-theme', t); } catch (e) {}
      sync();
    });
  });
  sync();
})();
