// Home page controls. Every figure shown comes from the engine export embedded in the
// page (#pi-data). This script looks values up, formats them and draws; it computes no
// published number. Counting animations only show intermediate frames on the way to
// the exported value.
(function () {
  "use strict";
  var dataEl = document.getElementById("pi-data");
  var scope = document.querySelector(".pi-scope");
  if (!dataEl || !scope) return;
  var D = JSON.parse(dataEl.textContent);
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)");
  var live = document.getElementById("pi-live");
  var dots = scope.querySelectorAll(".pi-d");
  var goldLines = scope.querySelectorAll(".pi-pg");
  var shown = { price: null, value: null, odds: null };
  var tweens = {};

  function usdM(n) { return "US$" + n.toLocaleString("en-US") + "M"; }
  function usd(n) { return "US$" + n.toLocaleString("en-US"); }

  function checked(name) {
    var el = scope.querySelector('input[name="' + name + '"]:checked');
    return el ? el.value : null;
  }

  function state() {
    var s = {
      price: checked("price"), gold: checked("gold"), ret: checked("ret"), ov: checked("ov")
    };
    var key = s.gold + "_" + s.ret + "_" + s.ov;
    s.value = D.value_m[key];
    s.odds = D.odds[s.price + "_" + key];
    return s;
  }

  function setAll(k, text) {
    var els = scope.querySelectorAll('[data-k="' + k + '"]');
    for (var i = 0; i < els.length; i++) els[i].textContent = text;
  }

  function paint(k, n) {
    if (k === "price") setAll("price", usdM(n));
    else if (k === "value") setAll("value", usdM(n));
    else if (k === "odds") { setAll("odds", n + "%"); setAll("oddsn", String(n)); }
  }

  // Count the displayed integer from its current value to the exported one.
  function count(k, from, to, ms, delay) {
    if (tweens[k]) cancelAnimationFrame(tweens[k]);
    if (reduce.matches || ms === 0 || from === null || from === to) { paint(k, to); return; }
    var start = null;
    function frame(t) {
      if (start === null) start = t + (delay || 0);
      var x = Math.min(Math.max((t - start) / ms, 0), 1);
      var e = 1 - Math.pow(1 - x, 3);
      paint(k, x >= 1 ? to : Math.round(from + (to - from) * e));
      if (x < 1) tweens[k] = requestAnimationFrame(frame);
    }
    tweens[k] = requestAnimationFrame(frame);
  }

  function render(ms, delay, fromZero) {
    var s = state();
    if (s.value === undefined || s.odds === undefined) return;
    var ns = s.odds === null;
    scope.classList.toggle("is-ns", ns);
    scope.classList.toggle("no-ov", s.ov === "0");
    setAll("ret", s.ret + "%");

    var price = Number(s.price);
    count("price", fromZero ? 0 : shown.price, price, ms, delay);
    count("value", fromZero ? 0 : shown.value, s.value, ms, delay);
    if (!ns) count("odds", fromZero ? 0 : (shown.odds === null ? 0 : shown.odds), s.odds, ms, delay);
    shown = { price: price, value: s.value, odds: ns ? null : s.odds };

    var lit = ns ? 0 : s.odds;
    for (var i = 0; i < dots.length; i++) {
      dots[i].classList.toggle("on", i < lit);
      if (!fromZero) dots[i].style.transitionDelay = "";
    }
    for (var j = 0; j < goldLines.length; j++) {
      var draw = Number(goldLines[j].getAttribute("data-draw"));
      goldLines[j].classList.toggle("on", !ns && draw * 100 < s.odds);
    }

    var g = D.gold_figures[s.gold];
    setAll("g50", usd(g.median));
    setAll("g90", usd(g.p5) + " to " + usd(g.p95));

    // Drawing only: bar lengths and the fan's vertical scale.
    scope.style.setProperty("--g", String(Number(s.gold) / D.base_gold));
    scope.style.setProperty("--vw", String(s.value / D.bar_scale));
    scope.style.setProperty("--pw", String(price / D.bar_scale));
    scope.style.setProperty("--ob", ns ? "1" : String(s.odds / 100));

    if (live) {
      live.textContent = ns
        ? "Price above built value at a " + s.ret + "% return. Price " + usdM(price) +
          ", worth if built " + usdM(s.value) + "."
        : "Price as a share of built value " + s.odds + "%. Price " + usdM(price) +
          ", worth if built " + usdM(s.value) + ", at a " + s.ret + "% extra return.";
    }
  }

  scope.addEventListener("change", function (ev) {
    if (ev.target && ev.target.type === "radio") render(400, 0, false);
  });

  // Opening count from zero to the starting values. The page already holds the values
  // as text, and nothing is zeroed until the browser draws a frame, so a page that is
  // never animated (a background tab, a preview) still shows the right numbers.
  if (!reduce.matches) {
    requestAnimationFrame(function () {
      for (var i = 0; i < dots.length; i++) {
        if (dots[i].classList.contains("on")) {
          dots[i].classList.remove("on");
          dots[i].style.transitionDelay = (300 + i * 14) + "ms";
        }
      }
      paint("price", 0); paint("value", 0); paint("odds", 0);
      requestAnimationFrame(function () {
        render(1600, 300, true);
        setTimeout(function () {
          for (var k = 0; k < dots.length; k++) dots[k].style.transitionDelay = "";
        }, 2400);
      });
    });
  } else {
    render(0, 0, false);
  }

  // Tooltips close on Escape and reopen on the next hover or focus.
  document.addEventListener("keydown", function (ev) {
    if (ev.key !== "Escape") return;
    var tips = document.querySelectorAll(".pi-tip");
    for (var i = 0; i < tips.length; i++) {
      if (tips[i].matches(":hover, :focus-within")) tips[i].classList.add("tt-off");
    }
  });
  var tipEls = document.querySelectorAll(".pi-tip");
  for (var t = 0; t < tipEls.length; t++) {
    tipEls[t].addEventListener("mouseleave", function () { this.classList.remove("tt-off"); });
    tipEls[t].addEventListener("focusout", function () { this.classList.remove("tt-off"); });
  }

  // Pause the gold path loop while the chart is off screen.
  var fan = document.getElementById("pi-fan");
  if (fan && "IntersectionObserver" in window) {
    new IntersectionObserver(function (entries) {
      fan.classList.toggle("paused", !entries[0].isIntersecting);
    }).observe(fan);
  }
})();
