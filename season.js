/* 賽季進度計算器（由 tools/build_season.py 產生） */
(function () {
  'use strict';
  function $(id) { return document.getElementById(id); }
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
    return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function n(id, def) { var v = parseInt($(id).value, 10); return isNaN(v) || v < 0 ? def : v; }

  function calc() {
    var goal = Math.max(1, n('snGoal', 1));
    var cur = n('snCur', 0);
    var per = Math.max(1, n('snPer', 1));
    var days = Math.max(1, n('snDays', 1));
    var maxPerDay = Math.max(1, n('snMax', 6));

    var need = Math.max(0, goal - cur);
    var games = Math.ceil(need / per);
    var perDay = Math.ceil(games / days);
    var pct = Math.min(100, Math.max(0, cur / goal * 100));

    $('snNeed').textContent = need;
    $('snGames').textContent = games;
    $('snPerDay').textContent = perDay;

    var el = $('snReply');
    if (need <= 0) {
      el.className = 'bd-reply ok';
      el.innerHTML = '<span class="ico">🏆</span><span class="body">' +
        '<div class="main">已達標！　<span class="num">100%</span></div>' +
        '<div class="sub">目前 ' + cur + ' ／ 目標 ' + goal + '。保持下去就好。</div>' +
        '<div class="bd-bar"><span style="width:100%"></span></div></span>';
      return;
    }
    if (perDay <= maxPerDay) {
      el.className = 'bd-reply ok';
      el.innerHTML = '<span class="ico">✓</span><span class="body">' +
        '<div class="main">可以達標！　<span class="num">每天 ' + perDay + ' 場</span></div>' +
        '<div class="sub">還差 ' + need + '，需要 ' + games + ' 場；剩下 ' + days + ' 天，每天 ' + perDay +
        ' 場（上限 ' + maxPerDay + ' 場）剛好來得及。</div>' +
        '<div class="bd-bar"><span style="width:' + pct.toFixed(1) + '%"></span></div></span>';
    } else {
      el.className = 'bd-reply warn';
      el.innerHTML = '<span class="ico">✗</span><span class="body">' +
        '<div class="main">時間不夠　<span class="num">每天要 ' + perDay + ' 場</span></div>' +
        '<div class="sub">還差 ' + need + '（' + games + ' 場），但每天只能打 ' + maxPerDay +
        ' 場 → ' + days + ' 天最多 ' + (days * maxPerDay) + ' 場，還差 ' + Math.max(0, games - days * maxPerDay) +
        ' 場。建議提高每場進度或增加天數。</div>' +
        '<div class="bd-bar"><span style="width:' + pct.toFixed(1) + '%"></span></div></span>';
    }
  }

  document.addEventListener('DOMContentLoaded', function () {
    if (!$('snGoal')) return;
    ['snGoal', 'snCur', 'snPer', 'snDays', 'snMax'].forEach(function (id) {
      var el = $(id);
      if (el) { el.addEventListener('input', calc); el.addEventListener('change', calc); }
    });
    calc();
  });
})();
