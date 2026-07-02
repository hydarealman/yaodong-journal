/**
 * wander — article search & tag filtering
 * Runs on the homepage after DOM is ready.
 */
(function () {
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  function init() {
    var searchInput = document.getElementById('post-search');
    var tagFilters = document.getElementById('tag-filters');
    var filterCount = document.getElementById('filter-count');
    var postList = document.querySelector('.post-list');
    var pinnedSection = document.getElementById('pinned-section');

    if (!postList || !searchInput) return;

    var activeTag = '';

    /* ── Clear keyword highlights ── */
    function clearHighlights() {
      var marks = postList.querySelectorAll('mark.wander-hl');
      for (var i = 0; i < marks.length; i++) {
        var m = marks[i];
        var parent = m.parentNode;
        parent.replaceChild(document.createTextNode(m.textContent), m);
        parent.normalize();
      }
    }

    /* ── Highlight matching keywords ── */
    function highlight(query) {
      clearHighlights();
      if (!query) return;

      var escaped = query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      var re = new RegExp('(' + escaped + ')', 'gi');

      function walk(node) {
        if (node.nodeType === 3 && node.parentNode) {
          var text = node.textContent;
          if (re.test(text)) {
            re.lastIndex = 0;
            var frag = document.createDocumentFragment();
            var last = 0, m;
            while ((m = re.exec(text)) !== null) {
              if (m.index > last) {
                frag.appendChild(document.createTextNode(text.slice(last, m.index)));
              }
              var mark = document.createElement('mark');
              mark.className = 'wander-hl';
              mark.textContent = m[0];
              frag.appendChild(mark);
              last = re.lastIndex;
              if (!m[0]) { re.lastIndex++; last = re.lastIndex; }
            }
            if (last < text.length) {
              frag.appendChild(document.createTextNode(text.slice(last)));
            }
            node.parentNode.replaceChild(frag, node);
          }
        } else if (node.nodeType === 1 && node.childNodes) {
          if (node.tagName === 'MARK' || node.tagName === 'CODE' || node.tagName === 'PRE') return;
          for (var i = 0; i < node.childNodes.length; i++) {
            walk(node.childNodes[i]);
          }
        }
      }

      walk(postList);
    }

    /* ── Main filter logic ── */
    function filter() {
      var query = searchInput.value.toLowerCase().trim();
      var items = postList.querySelectorAll('.post-entry');
      var visible = 0;

      for (var i = 0; i < items.length; i++) {
        var item = items[i];
        var tags = (item.dataset.tags || '').toLowerCase();
        var title = (item.dataset.title || '').toLowerCase();
        var summary = (item.dataset.summary || '').toLowerCase();

        var matchTag = !activeTag;
        if (activeTag) {
          var tagList = tags.split(',');
          for (var j = 0; j < tagList.length; j++) {
            if (tagList[j].trim() === activeTag) { matchTag = true; break; }
          }
        }

        var matchSearch = !query
          || title.indexOf(query) !== -1
          || summary.indexOf(query) !== -1
          || tags.indexOf(query) !== -1;

        var show = matchTag && matchSearch;
        item.style.display = show ? '' : 'none';
        if (show) visible++;
      }

      if (filterCount) filterCount.textContent = visible + ' 篇';
      if (pinnedSection) pinnedSection.style.display = (query || activeTag) ? 'none' : '';

      highlight(query);
    }

    /* ── Wire up events ── */
    searchInput.addEventListener('input', filter);

    if (tagFilters) {
      tagFilters.addEventListener('click', function (e) {
        var pill = e.target.closest('.wander-tags__pill');
        if (!pill) return;
        activeTag = (pill.dataset.tag || '').toLowerCase();
        var pills = tagFilters.querySelectorAll('.wander-tags__pill');
        for (var i = 0; i < pills.length; i++) {
          pills[i].classList.toggle('active', pills[i] === pill);
        }
        filter();
      });
    }
  }
})();
