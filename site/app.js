(function () {
  var START = 0, TARGET_LO = 67, TARGET_HI = 68;
  var DAY = 86400000;

  function $(id) { return document.getElementById(id); }
  function fail(msg) { var e = $('err'); e.textContent = msg; e.hidden = false; }
  function get(path) {
    return fetch(path, { cache: 'no-cache' }).then(function (r) {
      if (!r.ok) throw new Error(path + ': ' + r.status);
      return r.text();
    });
  }
  function md(el, text) {
    el.innerHTML = window.marked ? window.marked.parse(text) : '<pre></pre>';
    if (!window.marked) el.firstChild.textContent = text;
  }
  function fmt(x, d) { return x.toFixed(d == null ? 1 : d).replace('.', ','); }
  function fmtDate(t) {
    var d = new Date(t);
    return ('0' + d.getUTCDate()).slice(-2) + '.' + ('0' + (d.getUTCMonth() + 1)).slice(-2);
  }

  function parseCsv(text) {
    var rows = [];
    text.split(/\r?\n/).slice(1).forEach(function (line) {
      if (!line.trim()) return;
      var p = line.split(',');
      var t = Date.parse(p[0] + 'T00:00:00Z');
      var w = parseFloat(p[1]);
      var note = p.slice(2).join(',');
      if (!isNaN(t) && !isNaN(w) && !/исключ/i.test(note)) rows.push({ t: t, w: w, note: note });
    });
    rows.sort(function (a, b) { return a.t - b.t; });
    return rows;
  }

  function withAverage(rows) {
    rows.forEach(function (r) {
      var win = rows.filter(function (x) { return x.t <= r.t && x.t > r.t - 7 * DAY; });
      r.avg = win.reduce(function (s, x) { return s + x.w; }, 0) / win.length;
      r.n = win.length;
    });
    return rows;
  }

  function stats(rows) {
    var last = rows[rows.length - 1];
    var cards = [
      [fmt(last.w), 'последний вес, кг (' + fmtDate(last.t) + ')'],
      [last.n >= 4 ? fmt(last.avg) : '—', 'среднее за 7 дней, кг'],
      [last.n >= 4 ? (last.avg - START > 0 ? '+' : '') + fmt(last.avg - START) : '—', 'к старту (' + fmt(START) + '), кг'],
      [last.n >= 4 ? fmt(Math.max(0, last.avg - TARGET_HI)) : '—', 'до цели 68 кг, кг']
    ];
    $('stats').innerHTML = cards.map(function (c) {
      return '<div class="stat"><b>' + c[0] + '</b><span>' + c[1] + '</span></div>';
    }).join('');
  }

  function chart(rows) {
    var W = 780, H = 300, L = 44, R = 16, T = 14, B = 30;
    var t0 = rows[0].t, t1 = Math.max(rows[rows.length - 1].t, t0 + 14 * DAY);
    var ws = rows.map(function (r) { return r.w; });
    var ymin = Math.floor(Math.min.apply(null, ws.concat([TARGET_LO])) - 0.5);
    var ymax = Math.ceil(Math.max.apply(null, ws.concat([TARGET_HI])) + 0.5);
    function x(t) { return L + (t - t0) / (t1 - t0) * (W - L - R); }
    function y(v) { return T + (ymax - v) / (ymax - ymin) * (H - T - B); }
    var s = '<svg viewBox="0 0 ' + W + ' ' + H + '" role="img" aria-label="График веса">';
    for (var v = ymin; v <= ymax; v++) {
      s += '<line x1="' + L + '" x2="' + (W - R) + '" y1="' + y(v) + '" y2="' + y(v) + '" stroke="var(--line)"/>';
      s += '<text x="' + (L - 8) + '" y="' + (y(v) + 4) + '" text-anchor="end" font-size="11" fill="var(--muted)">' + v + '</text>';
    }
    s += '<rect x="' + L + '" y="' + y(TARGET_HI) + '" width="' + (W - L - R) + '" height="' + (y(TARGET_LO) - y(TARGET_HI)) + '" fill="var(--band)"/>';
    var step = Math.ceil((t1 - t0) / DAY / 8) * DAY;
    for (var t = t0; t <= t1; t += step) {
      s += '<text x="' + x(t) + '" y="' + (H - 8) + '" text-anchor="middle" font-size="11" fill="var(--muted)">' + fmtDate(t) + '</text>';
    }
    var daily = rows.map(function (r, i) {
      return (i ? 'L' : 'M') + x(r.t).toFixed(1) + ' ' + y(r.w).toFixed(1);
    }).join(' ');
    s += '<path d="' + daily + '" fill="none" stroke="var(--dot)" stroke-width="2" stroke-linejoin="round"/>';
    var avg = rows.filter(function (r) { return r.n >= 3; }).map(function (r, i) {
      return (i ? 'L' : 'M') + x(r.t).toFixed(1) + ' ' + y(r.avg).toFixed(1);
    }).join(' ');
    if (avg) s += '<path d="' + avg + '" fill="none" stroke="var(--avg)" stroke-width="2.5" stroke-dasharray="6 4" stroke-linejoin="round"/>';
    rows.forEach(function (r) {
      s += '<circle cx="' + x(r.t).toFixed(1) + '" cy="' + y(r.w).toFixed(1) + '" r="4.5" fill="var(--dot)" stroke="var(--card)" stroke-width="1.5"><title>' + fmtDate(r.t) + ': ' + fmt(r.w) + ' кг</title></circle>';
    });
    s += '</svg>';
    $('chart').innerHTML = s;
  }

  function weeks(list) {
    $('weeks').innerHTML = list.slice().reverse().map(function (w) {
      return '<li><a href="#report=' + w.id + '" data-id="' + w.id + '" data-path="' + w.report + '">' +
        '<span><b>' + w.title + '</b> · ' + w.dates + '</span><span class="tag">' + w.status + '</span></a></li>';
    }).join('');
    function show() {
      var m = location.hash.match(/report=([\w-]+)/);
      var el = $('report');
      if (!m) { el.innerHTML = ''; return; }
      var w = list.filter(function (x) { return x.id === m[1]; })[0];
      if (!w) return;
      get(w.report).then(function (t) {
        el.className = 'card';
        md(el, t);
        el.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }).catch(function (e) { fail(e.message); });
    }
    window.addEventListener('hashchange', show);
    show();
  }

  Promise.all([get('data/weights.csv'), get('data/weeks.json'), get('plan.md')]).then(function (r) {
    var rows = withAverage(parseCsv(r[0]));
    if (rows.length) { START = rows[0].w; stats(rows); chart(rows); }
    weeks(JSON.parse(r[1]));
    md($('plan'), r[2]);
  }).catch(function (e) { fail('Не удалось загрузить данные: ' + e.message); });
})();
