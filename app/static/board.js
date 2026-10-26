/* Không gian bảng cho bài thực hành (trường "board"): học viên kéo thả module, ghi nội dung
   trong module và kéo chấm nối để nối các module với nhau. Bài nộp lưu dạng
   {nodes: [{id, kind, x, y, title?, text, tag?, p?}], links: [{id, from, to, <trường ghi trên dây>}]}. */
const BOARD_NODE_W = 236;
let boardSeq = 0;

function boardUid(prefix) { return prefix + Date.now().toString(36) + Math.random().toString(36).slice(2, 6); }

/* Tạo bài làm rỗng từ module dựng sẵn, hoặc bổ sung module cố định còn thiếu vào bài đã lưu */
function boardInit(f, v) {
  const ok = v && typeof v === 'object' && Array.isArray(v.nodes);
  const b = ok ? JSON.parse(JSON.stringify(v)) : { nodes: [], links: [] };
  if (!Array.isArray(b.links)) b.links = [];
  const have = new Set(b.nodes.map(n => n.id));
  for (const n of f.nodes || []) {
    if (have.has(n.id) || (ok && !n.locked)) continue;
    b.nodes.push({ id: n.id, kind: n.kind, x: n.x, y: n.y, text: '' });
  }
  const kinds = {};
  for (const k of f.kinds) kinds[k.kind] = k;
  for (const n of b.nodes) {
    if (typeof n.text !== 'string') n.text = '';
    if (kinds[n.kind] && kinds[n.kind].props && (!n.p || typeof n.p !== 'object')) n.p = {};
  }
  return b;
}

const filled = v => typeof v === 'string' && v.trim() !== '';

