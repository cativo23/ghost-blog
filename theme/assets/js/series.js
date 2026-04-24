(function () {
  var badge = document.querySelector('.series-badge');
  var seriesIndex = document.querySelector('.series-index');
  if (!badge || !seriesIndex) return;

  var rawName = badge.dataset.seriesName || '';
  var displayName = rawName.replace(/^series:\s*/i, '').trim();

  var currentSlug = window.location.pathname.split('/').filter(Boolean).pop();
  var items = seriesIndex.querySelectorAll('.series-item');
  var total = items.length;
  var currentPosition = 0;

  items.forEach(function (item, i) {
    if (item.dataset.postSlug === currentSlug) {
      currentPosition = i + 1;
      item.classList.add('current');

      var link = item.querySelector('a.series-link');
      if (link) {
        var span = document.createElement('span');
        span.className = 'series-link';
        span.textContent = link.textContent;
        link.replaceWith(span);
      }

      var indicator = document.createElement('span');
      indicator.className = 'current-indicator';
      indicator.textContent = '← estás aquí';
      item.appendChild(indicator);
    }
  });

  badge.querySelector('.series-badge-name').textContent = displayName;
  badge.querySelector('.series-badge-position').textContent = currentPosition + '/' + total;

  seriesIndex.querySelector('.series-title').textContent =
    '📚 ' + displayName + ' (' + currentPosition + '/' + total + ')';

  var header = seriesIndex.querySelector('.series-header');
  var toggle = seriesIndex.querySelector('.series-toggle');
  header.addEventListener('click', function () {
    seriesIndex.classList.toggle('collapsed');
    toggle.textContent = seriesIndex.classList.contains('collapsed') ? '▶' : '▼';
  });
})();
