(function (root, factory) {
  var api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.WeightStats = api;
}(typeof self !== 'undefined' ? self : this, function () {
  var DAY = 86400000;

  function withAverage(rows, days) {
    var windowDays = days || 7;
    rows.forEach(function (row) {
      var win = rows.filter(function (item) {
        return item.t <= row.t && item.t > row.t - windowDays * DAY;
      });
      row.avg = win.reduce(function (sum, item) { return sum + item.w; }, 0) / win.length;
      row.n = win.length;
    });
    return rows;
  }

  function goalReached(rows, threshold, minPoints) {
    if (!rows.length) return null;
    var last = rows[rows.length - 1];
    var required = minPoints == null ? 4 : minPoints;
    if (last.n < required) return null;
    return last.avg <= threshold;
  }

  function pointLabel(timestamp, weight) {
    var d = new Date(timestamp);
    var pad = function (value) { return ('0' + value).slice(-2); };
    var date = pad(d.getUTCDate()) + '.' + pad(d.getUTCMonth() + 1) + '.' + d.getUTCFullYear();
    return date + ' · ' + weight.toFixed(1).replace('.', ',') + ' кг';
  }

  return { withAverage: withAverage, goalReached: goalReached, pointLabel: pointLabel };
}));
