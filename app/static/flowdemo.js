/* Mô hình động dạng sơ đồ khối (khối {"t": "widget", "name": "flow", "spec": ...} trong bài học).
   spec = {w, h, label, nodes: [{id, x, y, w, h, t: [dòng…], k: note|brand|ok|bad|warn}],
           edges: [{id, a, b, d?, lb?}], notes: [{x, y, t, a?}],
           scenarios: [{name, intro, set?: {node: [dòng…]}, steps: [{s, t, x, on: [node], go: [edge], msg, tag: {node: chữ},
                                               tone: {node: ok|bad|warn}, set: {node: [dòng…]}, code}]}]}
   Bước 0 là toàn cảnh (như hình tĩnh). Từ bước 1: khối đang xét được tô đậm, khối chưa tới mờ đi,
   gói dữ liệu chạy dọc các mũi tên của bước. Dữ liệu sinh từ tools/ai_agent_flows.py. */
let flowSeq = 0;

function flowRoute(A, B) {
  const ac = [A.x + A.w / 2, A.y + A.h / 2], bc = [B.x + B.w / 2, B.y + B.h / 2];
  if (B.x >= A.x + A.w || B.x + B.w <= A.x) {
    const right = B.x >= A.x + A.w;
    const x1 = right ? A.x + A.w : A.x, x2 = right ? B.x : B.x + B.w;
    if (Math.abs(ac[1] - bc[1]) < 2) return `M${x1},${ac[1]} H${x2}`;
    const mx = Math.round((x1 + x2) / 2);
    return `M${x1},${ac[1]} H${mx} V${bc[1]} H${x2}`;
  }
  const down = bc[1] > ac[1];
  const y1 = down ? A.y + A.h : A.y, y2 = down ? B.y : B.y + B.h;
  if (Math.abs(ac[0] - bc[0]) < 2) return `M${ac[0]},${y1} V${y2}`;
  const my = Math.round((y1 + y2) / 2);
  return `M${ac[0]},${y1} V${my} H${bc[0]} V${y2}`;
}