const BoardField = {
  props: { f: Object, value: Object, readonly: Boolean },
  emits: ['dirty'],
  data() {
    return {
      uid: 'bn' + (++boardSeq), zoom: 0.8, panX: 0, panY: 0, sizes: {}, sel: null,
      op: null, draft: null, full: false, W: BOARD_NODE_W, vpW: 800, vpH: 560,
    };
  },
  computed: {
    kinds() { const m = {}; for (const k of this.f.kinds) m[k.kind] = k; return m; },
    presets() { const m = {}; for (const n of this.f.nodes || []) m[n.id] = n; return m; },
    nodeMap() { const m = {}; for (const n of this.value.nodes) m[n.id] = n; return m; },
    addable() { return this.f.kinds.filter(k => k.add); },
    size() { return this.f.size || [1600, 1000]; },
    paths() {
      return this.value.links.map(l => {
        const a = this.nodeMap[l.from], b = this.nodeMap[l.to];
        if (!a || !b) return null;
        const g = this.curve(a, this.box(a), b, this.box(b));
        const def = this.linkDef(l);
        const parts = def.map(x => filled(l[x.key]) ? (x.prefix || '') + l[x.key].trim() : '').filter(Boolean);
        return { l, d: g.d, mx: g.mx, my: g.my, fields: def, label: parts.join(' · '), sel: this.isSel('link', l.id) };
      }).filter(Boolean);
    },
    draftPath() {
      if (!this.draft) return '';
      const a = this.nodeMap[this.draft.from];
      const s = this.box(a);
      const k = this.draft.left ? -1 : 1;
      const x1 = this.draft.left ? a.x : a.x + s.w, y1 = a.y + s.h / 2, x2 = this.draft.x, y2 = this.draft.y;
      const c = Math.max(40, Math.abs(x2 - x1) / 2);
      return `M${x1},${y1} C${x1 + k * c},${y1} ${x2 - k * c},${y2} ${x2},${y2}`;
    },
    goals() { return (this.f.goals || []).map(g => ({ text: g.text, ...this.check(g) })); },
    goalsDone() { return this.goals.filter(g => g.done).length; },
    warnings() {
      const out = [];
      for (const w of this.f.warnings || []) {
        const n = this.nodeMap[w.node];
        if (w.type === 'maxIn' && n && this.degree(n.id) > w.max) out.push(w.text);
        if (w.type === 'tag' && n && n.tag === w.value) out.push(w.text);
        if (w.type === 'pair' && this.linked(w.node, w.other)) out.push(w.text);
      }
      return out;
    },
    matrix() {
      const s = this.f.summary;
      if (!s || s.type !== 'matrix') return null;
      const rows = this.value.nodes.filter(n => n.kind === s.rows);
      const cols = this.value.nodes.filter(n => n.kind === s.cols);
      return {
        cols: cols.map(c => this.title(c)),
        rows: rows.map(r => ({
          label: this.title(r),
          cells: cols.map(c => {
            const l = this.value.links.find(x => (x.from === r.id && x.to === c.id) || (x.from === c.id && x.to === r.id));
            if (!l) return { text: 'Không', none: true };
            const parts = s.cell.map(k => filled(l[k.key]) ? (k.prefix || '') + l[k.key].trim() : '').filter(Boolean);
            return { text: parts.length ? parts.join(' – ') : 'Có quyền (chưa ghi phạm vi)', missing: parts.length < s.cell.length };
          }),
        })),
      };
    },
    outline() {
      return this.f.kinds.map(k => ({
        k,
        nodes: this.value.nodes.filter(n => n.kind === k.kind).map(n => ({
          n, title: this.title(n),
          links: this.value.links.filter(l => l.from === n.id || l.to === n.id).map(l => {
            const other = this.nodeMap[l.from === n.id ? l.to : l.from];
            const def = this.linkDef(l);
            const extra = def.map(x => filled(l[x.key]) ? (x.prefix || x.label + ': ') + l[x.key].trim() : '').filter(Boolean).join('; ');
            return other ? (l.from === n.id ? '→ ' : '← ') + this.title(other) + (extra ? ' (' + extra + ')' : '') : '';
          }).filter(Boolean),
        })),
      })).filter(g => g.nodes.length);
    },
    pop() {
      // ô sửa chữ ghi trên dây đang chọn, đặt theo tọa độ màn hình
      if (!this.sel || this.sel.type !== 'link') return null;
      const p = this.paths.find(x => x.l.id === this.sel.id);
      if (!p) return null;
      const x = Math.min(Math.max(8, p.mx * this.zoom + this.panX - 140), Math.max(8, this.vpW - 290));
      const y = Math.min(Math.max(8, p.my * this.zoom + this.panY + 18), Math.max(8, this.vpH - 60 - 64 * p.fields.length));
      return { p, x, y };
    },
  },
  methods: {
    touch() { this.$emit('dirty'); },
    kindOf(n) { return this.kinds[n.kind] || { label: n.kind, color: 'slate' }; },
    title(n) { return (filled(n.title) && n.title.trim()) || (this.presets[n.id] && this.presets[n.id].title) || this.kindOf(n).label; },
    hint(n) { return (this.presets[n.id] && this.presets[n.id].hint) || this.kindOf(n).hint || 'Ghi nội dung…'; },
    locked(n) { return !!(this.presets[n.id] && this.presets[n.id].locked); },
    box(n) { return this.sizes[n.id] || { w: this.W, h: 130 }; },
    isSel(type, id) { return !!this.sel && this.sel.type === type && this.sel.id === id; },
    rows(t) { return Math.max(2, (t || '').split('\n').reduce((s, line) => s + Math.max(1, Math.ceil(line.length / 30)), 0)); },
    tone(n) { const k = this.kindOf(n); return (k.tones && n.tag && k.tones[n.tag]) || (n.tag ? 'set' : ''); },
    degree(id) { return this.value.links.filter(l => l.from === id || l.to === id).length; },
    linked(a, b) { return this.value.links.some(l => (l.from === a && l.to === b) || (l.from === b && l.to === a)); },
    linkDef(l) {
      const a = this.nodeMap[l.from], b = this.nodeMap[l.to];
      if (!a || !b) return [];
      const has = (v, k) => (Array.isArray(v) ? v : [v]).includes(k);
      const d = (this.f.links || []).find(x => (has(x.a, a.kind) && has(x.b, b.kind)) || (has(x.a, b.kind) && has(x.b, a.kind)));
      return d ? d.fields : [];
    },
    nodeFilled(n) {
      return filled(n.text) || (!this.locked(n) && filled(n.title))
        || (n.p && Object.values(n.p).some(filled));
    },
    pick(g) {
      const kinds = g.kind ? (Array.isArray(g.kind) ? g.kind : [g.kind]) : null;
      return this.value.nodes.filter(n => (g.ids ? g.ids.includes(n.id) : kinds.includes(n.kind)));
    },
    check(g) {
      const ks = v => (Array.isArray(v) ? v : [v]);
      const between = (l, a, b) => {
        const x = this.nodeMap[l.from], y = this.nodeMap[l.to];
        return x && y && ((ks(a).includes(x.kind) && ks(b).includes(y.kind)) || (ks(a).includes(y.kind) && ks(b).includes(x.kind)));
      };
      let have = 0, need = 1;
      if (g.type === 'filled') {
        const ns = this.pick(g); have = ns.filter(this.nodeFilled).length; need = g.min || ns.length;
      } else if (g.type === 'tagged') {
        const ns = this.pick(g); have = ns.filter(n => filled(n.tag)).length; need = g.min || ns.length;
      } else if (g.type === 'props') {
        const ns = this.pick(g); need = ns.length * g.fields.length;
        have = ns.reduce((s, n) => s + g.fields.filter(k => n.p && filled(n.p[k])).length, 0);
      } else if (g.type === 'links') {
        have = this.value.links.filter(l => between(l, g.a, g.b)).length; need = g.min || 1;
      } else if (g.type === 'each') {
        const ns = this.pick(g); need = ns.length;
        have = ns.filter(n => this.value.links.some(l => (l.from === n.id || l.to === n.id)
          && ks(g.to).includes((this.nodeMap[l.from === n.id ? l.to : l.from] || {}).kind))).length;
      } else if (g.type === 'linkfield') {
        const ls = this.value.links.filter(l => between(l, g.a, g.b));
        need = Math.max(g.min || 1, ls.length);
        have = ls.filter(l => g.fields.every(k => filled(l[k]))).length;
      }
      need = Math.max(need, 1);
      return { done: have >= need, progress: Math.min(have, need) + '/' + need };
    },
    /* đường cong nối hai module: đi ra từ cạnh gần nhau nhất */
    curve(a, sa, b, sb) {
      let p0, p3, n0, n3;
      if (b.x > a.x + sa.w + 16) { p0 = [a.x + sa.w, a.y + sa.h / 2]; p3 = [b.x, b.y + sb.h / 2]; n0 = [1, 0]; n3 = [-1, 0]; }
      else if (b.x + sb.w < a.x - 16) { p0 = [a.x, a.y + sa.h / 2]; p3 = [b.x + sb.w, b.y + sb.h / 2]; n0 = [-1, 0]; n3 = [1, 0]; }
      else if (b.y > a.y) { p0 = [a.x + sa.w / 2, a.y + sa.h]; p3 = [b.x + sb.w / 2, b.y]; n0 = [0, 1]; n3 = [0, -1]; }
      else { p0 = [a.x + sa.w / 2, a.y]; p3 = [b.x + sb.w / 2, b.y + sb.h]; n0 = [0, -1]; n3 = [0, 1]; }
      const c = Math.max(36, Math.hypot(p3[0] - p0[0], p3[1] - p0[1]) / 2.4);
      const p1 = [p0[0] + n0[0] * c, p0[1] + n0[1] * c], p2 = [p3[0] + n3[0] * c, p3[1] + n3[1] * c];
      // chừa chỗ cho đầu mũi tên
      const e = [p3[0] + n3[0] * 6, p3[1] + n3[1] * 6];
      return {
        d: `M${p0[0]},${p0[1]} C${p1[0]},${p1[1]} ${p2[0]},${p2[1]} ${e[0]},${e[1]}`,
        mx: (p0[0] + 3 * p1[0] + 3 * p2[0] + p3[0]) / 8, my: (p0[1] + 3 * p1[1] + 3 * p2[1] + p3[1]) / 8,
      };
    },
    toWorld(e) {
      const r = this.$refs.vp.getBoundingClientRect();
      return { x: (e.clientX - r.left - this.panX) / this.zoom, y: (e.clientY - r.top - this.panY) / this.zoom };
    },
    down(e) {
      if (e.button > 0) return;
      const t = e.target;
      if (t.closest('textarea, input, select, button, .bn-pop')) return;
      const p = this.toWorld(e);
      const port = t.closest('.bn-port');
      const node = t.closest('.bn-node');
      const hit = t.closest('.bn-hit');
      if (hit) { this.sel = { type: 'link', id: hit.dataset.id }; return; }
      if (port && !this.readonly) {
        this.draft = { from: port.dataset.id, left: port.dataset.side === 'l', x: p.x, y: p.y };
      } else if (node && !this.readonly) {
        const n = this.nodeMap[node.dataset.id];
        this.sel = { type: 'node', id: n.id };
        this.op = { type: 'node', n, dx: p.x - n.x, dy: p.y - n.y, moved: false };
      } else {
        if (!node) this.sel = null;
        else this.sel = { type: 'node', id: node.dataset.id };
        this.op = { type: 'pan', x: e.clientX, y: e.clientY, px: this.panX, py: this.panY };
      }
      e.preventDefault();
      window.addEventListener('pointermove', this.move);
      window.addEventListener('pointerup', this.up);
      window.addEventListener('pointercancel', this.up);
    },
    move(e) {
      if (this.draft) { const p = this.toWorld(e); this.draft.x = p.x; this.draft.y = p.y; return; }
      const o = this.op;
      if (!o) return;
      if (o.type === 'pan') { this.panX = o.px + e.clientX - o.x; this.panY = o.py + e.clientY - o.y; return; }
      const p = this.toWorld(e), s = this.box(o.n);
      o.n.x = Math.round(Math.min(Math.max(0, p.x - o.dx), this.size[0] - s.w));
      o.n.y = Math.round(Math.min(Math.max(0, p.y - o.dy), this.size[1] - s.h));
      o.moved = true;
    },
    up(e) {
      window.removeEventListener('pointermove', this.move);
      window.removeEventListener('pointerup', this.up);
      window.removeEventListener('pointercancel', this.up);
      if (this.draft) {
        const el = document.elementFromPoint(e.clientX, e.clientY);
        const target = el && el.closest('.bn-node');
        const from = this.draft.from;
        this.draft = null;
        if (target && this.$el.contains(target)) {
          const to = target.dataset.id;
          if (to !== from && !this.linked(from, to)) {
            const l = { id: boardUid('l'), from, to };
            this.value.links.push(l);
            this.sel = { type: 'link', id: l.id };
            this.touch();
          }
        }
      }
      if (this.op && this.op.type === 'node' && this.op.moved) {
        this.op.n.x = Math.round(this.op.n.x / 10) * 10;
        this.op.n.y = Math.round(this.op.n.y / 10) * 10;
        this.touch();
      }
      this.op = null;
    },
    wheel(e) {
      if (e.ctrlKey || e.metaKey) {
        e.preventDefault();
        const r = this.$refs.vp.getBoundingClientRect();
        this.zoomAt(e.deltaY < 0 ? 1.1 : 1 / 1.1, e.clientX - r.left, e.clientY - r.top);
      } else if (this.full) {
        e.preventDefault();
        this.panX -= e.deltaX; this.panY -= e.deltaY;
      }
    },
    zoomAt(k, cx, cy) {
      const z = Math.min(1.6, Math.max(0.3, this.zoom * k));
      this.panX = cx - (cx - this.panX) * z / this.zoom;
      this.panY = cy - (cy - this.panY) * z / this.zoom;
      this.zoom = z;
    },
    zoomBy(k) { this.zoomAt(k, this.vpW / 2, this.vpH / 2); },
    fit() {
      const ns = this.value.nodes;
      if (!ns.length) return;
      let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
      for (const n of ns) { const s = this.box(n); x0 = Math.min(x0, n.x); y0 = Math.min(y0, n.y); x1 = Math.max(x1, n.x + s.w); y1 = Math.max(y1, n.y + s.h); }
      for (const z of this.f.zones || []) { x0 = Math.min(x0, z.x); y0 = Math.min(y0, z.y); x1 = Math.max(x1, z.x + z.w); y1 = Math.max(y1, z.y + z.h); }
      const pad = 24;
      // không thu nhỏ quá mức chữ còn đọc được; bảng rộng hơn khung thì canh trái, kéo nền để xem tiếp
      this.zoom = Math.max(0.72, Math.min(1, (this.vpW - 2 * pad) / (x1 - x0), (this.vpH - 2 * pad) / (y1 - y0)));
      const w = (x1 - x0) * this.zoom;
      this.panX = (w <= this.vpW - 2 * pad ? (this.vpW - w) / 2 : pad) - x0 * this.zoom;
      this.panY = pad - y0 * this.zoom;
    },
    measure() {
      const vp = this.$refs.vp;
      if (vp) { this.vpW = vp.clientWidth; this.vpH = vp.clientHeight; }
      for (const el of this.$el.querySelectorAll('.bn-node')) {
        const id = el.dataset.id, s = this.sizes[id];
        if (!s || s.w !== el.offsetWidth || s.h !== el.offsetHeight) this.sizes[id] = { w: el.offsetWidth, h: el.offsetHeight };
      }
    },
    add(k) {
      const n = { id: boardUid('n'), kind: k.kind, text: '', title: '' };
      if (k.props) n.p = {};
      const c = this.value.nodes.filter(x => x.kind === k.kind).length % 6;
      n.x = Math.round(Math.min(Math.max(0, (this.vpW / 2 - this.panX) / this.zoom - this.W / 2 + c * 18), this.size[0] - this.W));
      n.y = Math.round(Math.min(Math.max(0, (this.vpH / 2 - this.panY) / this.zoom - 60 + c * 18), this.size[1] - 160));
      this.value.nodes.push(n);
      this.sel = { type: 'node', id: n.id };
      this.touch();
      this.$nextTick(() => { const el = this.$el.querySelector(`.bn-node[data-id="${n.id}"] .bn-title`); if (el) el.focus(); });
    },
    removeNode(n) {
      if (this.locked(n)) return;
      if (this.nodeFilled(n) && !confirm('Xóa module “' + this.title(n) + '” và các dây nối của nó?')) return;
      this.value.links = this.value.links.filter(l => l.from !== n.id && l.to !== n.id);
      this.value.nodes.splice(this.value.nodes.indexOf(n), 1);
      this.sel = null;
      this.touch();
    },
    removeLink(l) {
      this.value.links.splice(this.value.links.indexOf(l), 1);
      this.sel = null;
      this.touch();
    },
    key(e) {
      if (e.key === 'Escape') { if (this.full) this.toggleFull(); this.sel = null; return; }
      if (this.readonly || !this.sel || (e.key !== 'Delete' && e.key !== 'Backspace')) return;
      if (e.target.closest && e.target.closest('textarea, input, select')) return;
      if (!this.$el.contains(document.activeElement) && document.activeElement !== document.body) return;
      if (this.sel.type === 'link') { const l = this.value.links.find(x => x.id === this.sel.id); if (l) { e.preventDefault(); this.removeLink(l); } }
      else { const n = this.nodeMap[this.sel.id]; if (n && !this.locked(n)) { e.preventDefault(); this.removeNode(n); } }
    },
    toggleFull() {
      this.full = !this.full;
      document.body.classList.toggle('bn-lock', this.full);
      this.$nextTick(() => { this.measure(); this.fit(); });
    },
    focusNode(id) {
      const n = this.nodeMap[id];
      if (!n) return;
      const s = this.box(n);
      this.panX = this.vpW / 2 - (n.x + s.w / 2) * this.zoom;
      this.panY = this.vpH / 2 - (n.y + s.h / 2) * this.zoom;
      this.sel = { type: 'node', id };
    },
  },
  mounted() {
    this.measure();
    this.$nextTick(() => { this.measure(); this.fit(); });
    this.ro = typeof ResizeObserver !== 'undefined' ? new ResizeObserver(() => this.measure()) : null;
    if (this.ro) this.ro.observe(this.$refs.vp);
    window.addEventListener('keydown', this.key);
  },
  updated() { this.measure(); },
  beforeUnmount() {
    if (this.ro) this.ro.disconnect();
    window.removeEventListener('keydown', this.key);
    this.up({ clientX: -1, clientY: -1 });
    if (this.full) document.body.classList.remove('bn-lock');
  },
  template: `
  <div class="board" :class="{ 'bn-full': full, 'bn-ro': readonly }">
    <details v-if="!readonly" class="bn-guide" open>
      <summary>Hướng dẫn làm bài</summary>
      <div class="bn-guide-body">
        <div>
          <b>Thao tác trên bảng</b>
          <ul>
            <li><b>Viết:</b> bấm vào ô trong module và gõ nội dung.</li>
            <li><b>Nối:</b> kéo chấm tròn ở mép trái hoặc phải của module, thả lên module khác. Thả nhầm thì chọn dây, nhấn Delete.</li>
            <li><b>Ghi chú trên dây:</b> bấm nhãn ở giữa dây, điền rồi bấm Xong.</li>
            <li><b>Sắp xếp:</b> kéo phần đầu module để di chuyển. Kéo nền trống để xem phần khác của bảng.</li>
            <li><b>Thêm/xóa:</b> dùng nút "Thêm module"; module tự thêm có dấu × để xóa.</li>
            <li><b>Phóng to:</b> nút + / −, Ctrl + cuộn chuột, hoặc "Toàn màn hình" cho dễ làm.</li>
          </ul>
        </div>
        <div v-if="f.steps && f.steps.length">
          <b>Các bước làm bài</b>
          <ol><li v-for="(s, i) in f.steps" :key="i">{{ s }}</li></ol>
          <p class="muted">Danh sách Nhiệm vụ bên dưới tự đánh dấu ✓ khi bạn làm đủ. Bài được lưu khi bấm "Nộp bài"; nộp lại bao nhiêu lần cũng được khi bài còn mở.</p>
        </div>
      </div>
    </details>
    <div class="bn-goals" v-if="goals.length">
      <div class="bn-goals-head">
        <b>Nhiệm vụ</b>
        <span class="bn-meter"><i :style="{ width: (100 * goalsDone / goals.length) + '%' }"></i></span>
        <span class="muted">{{ goalsDone }}/{{ goals.length }}</span>
        <span v-if="goalsDone === goals.length" class="bn-cheer">Đủ ý chính. Đọc lại một lượt rồi nộp bài.</span>
      </div>
      <ul>
        <li v-for="(g, i) in goals" :key="i" :class="{ done: g.done }"><span class="bn-tick">{{ g.done ? '✓' : '' }}</span>{{ g.text }} <span class="muted">{{ g.progress }}</span></li>
      </ul>
      <div v-for="(w, i) in warnings" :key="'w' + i" class="bn-warn">⚠ {{ w }}</div>
    </div>

    <div class="bn-toolbar">
      <template v-if="!readonly">
        <span class="bn-tlabel">Thêm module:</span>
        <button v-for="k in addable" :key="k.kind" class="btn sm bn-add" :class="'tone-' + k.color" @click="add(k)"><span>{{ k.icon }}</span>{{ k.label }}</button>
      </template>
      <span v-else class="bn-tlabel">Kéo nền để xem các phần của bảng</span>
      <div class="grow"></div>
      <button class="btn sm" @click="zoomBy(1 / 1.2)" title="Thu nhỏ" aria-label="Thu nhỏ">−</button>
      <span class="bn-zoom">{{ Math.round(zoom * 100) }}%</span>
      <button class="btn sm" @click="zoomBy(1.2)" title="Phóng to" aria-label="Phóng to">+</button>
      <button class="btn sm" @click="fit">Xem toàn bộ</button>
      <button class="btn sm" @click="toggleFull">{{ full ? '✕ Thoát toàn màn hình' : '⛶ Toàn màn hình' }}</button>
    </div>

    <div class="bn-vp" ref="vp" @pointerdown="down" @wheel="wheel" :class="{ panning: op && op.type === 'pan', linking: draft }">
      <div class="bn-world" :style="{ width: size[0] + 'px', height: size[1] + 'px', transform: 'translate(' + panX + 'px,' + panY + 'px) scale(' + zoom + ')' }">
        <div v-for="(z, i) in f.zones || []" :key="'z' + i" class="bn-zone" :class="'tone-' + z.color"
          :style="{ left: z.x + 'px', top: z.y + 'px', width: z.w + 'px', height: z.h + 'px' }">
          <span>{{ z.label }}</span><small v-if="z.hint">{{ z.hint }}</small>
        </div>
        <svg class="bn-svg" :width="size[0]" :height="size[1]">
          <defs>
            <marker :id="uid + 'a'" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" class="bn-arrow"/></marker>
            <marker :id="uid + 's'" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" class="bn-arrow sel"/></marker>
          </defs>
          <g v-for="p in paths" :key="p.l.id">
            <path :d="p.d" class="bn-link" :class="{ sel: p.sel, empty: p.fields.length && !p.label }" :marker-end="'url(#' + uid + (p.sel ? 's' : 'a') + ')'"/>
            <path :d="p.d" class="bn-hit" :data-id="p.l.id"/>
          </g>
          <path v-if="draft" :d="draftPath" class="bn-link draft"/>
        </svg>
        <template v-for="p in paths" :key="'lb' + p.l.id">
          <button v-if="p.fields.length || p.sel" class="bn-linklabel" :class="{ sel: p.sel, empty: !p.label }"
            :style="{ left: p.mx + 'px', top: p.my + 'px' }" @click="sel = { type: 'link', id: p.l.id }">
            {{ p.label || (readonly ? 'Chưa ghi' : '+ ghi ' + p.fields.map(x => x.label.toLowerCase()).join(', ')) }}
          </button>
        </template>
        <div v-for="n in value.nodes" :key="n.id" class="bn-node" :data-id="n.id"
          :class="['tone-' + kindOf(n).color, { sel: isSel('node', n.id), lit: draft && draft.from !== n.id, done: nodeFilled(n) }]"
          :style="{ left: n.x + 'px', top: n.y + 'px', width: W + 'px' }">
          <div class="bn-head">
            <span class="bn-ico">{{ kindOf(n).icon }}</span><span class="bn-kind">{{ kindOf(n).label }}</span>
            <span v-if="degree(n.id)" class="bn-deg" :title="degree(n.id) + ' dây nối'">{{ degree(n.id) }} ⟷</span>
            <button v-if="!readonly && !locked(n)" class="bn-x" title="Xóa module" @click="removeNode(n)">✕</button>
          </div>
          <div v-if="locked(n) || readonly" class="bn-title">{{ title(n) }}</div>
          <input v-else class="bn-title" v-model="n.title" :placeholder="title(n)" maxlength="120" @input="touch">
          <select v-if="kindOf(n).options && !readonly" v-model="n.tag" class="bn-tag" :class="'tag-' + tone(n)" @change="touch">
            <option :value="undefined">{{ kindOf(n).optionLabel || 'Chọn…' }}</option>
            <option v-for="o in kindOf(n).options" :key="o" :value="o">{{ o }}</option>
          </select>
          <span v-else-if="kindOf(n).options" class="bn-tag" :class="'tag-' + tone(n)">{{ n.tag || 'Chưa chọn' }}</span>
          <label v-for="pp in kindOf(n).props || []" :key="pp.key" class="bn-prop">
            <span>{{ pp.label }}</span>
            <input v-model="n.p[pp.key]" :placeholder="pp.placeholder || ''" :readonly="readonly" maxlength="200" @input="touch">
          </label>
          <textarea class="bn-text" v-model="n.text" :placeholder="readonly ? '' : hint(n)" :readonly="readonly" :rows="rows(n.text)" maxlength="1500" @input="touch"></textarea>
          <template v-if="!readonly">
            <span class="bn-port bn-port-l" :data-id="n.id" data-side="l" title="Kéo chấm này sang module khác để nối"></span>
            <span class="bn-port" :data-id="n.id" title="Kéo chấm này sang module khác để nối"></span>
          </template>
        </div>
      </div>

      <div v-if="pop" class="bn-pop" :style="{ left: pop.x + 'px', top: pop.y + 'px' }">
        <div class="bn-pop-head"><b>{{ title(nodeMap[pop.p.l.from]) }} → {{ title(nodeMap[pop.p.l.to]) }}</b></div>
        <label v-for="x in pop.p.fields" :key="x.key" class="bn-prop">
          <span>{{ x.label }}</span>
          <input v-model="pop.p.l[x.key]" :placeholder="x.placeholder || ''" :readonly="readonly" maxlength="200" @input="touch" @keydown.enter="sel = null">
        </label>
        <div class="row" style="gap:6px;margin-top:6px">
          <button class="btn sm" @click="sel = null">Xong</button>
          <div class="grow"></div>
          <button v-if="!readonly" class="btn sm ghost danger" @click="removeLink(pop.p.l)">Xóa dây nối</button>
        </div>
      </div>
      <div class="bn-help" v-if="!readonly">Kéo module để sắp xếp · kéo chấm <i></i> ở mép trái hoặc phải sang module khác để nối · bấm nhãn trên dây để ghi chú · Ctrl + cuộn để phóng to</div>
    </div>

    <div v-if="matrix" class="bn-summary">
      <b>{{ f.summary.title || 'Bảng tự lập từ các dây nối' }}</b>
      <div class="tablewrap"><table class="formtable bn-matrix">
        <thead><tr><th></th><th v-for="c in matrix.cols" :key="c">{{ c }}</th></tr></thead>
        <tbody><tr v-for="r in matrix.rows" :key="r.label"><td class="rowlabel">{{ r.label }}</td>
          <td v-for="(c, j) in r.cells" :key="j" :class="{ none: c.none, missing: c.missing }">{{ c.text }}</td></tr></tbody>
      </table></div>
    </div>
    <details class="bn-summary bn-outline">
      <summary>Bản đọc nhanh: toàn bộ nội dung trên bảng dạng văn bản</summary>
      <div v-for="g in outline" :key="g.k.kind">
        <h4>{{ g.k.icon }} {{ g.k.label }}</h4>
        <ul><li v-for="x in g.nodes" :key="x.n.id">
          <a href="#" @click.prevent="focusNode(x.n.id)"><b>{{ x.title }}</b></a><span v-if="x.n.tag" class="tag">{{ x.n.tag }}</span>
          <template v-for="pp in kindOf(x.n).props || []" :key="pp.key"><span v-if="x.n.p && x.n.p[pp.key]"> · {{ pp.label }}: {{ x.n.p[pp.key] }}</span></template>
          <div v-if="x.n.text" class="bn-otext">{{ x.n.text }}</div>
          <div v-for="(t, i) in x.links" :key="i" class="muted bn-olink">{{ t }}</div>
        </li></ul>
      </div>
    </details>
  </div>`,
};
