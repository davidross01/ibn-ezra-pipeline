// Page planner: paginates verse band + Hebrew commentary + English commentary + two-column notes.
(async function () {
  await Promise.all([...document.fonts].map(f => f.load().catch(() => null)));
  await document.fonts.ready;
  const LOG = [];
  const log = (...a) => LOG.push(a.join(' '));
  const LH = { hc: 16.4, ec: 16.4, n: 13.6 };
  const GAPS = { hc: { p: 0 }, ec: { p: 3, first: 5, chap: 8, src: 4 }, n: { p: 2, first: 3, chap: 6 } };
  const TOP = 63, BOTTOM = 954, AVAIL = BOTTOM - TOP;
  const SP = { afterBand: 15, divHe: 14, afterDivHe: 9, afterHc: 14, divEn: 13, afterDivEn: 10, afterEc: 12, rule: 1, afterRule: 8 };
  const NV = VERSES.length;
  // parasha heading on the first page of a parasha that does not open its own volume (parasha.json heading_en/heading_he)
  const HEAD = (PARASHA.heading_en && !PARASHA.title_page) ? 74 : 0;   // E1: a parasha with a title page of its own has no heading here

  // ---------------- streams
  function makeStream(s) {
    const lh = LH[s];
    const bl = BLOCKS.filter(b => b.s === s).map(b => {
      const el = document.getElementById(b.id);
      const h = el.getBoundingClientRect().height;
      const n = Math.round(h / lh);
      const isFirst = el.classList.contains('first');
      const splittable = b.kind === 'p' && Math.abs(h - n * lh) < 0.75;
      if (b.kind === 'p' && !splittable) log('WARN non-grid block', b.id, s, h.toFixed(2), (h / lh).toFixed(2));
      return { id: b.id, el, vi: b.vi, kind: b.kind, h, n, splittable, isFirst, off: 0 };
    });
    let y = 0;
    bl.forEach((b, i) => {
      const g = GAPS[s];
      b.gap = i === 0 ? 0 : (b.kind === 'chap' ? g.chap : b.kind === 'src' ? g.src : (b.isFirst ? (g.first ?? g.p) : g.p));
      y += b.gap; b.top = y; y += b.h;
    });
    const total = y;
    const cuts = [];
    bl.forEach((b, i) => {
      const allowStart = i === 0 || !(bl[i - 1].kind === 'chap' || b.kind === 'src');
      if (allowStart) cuts.push({ bi: i, li: 0, ye: b.top - b.gap, yb: b.top });
      if (b.splittable && b.n >= 4) for (let li = 2; li <= b.n - 2; li++) cuts.push({ bi: i, li, ye: b.top + li * lh, yb: b.top + li * lh });
    });
    cuts.push({ bi: bl.length, li: 0, ye: total, yb: total });
    // verse segments
    const segS = new Array(NV + 1).fill(null), segE = new Array(NV + 1).fill(null);
    bl.forEach(b => {
      if (segS[b.vi] === null) segS[b.vi] = b.top - b.gap;
      segE[b.vi] = b.top + b.h;
    });
    let next = total;
    for (let v = NV - 1; v >= 0; v--) {
      if (segS[v] === null) { segS[v] = next; segE[v] = next; }
      next = segS[v];
    }
    segS[NV] = total; segE[NV] = total;
    return { s, lh, bl, cuts, total, segS, segE, cur: 0 };
  }
  const ST = { hc: makeStream('hc'), ec: makeStream('ec'), n: makeStream('n') };

  function H(S, a, b) { return b > a ? S.cuts[b].ye - S.cuts[a].yb : 0; }
  function target(S, t) {
    if (t >= NV) return S.total;
    const v = Math.floor(t), f = t - v;
    return S.segS[v] + f * (S.segE[v] - S.segS[v]);
  }
  function snap(S, Y) {
    let lo = S.cur, hi = S.cuts.length - 1;
    if (S.cuts[lo].ye > Y + 0.01) return S.cur;
    while (lo < hi) { const mid = (lo + hi + 1) >> 1; if (S.cuts[mid].ye <= Y + 0.01) lo = mid; else hi = mid - 1; }
    return Math.max(lo, S.cur);
  }
  function balance(S, a, b) {
    if (b <= a) return { h: 0, m: a };
    if (b === a + 1) return { h: H(S, a, b), m: b };
    let lo = a + 1, hi = b;
    while (lo < hi) { const mid = (lo + hi) >> 1; if (H(S, a, mid) >= H(S, mid, b)) hi = mid; else lo = mid + 1; }
    let best = null;
    for (const m of [lo - 1, lo]) {
      if (m <= a || m > b) continue;
      const h1 = H(S, a, m), h2 = H(S, m, b), h = Math.max(h1, h2);
      if (!best || h < best.h - 0.01 || (Math.abs(h - best.h) < 0.01 && h1 >= h2)) best = { h, m, h1, h2 };
    }
    return best;
  }

  // ---------------- verse band
  const bandBox = document.getElementById('m-band');
  const bandCache = {};
  function bandHTML(a, b) {
    let en = '<div class="ve"><p>', he = '<div class="vh"><p>';
    for (let i = a; i < b; i++) {
      const V = VERSES[i];
      // row E7: a new chapter starts a new paragraph in both languages (after פ/ס it already has)
      if (V.v === 1 && i > a && !VERSES[i - 1].brk) { en += '</p><p>'; he += '</p><p>'; }
      if (i === 0 && V.v !== 1) {   // the parasha opens mid-chapter: show the chapter with the first verse
        en += `<sup class="vn">${V.ch}:${V.v}</sup>${V.en} `;
        he += `<span class="hch">[${V.hch}]</span> ` + `<span class="hvn">${V.hv}</span> ${V.he} `;
      } else if (V.v === 1) {
        const m = V.en.match(/^(\s*)(<[^>]+>)*([A-Za-z“‘])/);
        let rest = V.en, first = '';
        const mm = V.en.match(/^([“‘]?[A-Za-z])/);
        if (mm) { first = mm[1]; rest = V.en.slice(first.length); }
        en += `<span class="drop">${V.ch}</span><span class="dropl">${first}</span>${rest} `;
        he += `<span class="hch">[${V.hch}]</span> ` + (V.aliyah ? `<span class="aliyah">${V.aliyah}</span>` : '') + `<span class="hvn">${V.hv}</span> ${V.he} `;
      } else {
        en += `<sup class="vn">${V.v}</sup>${V.en} `;
        he += (V.aliyah ? `<span class="aliyah">${V.aliyah}</span>` : '') + `<span class="hvn">${V.hv}</span> ${V.he} `;
      }
      // section break of the Torah scroll: פ = open portion, ס = closed portion (David, Oct 2026)
      if (V.brk) he += `<span class="brk">${V.brk}</span> `;
      if (V.brk && i < b - 1) { en += '</p><p>'; he += '</p><p>'; }
    }
    en += '</p></div>'; he += '</p>';
    if (b === NV) he += '<div class="endmark">פ פ פ</div>';
    he += '</div>';
    return `<div class="band">${en}${he}</div>`;
  }
  function bandH(a, b) {
    if (b <= a) return 0;
    const k = a + '-' + b;
    if (!(k in bandCache)) { bandBox.innerHTML = bandHTML(a, b); bandCache[k] = bandBox.firstChild.getBoundingClientRect().height; }
    return bandCache[k];
  }

  // ---------------- page fitting
  // Priority: a page shows its verses, then ALL of the Hebrew and English comments on those verses,
  // then as many notes as fit. Notes may run on to the next page; comments do not leave their verse's page
  // unless one verse's comments are longer than a page.
  let nv = 0;
  const plans = [];
  const avail = () => (plans.length === 0 ? AVAIL - HEAD : AVAIL);   // the first page gives room to the heading
  const NB = 100;          // most notes (single-column px) allowed to run on past a page (row E5: notes stay with their verse's page where they fit)
  const STRETCH = 0.15;    // if more than this share of the page is left empty, start the next verse here
  function limitCut(S, k) {
    if (k >= NV) return S.cuts.length - 1;
    const Y = S.segS[k];
    let lo = 0, hi = S.cuts.length - 1;
    while (lo < hi) { const mid = (lo + hi + 1) >> 1; if (S.cuts[mid].ye <= Y + 0.01) lo = mid; else hi = mid - 1; }
    return Math.max(lo, S.cur);
  }
  function pageTotal(k, c) {
    const h = { band: bandH(nv, k), hc: H(ST.hc, ST.hc.cur, c.hc), ec: H(ST.ec, ST.ec.cur, c.ec) };
    const bal = balance(ST.n, ST.n.cur, c.n); h.n = bal.h;
    const parts = [];
    if (h.band > 0) parts.push([h.band, SP.afterBand]);
    if (h.hc > 0) parts.push([SP.divHe + SP.afterDivHe + h.hc, SP.afterHc]);
    if (h.ec > 0) parts.push([SP.divEn + SP.afterDivEn + h.ec, SP.afterEc]);
    if (h.n > 0) parts.push([SP.rule + SP.afterRule + h.n, 0]);
    let y = 0; parts.forEach((p, i) => { y += p[0]; if (i < parts.length - 1) y += p[1]; });
    return { total: y, bal, h };
  }
  function fillMax(s, lo, hi, test) {   // largest cut index in [lo, hi] with test(c) true (test(lo) assumed true)
    while (lo < hi) { const mid = (lo + hi + 1) >> 1; if (test(mid)) lo = mid; else hi = mid - 1; }
    return lo;
  }
  function done() { return nv >= NV && ST.hc.cur >= ST.hc.cuts.length - 1 && ST.ec.cur >= ST.ec.cuts.length - 1 && ST.n.cur >= ST.n.cuts.length - 1; }
  function notesFor(k, c) {
    const Ln = limitCut(ST.n, k);
    c.n = fillMax('n', ST.n.cur, Ln, x => pageTotal(k, { hc: c.hc, ec: c.ec, n: x }).total <= avail());
    return Ln;
  }
  // proportional fill for a verse whose comments are longer than a page: Hebrew and English advance together
  function partial(k) {
    const tA = Math.max(0, k - 1), tB = k;
    const at = t => { const c = {}; for (const s of ['hc', 'ec']) { const S = ST[s]; c[s] = Math.min(limitCut(S, k), Math.max(S.cur, snap(S, target(S, t)))); } c.n = ST.n.cur; return c; };
    let lo = tA, hi = tB;
    if (pageTotal(k, at(lo)).total > avail()) lo = tA;
    for (let it = 0; it < 50; it++) { const mid = (lo + hi) / 2; if (pageTotal(k, at(mid)).total <= avail()) lo = mid; else hi = mid; }
    const c = at(lo);
    // make sure something moves
    if (c.hc === ST.hc.cur && c.ec === ST.ec.cur && k === nv) {
      for (const s of ['hc', 'ec']) if (ST[s].cur < limitCut(ST[s], k)) { c[s] = ST[s].cur + 1; break; }
    }
    notesFor(k, c);
    return c;
  }

  let guard = 0;
  while (!done() && guard++ < 400) {
    const pending = ['hc', 'ec'].some(s => ST[s].cur < limitCut(ST[s], nv));
    let chosen = null;
    for (let k = NV; k >= nv; k--) {
      if (k === nv && !pending && nv < NV) continue;
      if (k > nv && bandH(nv, k) > avail()) continue;
      const c = { hc: limitCut(ST.hc, k), ec: limitCut(ST.ec, k), n: ST.n.cur };
      if (pageTotal(k, c).total > avail()) continue;          // comments on these verses would not all fit
      const Ln = notesFor(k, c);
      const backlog = H(ST.n, c.n, Ln);
      const smallest = (k === nv) || (k === nv + 1 && !pending);
      if (backlog > NB && !smallest) continue;              // leave room for the notes
      if (k === NV && backlog > 0 && k - 1 > nv) continue;  // don't end the parasha on a page of leftover notes
      chosen = { k, c };
      break;
    }
    if (!chosen) {                                         // one verse's comments are longer than a page
      const k = pending ? nv : nv + 1;
      chosen = { k, c: partial(k) };
    } else if (chosen.k < NV) {
      // a lot of empty space left: start the next verse here, its comments continuing on the next page
      const r0 = pageTotal(chosen.k, chosen.c);
      const notesLeft = H(ST.n, chosen.c.n, limitCut(ST.n, chosen.k));
      if (avail() - r0.total > STRETCH * AVAIL && notesLeft < 1) {
        const k2 = chosen.k + 1;
        if (pageTotal(k2, chosen.c).total + SP.afterBand <= avail()) {
          const save = { hc: ST.hc.cur, ec: ST.ec.cur, n: ST.n.cur };
          const c2 = partial(k2);
          const hasHc = limitCut(ST.hc, k2) > chosen.c.hc, hasEc = limitCut(ST.ec, k2) > chosen.c.ec;
          if ((!hasHc || c2.hc > chosen.c.hc) && (!hasEc || c2.ec > chosen.c.ec) && (hasHc || hasEc)) chosen = { k: k2, c: c2, stretched: true };
          Object.assign(ST.hc, { cur: save.hc }); Object.assign(ST.ec, { cur: save.ec }); Object.assign(ST.n, { cur: save.n });
        }
      }
    }
    const r = pageTotal(chosen.k, chosen.c);
    const progressed = chosen.k > nv || ['hc', 'ec', 'n'].some(s => chosen.c[s] > ST[s].cur);
    if (!progressed) { log('WARN no progress at verse', nv); break; }
    if (chosen.stretched) log('INFO page starts verse', chosen.k - 1, 'and its comments continue overleaf');
    plans.push({ head: plans.length === 0 && HEAD > 0, nvStart: nv, nvEnd: chosen.k, from: { hc: ST.hc.cur, ec: ST.ec.cur, n: ST.n.cur }, to: { ...chosen.c }, m: r.bal.m, total: r.total, h: { ...r.h } });
    nv = chosen.k; for (const s of ['hc', 'ec', 'n']) ST[s].cur = chosen.c[s];
  }
  for (const s of ['hc', 'ec', 'n']) ST[s].cur = 0;

  // ---------------- splitting & fragments
  function textNodes(el) { const w = document.createTreeWalker(el, NodeFilter.SHOW_TEXT); const a = []; let n; while ((n = w.nextNode())) a.push(n); return a; }
  function findSplit(el, k, lh) {
    const top = el.getBoundingClientRect().top;
    const yb = top + k * lh;
    const cands = [];
    for (const n of textNodes(el)) {
      const d = n.data;
      for (let i = 0; i < d.length; i++) {
        const c = d.charCodeAt(i);
        if (c === 32 || c === 0xA0 || c === 0xAD || c === 10 || (c >= 0x0591 && c <= 0x05C7 && c !== 0x05BE && c !== 0x05C0 && c !== 0x05C3)) continue;
        cands.push([n, i]);
      }
    }
    const r = document.createRange();
    const cy = j => { const [n, i] = cands[j]; r.setStart(n, i); r.setEnd(n, i + 1); const rs = [...r.getClientRects()].filter(q => q.width > 0.01); if (!rs.length) return null; const R = rs.reduce((a, b) => (b.width > a.width ? b : a)); return (R.top + R.bottom) / 2; };
    let lo = 0, hi = cands.length;
    while (lo < hi) {
      const mid = (lo + hi) >> 1; let y = cy(mid); let j = mid;
      while (y === null && j < cands.length - 1) { j++; y = cy(j); }
      if (y === null || y > yb) hi = mid; else lo = mid + 1;
    }
    return cands[lo];
  }
  function split(el, k, lh) {
    const nTot = Math.round(el.getBoundingClientRect().height / lh);
    let pos = findSplit(el, k, lh);
    if (!pos) { log('WARN split failed', el.id, k); return [el, null]; }
    // a split can only fall inside a word at a soft hyphen: move back to it if needed
    {
      const all = textNodes(el); let g = 0, base = [];
      for (const n of all) { base.push(g); g += n.data.length; }
      const txt = all.map(n => n.data).join('');
      let gi = base[all.indexOf(pos[0])] + pos[1];
      if (/[A-Za-z’']/.test(txt[gi - 1] || '') && /[A-Za-z]/.test(txt[gi] || '')) {
        let q = gi - 1;
        while (q >= 0 && /[A-Za-z’']/.test(txt[q])) q--;
        if (q >= 0 && txt[q] === '\u00AD') {
          gi = q + 1;
          let ni = 0; while (ni < all.length - 1 && base[ni + 1] <= gi && !(base[ni + 1] === gi && all[ni].data.length === gi - base[ni] && false)) ni++;
          // prefer the node that contains gi as a start position
          for (let t = 0; t < all.length; t++) { if (gi >= base[t] && gi < base[t] + all[t].data.length) { ni = t; break; } }
          pos = [all[ni], gi - base[ni]];
        }
      }
    }
    // character just before the split point (document order)
    let prevChar = '';
    if (pos[1] > 0) prevChar = pos[0].data[pos[1] - 1];
    else { const all = textNodes(el); const ix = all.indexOf(pos[0]); for (let q = ix - 1; q >= 0; q--) { if (all[q].data.length) { prevChar = all[q].data[all[q].data.length - 1]; break; } } }
    const splitChar = pos[0].data[pos[1]];
    const r = document.createRange();
    r.setStart(pos[0], pos[1]); r.setEndAfter(el.lastChild);
    const frag = r.extractContents();
    const tail = el.cloneNode(false); tail.id = el.id + 't' + k; tail.classList.add('cut-start'); tail.classList.remove('first');
    tail.appendChild(frag);
    el.after(tail);
    el.classList.add('cut-end');
    if (prevChar === '\u00AD') {
      const tn = textNodes(el).filter(n => n.data.length); const last = tn[tn.length - 1];
      last.data = last.data.replace(/\u00AD$/, '\u2010');
    } else if (/[A-Za-z]/.test(prevChar) && /[a-z]/.test(splitChar)) log('WARN mid-word split', el.id, JSON.stringify(el.textContent.slice(-25)), JSON.stringify(tail.textContent.slice(0,25)));
    const h1 = el.getBoundingClientRect().height, h2 = tail.getBoundingClientRect().height;
    if (Math.abs(h1 - k * lh) > 0.75 || Math.abs(h2 - (nTot - k) * lh) > 0.75) log('WARN split mismatch', el.id, k, nTot, h1.toFixed(1), h2.toFixed(1));
    return [el, tail];
  }
  function fragment(S, a, b, box) {
    const A = S.cuts[a], B = S.cuts[b];
    const vis = new Set();
    let firstPlaced = true;
    const lastBi = B.li > 0 ? B.bi : B.bi - 1;
    for (let bi = A.bi; bi <= lastBi; bi++) {
      const blk = S.bl[bi];
      let el = blk.el;
      const endLine = (bi === B.bi && B.li > 0) ? B.li : blk.n;
      if (blk.splittable && endLine < blk.n) {
        const [head, tail] = split(el, endLine - blk.off, S.lh);
        el = head; blk.el = tail; blk.off = endLine;
      }
      el.style.marginTop = firstPlaced ? '0px' : blk.gap + 'px';
      box.appendChild(el);
      firstPlaced = false;
      vis.add(blk.vi);
    }
    return vis;
  }

  // ---------------- pages
  const book = document.getElementById('book');
  let pageNo = (PARASHA.first_page || 1) - 1;  // continuous numbering across parashot (parasha.json)
  const pages = [];
  function newPage() { const p = document.createElement('div'); p.className = 'page'; book.appendChild(p); pageNo++; pages.push(p); p.dataset.no = pageNo; return p; }
  function el(tag, cls, html) { const e = document.createElement(tag); if (cls) e.className = cls; if (html !== undefined) e.innerHTML = html; return e; }
  function sec(page, top, child) { const d = el('div', 'sec'); d.style.top = top + 'px'; d.appendChild(child); page.appendChild(d); return d; }

  function header(page, rangeEn, rangeHe, rightTitleEn, rightTitleHe) {
    const odd = pageNo % 2 === 1;
    const h = el('div', 'hdr');
    if (odd) {
      h.appendChild(el('span', 'l en-run', `${pageNo} / ${PARASHA.run_en}`));
      h.appendChild(el('span', 'r en-rng', rightTitleEn || rangeEn || ''));
    } else {
      h.appendChild(el('span', 'l he-rng', rightTitleHe || rangeHe || ''));
      h.appendChild(el('span', 'r he-run', `<span class="pn">${pageNo}</span> / ${PARASHA.run_he}`));
    }
    page.appendChild(h);
    page.appendChild(el('div', 'hrule'));
  }
  function ranges(vset) {
    const a = Math.min(...vset), b = Math.max(...vset);
    const A = VERSES[a], B = VERSES[b];
    let en, he;
    if (a === b) { en = `${A.ch}/${A.v}`; he = `${A.hch}/${A.hv}`; }
    else if (A.ch === B.ch) { en = `${A.ch}/${A.v}–${B.v}`; he = `${A.hch}/${A.hv}–${B.hv}`; }
    else { en = `${A.ch}/${A.v} – ${B.ch}/${B.v}`; he = `${A.hch}/${A.hv} – ${B.hch}/${B.hv}`; }
    return [en, he];
  }
  const stripProbe = document.getElementById('strip-probe');
  function strip(page, texts) {
    const txt = texts.join(' \n ').replace(/­/g, '');
    const found = [];
    for (const g of GLOSS) {
      const re = new RegExp(g.re, 'i'); const m = re.exec(txt);
      if (m) found.push([m.index, g]);
    }
    found.sort((x, y) => x[0] - y[0]);
    const want = [...new Set(found.map(f => f[1].label))];
    function fit(fs) {
      stripProbe.style.fontSize = fs + 'px';
      const seen = new Set(); const lines = ['']; const used = [];
      for (const [, g] of found) {
        if (seen.has(g.label)) continue;
        const piece = `<b>${g.label}</b> = ${g.gloss}`;
        let placed = false;
        for (let li = 0; li < (fs <= 8.2 ? 4 : 3) && !placed; li++) {
          if (li >= lines.length) lines.push('');
          const trial = lines[li] ? lines[li] + ' &nbsp;·&nbsp; ' + piece : piece;
          stripProbe.innerHTML = trial;
          if (stripProbe.getBoundingClientRect().width > 588) continue;
          lines[li] = trial; placed = true;
        }
        if (placed) { seen.add(g.label); used.push(g.label); }
      }
      return [lines.filter(x => x), used];
    }
    let fs = 9.2, [full, used] = fit(fs);
    for (const f2 of [8.7, 8.2, 7.8]) { if (used.length >= want.length) break; fs = f2; [full, used] = fit(fs); }
    stripProbe.style.fontSize = '';
    full.forEach((h, i) => {
      const d = el('div', 'stripline', '');
      d.style.top = (full.length === 1 ? 972 : full.length === 2 ? 966 + 12 * i : full.length === 3 ? 959 + 12 * i : 957 + 10.4 * i) + 'px';
      const sp = el('span', 'strip', h); if (fs !== 9.2) sp.style.fontSize = fs + 'px';
      d.appendChild(sp); page.appendChild(d);
    });
    if (used.length < want.length) log('WARN strip dropped', pageNo, want.filter(x => !used.includes(x)).join(', '));
    return used;
  }

  // front matter pages
  function staticPage(item) {
    const p = newPage();
    if (item.header) header(p, null, null, item.header.en, item.header.he);
    p.insertAdjacentHTML('beforeend', item.html);
    return p;
  }
  for (const item of FRONT.before) staticPage(item);

  const report = [];
  for (const pl of plans) {
    const page = newPage();
    let y = TOP;
    if (pl.head) {
      const hd = el('div', 'phead', `<div class="phead-he">${PARASHA.heading_he}</div><div class="phead-en">${PARASHA.heading_en} <span class="phead-ref">· ${PARASHA.verses}</span></div><div class="phead-rule"></div>`);
      sec(page, y, hd); y += HEAD;
    }
    const vset = new Set();
    for (let i = pl.nvStart; i < pl.nvEnd; i++) vset.add(i);
    const pieces = [];
    if (pl.nvEnd > pl.nvStart) {
      const b = el('div'); b.innerHTML = bandHTML(pl.nvStart, pl.nvEnd);
      const s = sec(page, y, b.firstChild); y += s.getBoundingClientRect().height; pieces.push(SP.afterBand);
    }
    const covered = new Set(); const sv = { hc: [], ec: [], n: [] };
    const texts = [];
    if (pl.to.hc > pl.from.hc) {
      if (pieces.length) y += pieces.pop();
      const d = el('div', 'divider he'); d.innerHTML = '<i></i><span>אִבְּן עֶזְרָא</span><i></i>'; sec(page, y, d); y += SP.divHe + SP.afterDivHe;
      const box = el('div'); const s = sec(page, y, box);
      fragment(ST.hc, pl.from.hc, pl.to.hc, box).forEach(v => { covered.add(v); sv.hc.push(v); });
      y += box.getBoundingClientRect().height; pieces.push(SP.afterHc);
    }
    if (pl.to.ec > pl.from.ec) {
      if (pieces.length) y += pieces.pop();
      const d = el('div', 'divider en'); d.innerHTML = '<i></i><span>IBN EZRA</span><i></i>'; sec(page, y, d); y += SP.divEn + SP.afterDivEn;
      const box = el('div'); sec(page, y, box);
      fragment(ST.ec, pl.from.ec, pl.to.ec, box).forEach(v => { covered.add(v); sv.ec.push(v); });
      texts.push(box.innerText);
      y += box.getBoundingClientRect().height; pieces.push(SP.afterEc);
    }
    if (pl.to.n > pl.from.n) {
      if (pieces.length) y += pieces.pop();
      sec(page, y, el('div', 'nrule')); y += SP.rule + SP.afterRule;
      const grid = el('div', 'notes'); const c1 = el('div'), c2 = el('div'); grid.appendChild(c1); grid.appendChild(c2);
      sec(page, y, grid);
      fragment(ST.n, pl.from.n, pl.m, c1).forEach(v => { covered.add(v); sv.n.push(v); });
      if (pl.to.n > pl.m) fragment(ST.n, pl.m, pl.to.n, c2).forEach(v => { covered.add(v); sv.n.push(v); });
      texts.push(c1.innerText, c2.innerText);
      y += grid.getBoundingClientRect().height;
    }
    const rv = new Set([...covered, ...vset]);
    const [en, he] = rv.size ? ranges(rv) : ['', ''];
    header(page, en, he);
    const used = strip(page, texts);
    report.push({ page: pageNo, verses: [pl.nvStart, pl.nvEnd], sv, bottom: Math.round(y), planned: Math.round(TOP + (pl.head ? HEAD : 0) + pl.total), terms: used, range: en });
    if (y > BOTTOM + 0.5) log('WARN overflow page', pageNo, y.toFixed(1));
  }
  for (const item of FRONT.after) staticPage(item);

  // remaining-in-measure check
  for (const s of ['hc', 'ec', 'n']) {
    const left = document.getElementById('m-' + s).children.length;
    if (left) log('WARN leftover blocks in', s, left);
  }
  document.getElementById('measure').remove();
  // final check, with every font loaded: sections must not overlap and must end above the strip
  await document.fonts.ready;
  for (const P of pages) {
    const pr = P.getBoundingClientRect();
    const secs = [...P.querySelectorAll(':scope > .sec')].map(e => { const q = e.getBoundingClientRect(); return [q.top - pr.top, q.bottom - pr.top]; });
    for (let i = 1; i < secs.length; i++) if (secs[i][0] < secs[i - 1][1] - 0.5) log('WARN overlap on page', P.dataset.no, 'section', i, secs[i - 1][1].toFixed(1), '>', secs[i][0].toFixed(1));
    if (secs.length && secs[secs.length - 1][1] > BOTTOM + 0.5) log('WARN past bottom on page', P.dataset.no, secs[secs.length - 1][1].toFixed(1));
    const rp = report.find(x => String(x.page) === P.dataset.no); if (rp && secs.length) rp.empty = Math.round(BOTTOM - secs[secs.length - 1][1]);
  }
  window.__LAYOUT = { pages: pageNo - ((PARASHA.first_page || 1) - 1), first_page: PARASHA.first_page || 1, last_page: pageNo, log: LOG, report };
  document.title = 'READY';
})().catch(e => { window.__LAYOUT = { error: String(e) + '\n' + e.stack }; document.title = 'READY'; });
