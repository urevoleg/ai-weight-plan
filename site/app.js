(function () {
  var START = 0, TARGET_LO = 67, TARGET_HI = 68, ZONE_HI = 70;
  var WIN = 14, MIN_N = 7;
  var DAY = 86400000;
  // t-критерий для 95% двусторонного интервала, df = 1..30; дальше ~1.96
  var T975 = [null, 12.706, 4.303, 3.182, 2.776, 2.571, 2.447, 2.365, 2.306, 2.262, 2.228,
    2.201, 2.179, 2.160, 2.145, 2.131, 2.120, 2.110, 2.101, 2.093, 2.086, 2.080, 2.074,
    2.069, 2.064, 2.060, 2.056, 2.052, 2.048, 2.045, 2.042];
  function tcrit(df) { return df <= 30 ? T975[df] : 1.96; }

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

  // 95% доверительный интервал среднего за последние WIN дней, оканчивающиеся на rows[i]
  function ciAt(rows, i) {
    var end = rows[i].t;
    var win = rows.filter(function (x) { return x.t <= end && x.t > end - WIN * DAY; });
    var n = win.length;
    if (n < MIN_N) return null;
    var mean = win.reduce(function (s, x) { return s + x.w; }, 0) / n;
    var sd = Math.sqrt(win.reduce(function (s, x) { return s + (x.w - mean) * (x.w - mean); }, 0) / (n - 1));
    var h = tcrit(n - 1) * sd / Math.sqrt(n);
    return { n: n, mean: mean, sd: sd, lo: mean - h, hi: mean + h };
  }

  function stats(rows) {
    var li = rows.length - 1, last = rows[li];
    var c = ciAt(rows, li);
    var cards = [
      [fmt(last.w), 'последний вес, кг (' + fmtDate(last.t) + ')'],
      [c ? fmt(c.mean) : '—', 'среднее за 14 дней, кг'],
      [c ? fmt(c.lo) + '–' + fmt(c.hi) : 'мало данных', '95% ДИ, кг (нужно ≥ ' + MIN_N + ' измерений)'],
      [c ? (c.hi <= TARGET_HI ? 'да' : 'нет') : '—', 'цель достигнута: верхняя граница ≤ 68 кг'],
      [c ? (c.mean - START > 0 ? '+' : '') + fmt(c.mean - START) : '—', 'среднее к старту (' + fmt(START) + '), кг']
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
    var ymax = Math.ceil(Math.max.apply(null, ws.concat([ZONE_HI])) + 0.5);
    function x(t) { return L + (t - t0) / (t1 - t0) * (W - L - R); }
    function y(v) { return T + (ymax - v) / (ymax - ymin) * (H - T - B); }
    var s = '<svg viewBox="0 0 ' + W + ' ' + H + '" role="img" aria-label="График веса">';

    // зоны: жёлтая 68–70, зелёная ниже 68 (цель 67–68 и глубже)
    s += '<rect x="' + L + '" y="' + y(ZONE_HI) + '" width="' + (W - L - R) + '" height="' + (y(TARGET_HI) - y(ZONE_HI)) + '" fill="var(--zone-yellow)"/>';
    s += '<rect x="' + L + '" y="' + y(TARGET_HI) + '" width="' + (W - L - R) + '" height="' + (y(ymin) - y(TARGET_HI)) + '" fill="var(--zone-green)"/>';

    for (var v = ymin; v <= ymax; v++) {
      s += '<line x1="' + L + '" x2="' + (W - R) + '" y1="' + y(v) + '" y2="' + y(v) + '" stroke="var(--line)"/>';
      s += '<text x="' + (L - 8) + '" y="' + (y(v) + 4) + '" text-anchor="end" font-size="11" fill="var(--muted)">' + v + '</text>';
    }
    var step = Math.ceil((t1 - t0) / DAY / 8) * DAY;
    for (var t = t0; t <= t1; t += step) {
      s += '<text x="' + x(t) + '" y="' + (H - 8) + '" text-anchor="middle" font-size="11" fill="var(--muted)">' + fmtDate(t) + '</text>';
    }

    // полоса 95% ДИ по скользящему окну
    var cis = [];
    rows.forEach(function (r, i) { var c = ciAt(rows, i); if (c) cis.push({ t: r.t, c: c }); });
    if (cis.length >= 2) {
      var up = cis.map(function (p, i) { return (i ? 'L' : 'M') + x(p.t).toFixed(1) + ' ' + y(p.c.hi).toFixed(1); });
      var down = cis.slice().reverse().map(function (p) { return 'L' + x(p.t).toFixed(1) + ' ' + y(p.c.lo).toFixed(1); });
      s += '<path d="' + up.concat(down).join(' ') + ' Z" fill="var(--ci)" stroke="none"/>';
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
