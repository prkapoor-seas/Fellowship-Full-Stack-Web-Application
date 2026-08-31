/*
 * Client-side pagination for the browse tables (labs / fellowships / faculty).
 *
 * Every `.table-wrap` on the page is paginated automatically. Page size is 10
 * by default; override per table with `data-page-size="N"` on the .table-wrap.
 * When a table is re-sorted (its <tbody> is rebuilt), pagination resets to
 * page 1 on its own.
 */
(function () {
  "use strict";

  var DEFAULT_PAGE_SIZE = 10;
  var WINDOW = 7; // how many numbered page buttons to show at once

  function paginate(wrap) {
    var table = wrap.querySelector("table.result-table");
    if (!table || !table.tBodies.length) return;
    var tbody = table.tBodies[0];

    var pageSize = parseInt(wrap.dataset.pageSize, 10) || DEFAULT_PAGE_SIZE;
    var current = 1;

    var nav = document.createElement("nav");
    nav.className = "pager";
    nav.setAttribute("aria-label", "Table pagination");
    wrap.insertAdjacentElement("afterend", nav);

    function rows() {
      return Array.prototype.slice.call(tbody.rows);
    }

    function button(label, page, opts) {
      opts = opts || {};
      var b = document.createElement("button");
      b.type = "button";
      b.className = "pager-btn" + (opts.active ? " is-active" : "");
      b.textContent = label;
      if (opts.disabled || opts.active) {
        b.disabled = !!opts.disabled;
      }
      if (!opts.disabled && !opts.active) {
        b.addEventListener("click", function () {
          current = page;
          render();
          wrap.scrollIntoView({ block: "nearest" });
        });
      }
      return b;
    }

    function gap() {
      var s = document.createElement("span");
      s.className = "pager-gap";
      s.textContent = "…";
      return s;
    }

    function renderControls(pages, total) {
      nav.innerHTML = "";
      if (total <= pageSize) {
        nav.style.display = "none";
        return;
      }
      nav.style.display = "flex";

      nav.appendChild(button("‹ Prev", current - 1, { disabled: current === 1 }));

      var start = Math.max(1, current - Math.floor(WINDOW / 2));
      var end = Math.min(pages, start + WINDOW - 1);
      start = Math.max(1, end - WINDOW + 1);

      if (start > 1) {
        nav.appendChild(button("1", 1));
        if (start > 2) nav.appendChild(gap());
      }
      for (var p = start; p <= end; p++) {
        nav.appendChild(button(String(p), p, { active: p === current }));
      }
      if (end < pages) {
        if (end < pages - 1) nav.appendChild(gap());
        nav.appendChild(button(String(pages), pages));
      }

      nav.appendChild(button("Next ›", current + 1, { disabled: current === pages }));

      var info = document.createElement("span");
      info.className = "pager-info";
      var from = (current - 1) * pageSize + 1;
      var to = Math.min(current * pageSize, total);
      info.textContent = from + "–" + to + " of " + total;
      nav.appendChild(info);
    }

    function render() {
      var all = rows();
      var pages = Math.max(1, Math.ceil(all.length / pageSize));
      if (current > pages) current = pages;

      var first = (current - 1) * pageSize;
      var last = current * pageSize;
      all.forEach(function (tr, i) {
        tr.style.display = i >= first && i < last ? "" : "none";
      });

      renderControls(pages, all.length);
    }

    // Re-sorting rebuilds <tbody>; reset to page 1 and re-render.
    new MutationObserver(function () {
      current = 1;
      render();
    }).observe(tbody, { childList: true });

    render();
  }

  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".table-wrap").forEach(paginate);
  });
})();