const FlowDemo = {
  name: 'FlowDemo',
  props: { spec: Object, caption: String },
  data() {
    return { uid: 'flw' + (++flowSeq), sc: 0, step: 0, timer: null, pk: {}, lbl: {} };
  },
  created() { this.paths = {}; this.raf = null; },
  computed: {
    scenario() { return this.spec.scenarios[this.sc]; },
    steps() { return this.scenario.steps; },
    cur() { return this.step ? this.steps[this.step - 1] : null; },
    nodeMap() { const m = {}; for (const n of this.spec.nodes) m[n.id] = n; return m; },
    edges() {
      return this.spec.edges.map(e => ({ ...e, d: e.d || flowRoute(this.nodeMap[e.a], this.nodeMap[e.b]) }));
    },
    // khối, mũi tên đã đi qua ở các bước trước bước hiện tại
    seenNodes() { const s = new Set(); this.steps.slice(0, this.step).forEach(st => (st.on || []).forEach(n => s.add(n))); return s; },
    seenEdges() { const s = new Set(); this.steps.slice(0, this.step).forEach(st => (st.go || []).forEach(n => s.add(n))); return s; },
    packets() {
      if (!this.cur || !this.cur.go) return [];
      const m = this.cur.msg;
      return this.cur.go.map(id => {
        let text = typeof m === 'object' && m ? (m[id] || '') : (m || '');
        if (text.length > 30) text = text.slice(0, 29) + '…';
        return { id, text, w: text ? Math.round(text.length * 6.3 + 16) : 14 };
      });
    },
  },
  watch: {
    step() { this.pk = {}; this.$nextTick(this.animate); },
    sc() { this.pk = {}; this.$nextTick(this.animate); },
  },
  mounted() {
    // nhãn trên mũi tên đặt ở giữa đường đi
    const lbl = {};
    for (const e of this.edges) {
      const p = this.paths[e.id];
      if (e.lb && p) { const q = p.getPointAtLength(p.getTotalLength() / 2); lbl[e.id] = [q.x, q.y]; }
    }
    this.lbl = lbl;
  },
  beforeUnmount() { this.stop(); if (this.raf) cancelAnimationFrame(this.raf); },
  methods: {
    setPath(id, el) { if (el) this.paths[id] = el; },
    nodeCls(n) {
      const c = ['flw-node', 'k-' + (n.k || 'note')];
      if (!this.cur) return c;
      const tone = this.cur.tone && this.cur.tone[n.id];
      if ((this.cur.on || []).includes(n.id)) c.push('on', tone ? 't-' + tone : '');
      else if (this.seenNodes.has(n.id)) c.push('seen');
      else c.push('dim');
      return c;
    },
    lines(n) {
      return (this.cur && this.cur.set && this.cur.set[n.id]) || (this.scenario.set && this.scenario.set[n.id]) || n.t;
    },
    lineY(n, i) {
      const L = this.lines(n).length;
      return n.y + n.h / 2 - (L - 1) * 8.2 + i * 16.4 + 4.5;
    },
    edgeCls(e) {
      if (!this.cur) return 'flw-edge';
      if ((this.cur.go || []).includes(e.id)) return 'flw-edge go';
      return this.seenEdges.has(e.id) ? 'flw-edge seen' : 'flw-edge dim';
    },
    marker(e) {
      const c = this.edgeCls(e);
      return `url(#${this.uid}-${c.includes('go') ? 'go' : c.includes('dim') ? 'dim' : 'idle'})`;
    },
    tagOf(n) { return this.cur && this.cur.tag ? this.cur.tag[n.id] : null; },
    tagTone(n) { return this.cur && this.cur.tone ? this.cur.tone[n.id] || '' : ''; },
    tagW(t) { return Math.round(t.length * 6.2 + 16); },
    // gói dữ liệu chạy từ đầu đến cuối mỗi mũi tên của bước
    animate() {
      if (this.raf) cancelAnimationFrame(this.raf);
      const items = this.packets.map(p => ({ id: p.id, el: this.paths[p.id] })).filter(x => x.el);
      const reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
      if (reduce) { this.pk = {}; return; }
      const t0 = performance.now(), dur = 1300;
      const frame = now => {
        const k = Math.min(1, (now - t0) / dur);
        const e = 1 - Math.pow(1 - k, 3);
        const pk = {};
        for (const it of items) {
          const q = it.el.getPointAtLength(it.el.getTotalLength() * e);
          pk[it.id] = [q.x, q.y, k < .8 ? 1 : (1 - k) / .2];
        }
        this.pk = pk;
        if (k < 1) this.raf = requestAnimationFrame(frame);
      };
      this.raf = requestAnimationFrame(frame);
    },
    go(s) { this.stop(); this.step = Math.max(0, Math.min(this.steps.length, s)); },
    pick(i) { this.stop(); this.sc = i; this.step = 0; },
    play() {
      if (this.timer) return this.stop();
      if (this.step >= this.steps.length) this.step = 0;
      const tick = () => { this.step += 1; if (this.step >= this.steps.length) this.stop(); };
      tick();
      this.timer = setInterval(tick, 3200);
    },
    stop() { if (this.timer) { clearInterval(this.timer); this.timer = null; } },
  },
  template: `
  <figure class="vdb flw" :aria-label="spec.label">
    <div class="vdb-ask" v-if="spec.scenarios.length > 1" style="margin-top:0;margin-bottom:10px">
      <span class="vdb-label">Tình huống:</span>
      <button v-for="(s, i) in spec.scenarios" :key="i" type="button" class="vdb-chip" :class="{ on: sc === i }" @click="pick(i)">{{ s.name }}</button>
    </div>
    <div class="vdb-steps">
      <button type="button" class="vdb-step" :class="{ on: step === 0 }" @click="go(0)"><b>0</b><span>Toàn cảnh</span></button>
      <button v-for="(s, i) in steps" :key="sc + '-' + i" type="button" class="vdb-step" :class="{ on: step === i + 1, done: step > i + 1 }" @click="go(i + 1)">
        <b>{{ i + 1 }}</b><span>{{ s.s }}</span>
      </button>
      <span class="vdb-nav">
        <button type="button" class="btn" :disabled="step === 0" @click="go(step - 1)" aria-label="Bước trước">←</button>
        <button type="button" class="btn primary" @click="play">{{ timer ? '⏸ Dừng' : step >= steps.length ? '↺ Chạy lại' : '▶ Tự chạy' }}</button>
        <button type="button" class="btn" :disabled="step >= steps.length" @click="go(step + 1)" aria-label="Bước sau">→</button>
      </span>
    </div>

    <div class="vdb-stage">
      <svg :viewBox="'0 0 ' + spec.w + ' ' + spec.h" class="flw-svg" role="img" :aria-label="spec.label">
        <defs>
          <marker v-for="m in ['idle', 'go', 'dim']" :key="m" :id="uid + '-' + m" viewBox="0 0 10 10" refX="9" refY="5"
                  markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" :class="'flw-mk ' + m"/></marker>
        </defs>
        <text v-for="(t, i) in spec.notes || []" :key="'n' + i" :x="t.x" :y="t.y" font-size="12" :text-anchor="t.a || 'start'" class="flw-note">{{ t.t }}</text>
        <g v-for="e in edges" :key="e.id">
          <path :d="e.d" :class="edgeCls(e)" :marker-end="marker(e)" :ref="el => setPath(e.id, el)"/>
          <text v-if="e.lb && lbl[e.id]" :x="lbl[e.id][0]" :y="lbl[e.id][1] - 6" font-size="11" text-anchor="middle" class="flw-elb">{{ e.lb }}</text>
        </g>
        <g v-for="n in spec.nodes" :key="n.id" :class="nodeCls(n)">
          <rect :x="n.x" :y="n.y" :width="n.w" :height="n.h" rx="9"/>
          <text v-for="(ln, i) in lines(n)" :key="i" :x="n.x + n.w / 2" :y="lineY(n, i)" text-anchor="middle"
                :font-size="i ? 11.5 : 13" :font-weight="i ? 400 : 600" :class="i ? 'sub' : ''">{{ ln }}</text>
          <g v-if="tagOf(n)" class="flw-tag" :class="'t-' + tagTone(n)">
            <rect :x="n.x + n.w / 2 - tagW(tagOf(n)) / 2" :y="n.y - 13" :width="tagW(tagOf(n))" height="20" rx="10"/>
            <text :x="n.x + n.w / 2" :y="n.y + 1" text-anchor="middle" font-size="11.5">{{ tagOf(n) }}</text>
          </g>
        </g>
        <g v-for="p in packets" :key="step + '-' + p.id" v-show="pk[p.id]" class="flw-pk"
           :transform="pk[p.id] ? 'translate(' + pk[p.id][0] + ',' + pk[p.id][1] + ')' : ''" :opacity="pk[p.id] ? pk[p.id][2] : 0">
          <rect :x="-p.w / 2" y="-10" :width="p.w" height="20" rx="10"/>
          <text v-if="p.text" y="4" text-anchor="middle" font-size="11">{{ p.text }}</text>
        </g>
      </svg>
    </div>

    <div class="vdb-panel">
      <template v-if="!cur">
        <h4>{{ scenario.name }}</h4>
        <p v-html="scenario.intro"></p>
        <p class="vdb-mut vdb-small">Bấm <b>▶ Tự chạy</b> hoặc từng bước để xem dữ liệu đi qua sơ đồ.</p>
      </template>
      <template v-else>
        <h4>Bước {{ step }} – {{ cur.t }}</h4>
        <p v-if="cur.x" v-html="cur.x"></p>
        <pre v-if="cur.code" class="flw-code"><code>{{ cur.code }}</code></pre>
      </template>
    </div>
    <figcaption v-if="caption">{{ caption }}</figcaption>
  </figure>`,
};
