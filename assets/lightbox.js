/* Gallery lightbox: click a gallery photo for the large version; arrows, swipe or keys to move; Esc or click outside to close. */
(function () {
  var imgs = Array.prototype.filter.call(document.querySelectorAll('.gallery figure img'), function (im) { return !im.closest('a'); });
  if (!imgs.length) return;
  var box = document.createElement('div');
  box.className = 'lbx'; box.hidden = true;
  box.setAttribute('role', 'dialog'); box.setAttribute('aria-modal', 'true'); box.setAttribute('aria-label', 'Photo');
  box.innerHTML = '<button class="lbx-x" aria-label="Close">&times;</button><button class="lbx-prev" aria-label="Previous photo">&lsaquo;</button>' +
    '<figure><img alt=""><figcaption></figcaption></figure><button class="lbx-next" aria-label="Next photo">&rsaquo;</button><div class="lbx-n"></div>';
  document.body.appendChild(box);
  var big = box.querySelector('img'), cap = box.querySelector('figcaption'), num = box.querySelector('.lbx-n'), cur = 0, last = null;
  function show(i) {
    cur = (i + imgs.length) % imgs.length;
    var im = imgs[cur], fc = im.parentNode.querySelector('figcaption');
    big.src = im.currentSrc || im.src; big.alt = im.alt;
    cap.innerHTML = fc ? fc.innerHTML : '';
    num.textContent = (cur + 1) + ' / ' + imgs.length;
  }
  function open(i) { last = document.activeElement; show(i); box.hidden = false; document.body.classList.add('lbx-open'); box.querySelector('.lbx-x').focus(); }
  function close() { box.hidden = true; document.body.classList.remove('lbx-open'); if (last) last.focus(); }
  imgs.forEach(function (im, i) {
    im.tabIndex = 0; im.style.cursor = 'zoom-in'; im.setAttribute('role', 'button');
    im.addEventListener('click', function () { open(i); });
    im.addEventListener('keydown', function (e) { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); open(i); } });
  });
  box.querySelector('.lbx-x').onclick = close;
  box.querySelector('.lbx-prev').onclick = function (e) { e.stopPropagation(); show(cur - 1); };
  box.querySelector('.lbx-next').onclick = function (e) { e.stopPropagation(); show(cur + 1); };
  box.addEventListener('click', function (e) { if (e.target === box) close(); });
  document.addEventListener('keydown', function (e) {
    if (box.hidden) return;
    if (e.key === 'Escape') close();
    else if (e.key === 'ArrowLeft') show(cur - 1);
    else if (e.key === 'ArrowRight') show(cur + 1);
  });
  var x0 = null;
  box.addEventListener('touchstart', function (e) { x0 = e.touches[0].clientX; }, { passive: true });
  box.addEventListener('touchend', function (e) {
    if (x0 === null) return; var dx = e.changedTouches[0].clientX - x0; x0 = null;
    if (Math.abs(dx) > 40) show(cur + (dx < 0 ? 1 : -1));
  });
})();
