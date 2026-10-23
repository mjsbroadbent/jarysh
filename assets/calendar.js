/* Jarysh Girls Calendar 2027 (presented by Aigyr): click an [data-calendar] image to open the wall calendar. Hover the bottom corner and the page
   lifts; click it to turn the page (bottom right = next month, bottom left brings the last month back down). Arrow keys, swipe, Esc also work. */
(function () {
  var triggers = document.querySelectorAll('[data-calendar]');
  if (!triggers.length) return;
  var YEAR = 2027;
  var MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
  var DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
  var HOLIDAYS = { '1-1': "New Year's Day", '3-11': 'Irad Day', '3-21': 'Nooruz' };
  var base = triggers[0].getAttribute('data-calendar'); // path to img/calendar/

  function pad(n) { return (n < 10 ? '0' : '') + n; }
  function grid(m) {
    var first = new Date(YEAR, m, 1), days = new Date(YEAR, m + 1, 0).getDate();
    var lead = (first.getDay() + 6) % 7, h = '<div class="cal-dn">' + DAYS.map(function (d, i) { return '<span' + (i > 4 ? ' class="we"' : '') + '>' + d + '</span>'; }).join('') + '</div><div class="cal-days">';
    for (var i = 0; i < lead; i++) h += '<span class="x"></span>';
    for (var d = 1; d <= days; d++) {
      var wd = (lead + d - 1) % 7, hol = HOLIDAYS[(m + 1) + '-' + d];
      h += '<span class="' + (wd === 6 || hol ? 'red' : wd === 5 ? 'sat' : '') + '"' + (hol ? ' title="' + hol + '"' : '') + '><b>' + d + '</b>' + (hol ? '<i>' + hol + '</i>' : '') + '</span>';
    }
    var cells = lead + days;
    while (cells % 7) { h += '<span class="x"></span>'; cells++; }
    return h + '</div>';
  }
  function cover() {
    var t = '';
    for (var i = 1; i <= 12; i++) t += '<img src="' + base + pad(i) + 's.jpg" alt="">';
    return '<div class="cal-front cal-cover"><img class="cal-logo" src="' + base + '../jarysh-logo.svg" alt="Jarysh">' +
      '<div class="cal-ttl"><span>JARYSH GIRLS</span> CALENDAR <em>' + YEAR + '</em></div>' +
      '<div class="cal-mosaic">' + t + '</div>' +
      '<div class="cal-tag">Twelve months. Twelve fillies. One stallion.</div>' +
      '<div class="cal-foot"><span>Presented by</span><img src="' + base + '../aigyr-crest.svg" alt="Aigyr Lager"><span>Ride hard. Drink Aigyr.</span></div></div>';
  }
  function month(m) {
    return '<div class="cal-front cal-month"><img class="cal-photo" src="' + base + pad(m + 1) + '.jpg" alt="Miss ' + MONTHS[m] + ' ' + YEAR + ' with a horse" loading="lazy">' +
      '<div class="cal-grid"><div class="cal-mh"><span>' + MONTHS[m] + '</span><em>' + YEAR + '</em></div>' + grid(m) + '</div>' +
      '<div class="cal-foot"><span>JARYSH GIRLS ' + YEAR + '</span>' + (m === 11 ? '<span>Miss December: Zhibek, Nurzhan</span>' : '') + '<span>Ride hard. Drink Aigyr.</span></div></div>';
  }

  var box = document.createElement('div');
  box.className = 'cal'; box.hidden = true;
  box.setAttribute('role', 'dialog'); box.setAttribute('aria-modal', 'true'); box.setAttribute('aria-label', 'Jarysh Girls Calendar ' + YEAR);
  var html = '<button class="cal-x" aria-label="Close">&times;</button><div class="cal-wall"><div class="cal-hanger"></div><div class="cal-stack">';
  for (var p = 0; p <= 12; p++) {
    html += '<div class="cal-page" data-i="' + p + '">' + (p === 0 ? cover() : month(p - 1)) + '<div class="cal-back"></div>' +
      '<div class="cal-fold"></div>' + (p < 12 ? '<button class="cal-hot nx" aria-label="Next month"></button>' : '') +
      (p > 0 ? '<button class="cal-hot pv" aria-label="Previous month"></button>' : '') + '</div>';
  }
  html += '</div></div><div class="cal-hint">Lift the corner to turn the page</div>';
  box.innerHTML = html;
  document.body.appendChild(box);
  var pages = Array.prototype.slice.call(box.querySelectorAll('.cal-page')), cur = 0, busy = false, last = null;

  function layout() {
    pages.forEach(function (pg, i) {
      pg.style.zIndex = 50 - i;
      pg.classList.toggle('off', !(i === cur || i === cur + 1));
      pg.classList.remove('peel-r', 'peel-l');
    });
  }
  function next() {
    if (busy || cur >= 12) return;
    busy = true;
    var pg = pages[cur];
    pg.classList.remove('peel-r', 'peel-l');
    pg.classList.add('flip');
    if (pages[cur + 1]) pages[cur + 1].classList.add('shade');
    setTimeout(function () {
      pg.classList.remove('flip');
      if (pages[cur + 1]) pages[cur + 1].classList.remove('shade');
      cur++; layout(); busy = false;
    }, 760);
  }
  function prev() {
    if (busy || cur <= 0) return;
    busy = true;
    var pg = pages[cur - 1];
    pg.classList.remove('off');
    pg.classList.add('up', 'noanim');
    pages[cur].classList.add('shade');
    void pg.offsetWidth;
    pg.classList.remove('noanim');
    requestAnimationFrame(function () { pg.classList.remove('up'); });
    setTimeout(function () { pages[cur].classList.remove('shade'); cur--; layout(); busy = false; }, 760);
  }
  pages.forEach(function (pg) {
    var nx = pg.querySelector('.nx'), pv = pg.querySelector('.pv');
    if (nx) {
      nx.addEventListener('mouseenter', function () { if (!busy) pg.classList.add('peel-r'); });
      nx.addEventListener('mouseleave', function () { pg.classList.remove('peel-r'); });
      nx.addEventListener('click', function (e) { e.stopPropagation(); next(); });
    }
    if (pv) {
      pv.addEventListener('click', function (e) { e.stopPropagation(); prev(); });
    }
  });

  function open() { last = document.activeElement; cur = 0; layout(); box.hidden = false; document.body.classList.add('cal-open'); box.querySelector('.cal-x').focus(); }
  function close() { box.hidden = true; document.body.classList.remove('cal-open'); if (last) last.focus(); }
  Array.prototype.forEach.call(triggers, function (t) {
    t.tabIndex = 0; t.style.cursor = 'pointer'; t.setAttribute('role', 'button');
    t.addEventListener('click', open);
    t.addEventListener('keydown', function (e) { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); open(); } });
  });
  box.querySelector('.cal-x').onclick = close;
  box.addEventListener('click', function (e) { if (e.target === box) close(); });
  document.addEventListener('keydown', function (e) {
    if (box.hidden) return;
    if (e.key === 'Escape') close();
    else if (e.key === 'ArrowRight' || e.key === 'ArrowDown' || e.key === 'PageDown') { e.preventDefault(); next(); }
    else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp' || e.key === 'PageUp') { e.preventDefault(); prev(); }
  });
  var y0 = null, x0 = null;
  box.addEventListener('touchstart', function (e) { y0 = e.touches[0].clientY; x0 = e.touches[0].clientX; }, { passive: true });
  box.addEventListener('touchend', function (e) {
    if (y0 === null) return;
    var dy = e.changedTouches[0].clientY - y0, dx = e.changedTouches[0].clientX - x0;
    if (Math.abs(dy) > 50 && Math.abs(dy) > Math.abs(dx)) { if (dy < 0) next(); else prev(); }
    else if (Math.abs(dx) > 50) { if (dx < 0) next(); else prev(); }
    y0 = null;
  });
})();
