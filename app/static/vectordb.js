/* Mô hình động Vector Database (khối {"t": "widget", "name": "vectordb"} trong bài học).
   Sáu bước: cắt tài liệu thành đoạn và đổi thành vector → đoạn cùng nghĩa nằm gần nhau → câu hỏi thành vector →
   đo độ gần (cosine) → lấy Top-K, lọc ngưỡng → ghép vào prompt. Vector rút gọn 6 chiều có tên để dễ nhìn;
   bản đồ 2D là hình chiếu của vector đó, điểm số tính trên đủ 6 chiều. Dữ liệu là tài liệu giả lập Nhà Xanh. */
const VDB_DIMS = ['Giao hàng', 'Tiền', 'Đổi trả', 'Bảo hành', 'Giá & KM', 'Nhân sự'];

// tâm mỗi chiều nghĩa trên bản đồ (khung 820 × 430, cột trái 0–110 là tài liệu và câu hỏi)
const VDB_ANCHORS = [[260, 110], [530, 105], [705, 220], [420, 320], [690, 350], [225, 345]];

const VDB_CHUNKS = [
  { muc: 'Giao hàng', text: 'Nội thành giao 1–2 ngày; ngoại thành và tỉnh khác 3–5 ngày.', v: [.95, .05, .1, .05, 0, 0], j: [-48, -6] },
  { muc: 'Giao hàng', text: 'Miễn phí giao hàng cho đơn từ 500.000 đồng.', v: [.75, .45, .05, 0, .3, 0], j: [30, 18] },
  { muc: 'Giao hàng', text: 'Khách tra trạng thái đơn trên website bằng mã đơn hàng và số điện thoại.', v: [.8, .1, .25, .15, 0, 0], j: [-6, 44] },
  { muc: 'Hoàn tiền', text: 'Hàng trả hợp lệ được hoàn tiền trong 5 ngày làm việc kể từ khi kho nhận lại hàng.', v: [.1, .85, .45, 0, 0, 0], j: [10, 30] },
  { muc: 'Hoàn tiền', text: 'Hoàn theo đúng hình thức khách đã thanh toán: thẻ, ví điện tử, chuyển khoản.', v: [.05, .95, .15, 0, .1, 0], j: [52, -14] },
  { muc: 'Hoàn tiền', text: 'Đơn trả tiền mặt khi nhận hàng (COD) được hoàn qua chuyển khoản vào tài khoản khách cung cấp.', v: [.3, .85, .2, 0, 0, 0], j: [-40, -4] },
  { muc: 'Đổi trả', text: 'Đổi hoặc trả hàng trong 7 ngày kể từ ngày nhận nếu sản phẩm lỗi, giao sai mẫu, sai màu.', v: [.3, .1, .95, .2, 0, 0], j: [-40, 10] },
  { muc: 'Đổi trả', text: 'Khách đổi ý: sản phẩm còn nguyên tem, hộp, chưa sử dụng; khách chịu phí vận chuyển hai chiều.', v: [.25, .3, .9, 0, 0, 0], j: [8, -46] },
  { muc: 'Đổi trả', text: 'Không nhận đổi ý với hàng xả kho và hàng đặt theo yêu cầu riêng.', v: [0, .1, .9, .05, .3, 0], j: [36, 18] },
  { muc: 'Bảo hành', text: 'Đồ gia dụng nhỏ (nồi chiên, máy xay, ấm siêu tốc) bảo hành 12 tháng; điện lạnh 24 tháng.', v: [0, .05, .15, .95, .1, 0], j: [44, 6] },
  { muc: 'Bảo hành', text: 'Không bảo hành hư hỏng do rơi vỡ, vào nước hoặc tự ý tháo sửa.', v: [0, 0, .25, .9, 0, 0], j: [-10, 42] },
  { muc: 'Bảo hành', text: 'Hàng điện lạnh, sản phẩm nặng trên 20 kg được bảo hành tại nhà; kỹ thuật viên hẹn lịch trong 2 ngày.', v: [.35, 0, .1, .85, 0, 0], j: [-34, -18] },
  { muc: 'Ngoài phạm vi', text: 'Giá bán, khuyến mãi: hướng dẫn khách xem trên website hoặc hỏi nhân viên bán hàng.', v: [0, .3, 0, 0, .9, 0], j: [-22, -12] },
];

// kw: cụm từ khóa của câu hỏi, dùng khi chuyển sang tìm theo từ khóa (khớp đúng cụm chữ)
const VDB_QUESTIONS = [
  { q: 'Sao hàng mãi chưa giao?', v: [.9, .05, .15, .05, 0, 0], kw: ['giao'],
    note: 'Đoạn #3 không có chữ “giao” nhưng vẫn được tìm thấy vì cùng nghĩa (theo dõi đơn).' },
  { q: 'Trả hàng thì bao lâu lấy lại tiền?', v: [.05, .85, .5, 0, 0, 0], kw: ['trả hàng', 'lấy lại tiền'],
    note: 'Tài liệu ghi “hoàn tiền”, câu hỏi ghi “lấy lại tiền”: khác chữ nhưng vector vẫn gần nhau.' },
  { q: 'Nồi chiên hỏng sau 3 tháng có được sửa miễn phí?', v: [.05, .1, .2, .95, .1, 0], kw: ['nồi chiên', 'sửa miễn phí'],
    note: 'Câu hỏi rơi vào vùng Bảo hành; ba đoạn gần nhất đều là quy định bảo hành.' },
  { q: 'Mua nhầm màu, đổi được không?', v: [.15, .15, .95, .05, 0, 0], kw: ['nhầm màu', 'đổi'],
    note: 'Câu hỏi rơi giữa cụm Đổi trả.' },
  { q: 'Nhân viên được nghỉ phép mấy ngày?', v: [0, .05, .05, 0, 0, .99], kw: ['nghỉ phép'],
    note: 'Kho chỉ có chính sách đổi trả: câu hỏi rơi vào vùng trống, không đoạn nào đủ gần. Agent phải nói “không có thông tin”, không được đoán.' },
];

const VDB_STEPS = [
  ['Nạp tài liệu', 'Cắt đoạn, đổi thành vector'],
  ['Gom nghĩa', 'Đoạn cùng nghĩa nằm gần nhau'],
  ['Câu hỏi', 'Đổi câu hỏi thành vector'],
  ['Đo độ gần', 'Cosine với từng đoạn'],
  ['Top-K & ngưỡng', 'Giữ đoạn gần nhất'],
  ['Ghép prompt', 'Gửi đoạn đã chọn cho LLM'],
];

function vdbCos(a, b) {
  let d = 0, na = 0, nb = 0;
  for (let i = 0; i < a.length; i++) { d += a[i] * b[i]; na += a[i] * a[i]; nb += b[i] * b[i]; }
  return na && nb ? d / Math.sqrt(na * nb) : 0;
}

// hình chiếu 2D: trung bình các tâm theo trọng số mũ 3 (chiều nổi trội kéo điểm về cụm của nó)
function vdbProject(v, j) {
  let x = 0, y = 0, s = 0;
  v.forEach((w, i) => { const k = w ** 3; x += k * VDB_ANCHORS[i][0]; y += k * VDB_ANCHORS[i][1]; s += k; });
  return [Math.round(x / s + (j ? j[0] : 0)), Math.round(y / s + (j ? j[1] : 0))];
}

function vdbNum(x) { return x.toFixed(2).replace('.', ','); }

const VectorDbDemo = {
  name: 'VectorDbDemo',
  props: { caption: String },
  data() {
    return { step: 0, qi: 0, mode: 'vector', k: 3, th: 0.5, sel: null, timer: null, docPos: [58, 108], askPos: [58, 318] };
  },
  computed: {
    steps() { return VDB_STEPS; },
    dims() { return VDB_DIMS; },
    questions() { return VDB_QUESTIONS; },
    cur() { return VDB_QUESTIONS[this.qi]; },
    qPos() { return vdbProject(this.cur.v); },
    anchors() {
      return VDB_DIMS.map((name, i) => ({ name, x: VDB_ANCHORS[i][0], y: VDB_ANCHORS[i][1], empty: name === 'Nhân sự' }));
    },
    chunks() {
      return VDB_CHUNKS.map((c, i) => {
        const [x, y] = vdbProject(c.v, c.j);
        const low = c.text.toLowerCase();
        const hits = this.cur.kw.filter(w => low.includes(w));
        return { ...c, no: i + 1, x, y, score: vdbCos(this.cur.v, c.v), hits };
      });
    },
    // xếp hạng theo cách tìm đang chọn; từ khóa: chỉ đoạn có chứa cụm từ, nhiều cụm khớp đứng trước
    ranked() {
      if (this.mode === 'vector') return [...this.chunks].sort((a, b) => b.score - a.score);
      return this.chunks.filter(c => c.hits.length).sort((a, b) => b.hits.length - a.hits.length || a.no - b.no);
    },
    topK() { return this.ranked.slice(0, this.k); },
    kept() { return this.mode === 'vector' ? this.topK.filter(c => c.score >= this.th) : this.topK; },
    keptNos() { return new Set(this.kept.map(c => c.no)); },
    topNos() { return new Set(this.topK.map(c => c.no)); },
    selChunk() { return this.sel ? this.chunks[this.sel - 1] : null; },
    prompt() {
      const docs = this.kept.map(c => `[Đoạn #${c.no} – mục ${c.muc}] ${c.text}`).join('\n');
      return 'Chỉ trả lời dựa trên tài liệu dưới đây. Nếu tài liệu không có thông tin, nói rõ là không có.\n' +
        `<tai_lieu>\n${docs || '(không có đoạn nào vượt ngưỡng)'}\n</tai_lieu>\n` +
        `Câu hỏi: ${this.cur.q}`;
    },
    lineKey() { return `${this.qi}-${this.mode}`; },
  },
  methods: {
    num: vdbNum,
    go(s) { this.stop(); this.step = Math.max(0, Math.min(VDB_STEPS.length, s)); },
    play() {
      if (this.timer) return this.stop();
      if (this.step >= VDB_STEPS.length) this.step = 0;
      const tick = () => {
        this.step += 1;
        if (this.step >= VDB_STEPS.length) this.stop();
      };
      tick();
      this.timer = setInterval(tick, 3600);
    },
    stop() { if (this.timer) { clearInterval(this.timer); this.timer = null; } },
    ask(i) { this.qi = i; if (this.step < 3) this.go(3); },
    pick(no) { this.sel = this.sel === no ? null : no; },
    // trạng thái của một điểm theo bước hiện tại
    dotCls(c) {
      if (this.step >= 5) return this.keptNos.has(c.no) ? 'kept' : this.topNos.has(c.no) ? 'cut' : 'dim';
      if (this.step === 4 && this.mode === 'keyword') return c.hits.length ? 'hit' : 'dim';
      return '';
    },
    dotStyle(c, i) {
      const on = this.step >= 1;
      const [x, y] = on ? [c.x, c.y] : this.docPos;
      return { transform: `translate(${x}px, ${y}px)`, opacity: on ? 1 : 0, transitionDelay: on ? `${i * 110}ms` : '0ms' };
    },
    lineOn(c) {
      if (this.step < 4) return false;
      if (this.mode === 'keyword') return c.hits.length > 0 && (this.step === 4 || this.topNos.has(c.no));
      return this.step === 4 || this.topNos.has(c.no);
    },
    lineOpacity(c) { return this.mode === 'keyword' ? 0.9 : Math.max(0.12, c.score ** 2); },
    showScore(c) {
      if (this.step === 4) return this.mode === 'vector' || c.hits.length > 0;
      return this.step >= 5 && this.topNos.has(c.no);
    },
    scoreText(c) { return this.mode === 'vector' ? this.num(c.score) : `khớp ${c.hits.length}`; },
    bar(v) { return { height: `${Math.round(v * 100)}%` }; },
  },
  beforeUnmount() { this.stop(); },
  template: `
  <figure class="vdb" aria-label="Mô hình động: Vector Database tìm đoạn văn theo nghĩa">
    <div class="vdb-steps" role="tablist">
      <button type="button" class="vdb-step" :class="{ on: step === 0 }" @click="go(0)"><b>0</b><span>Kho trống</span></button>
      <button v-for="(s, i) in steps" :key="i" type="button" class="vdb-step" :class="{ on: step === i + 1, done: step > i + 1 }" @click="go(i + 1)">
        <b>{{ i + 1 }}</b><span>{{ s[0] }}</span>
      </button>
      <span class="vdb-nav">
        <button type="button" class="btn" :disabled="step === 0" @click="go(step - 1)" aria-label="Bước trước">←</button>
        <button type="button" class="btn primary" @click="play">{{ timer ? '⏸ Dừng' : step >= steps.length ? '↺ Chạy lại' : '▶ Tự chạy' }}</button>
        <button type="button" class="btn" :disabled="step >= steps.length" @click="go(step + 1)" aria-label="Bước sau">→</button>
      </span>
    </div>

    <div class="vdb-ask" v-if="step >= 3">
      <span class="vdb-label">Câu hỏi:</span>
      <button v-for="(q, i) in questions" :key="i" type="button" class="vdb-chip" :class="{ on: qi === i }" @click="ask(i)">{{ q.q }}</button>
    </div>
    <div class="vdb-ask" v-if="step >= 4">
      <span class="vdb-label">Cách tìm:</span>
      <span class="seg">
        <button type="button" :class="{ on: mode === 'vector' }" @click="mode = 'vector'">Theo nghĩa (vector)</button>
        <button type="button" :class="{ on: mode === 'keyword' }" @click="mode = 'keyword'">Theo từ khóa</button>
      </span>
      <template v-if="step >= 5">
        <label class="vdb-range">Top-K = <b>{{ k }}</b><input type="range" min="1" max="5" step="1" v-model.number="k"></label>
        <label class="vdb-range" :class="{ off: mode === 'keyword' }">Ngưỡng = <b>{{ num(th) }}</b>
          <input type="range" min="0.3" max="0.95" step="0.05" v-model.number="th" :disabled="mode === 'keyword'"></label>
      </template>
    </div>

    <div class="vdb-stage">
      <svg viewBox="0 0 820 430" class="vdb-svg" role="img" aria-label="Bản đồ nghĩa: mỗi chấm là một đoạn tài liệu, ngôi sao là câu hỏi">
        <rect x="120" y="6" width="694" height="418" rx="12" class="vdb-map"/>
        <g class="vdb-grid">
          <line v-for="x in [235, 350, 465, 580, 695]" :key="'x' + x" :x1="x" y1="6" :x2="x" y2="424"/>
          <line v-for="y in [90, 174, 258, 342]" :key="'y' + y" x1="120" :y1="y" x2="814" :y2="y"/>
        </g>
        <text x="806" y="24" class="vdb-mut" font-size="11" text-anchor="end">Bản đồ 2D thu gọn từ vector 6 chiều</text>

        <g class="vdb-fade" :style="{ opacity: step >= 2 ? 1 : 0 }">
          <g v-for="a in anchors" :key="a.name">
            <ellipse :cx="a.x" :cy="a.y" rx="88" ry="62" class="vdb-halo" :class="{ empty: a.empty }"/>
            <text :x="a.x" :y="a.y - 66" font-size="13" text-anchor="middle" class="vdb-topic" :class="{ 'vdb-mut': a.empty }">{{ a.name }}{{ a.empty ? ' (chưa có tài liệu)' : '' }}</text>
          </g>
        </g>

        <g class="vdb-col">
          <rect x="10" y="50" width="96" height="118" rx="8" class="vdb-doc"/>
          <path d="M84,50 v18 h22" class="vdb-fold"/>
          <line v-for="y in [92, 104, 116, 128, 140]" :key="y" x1="22" :y1="y" x2="94" :y2="y" class="vdb-docline"/>
          <text x="58" y="40" font-size="12.5" text-anchor="middle" font-weight="600">Tài liệu</text>
          <text x="58" y="160" font-size="10.5" text-anchor="middle" class="vdb-mut">13 đoạn</text>
          <text x="58" y="198" font-size="11" text-anchor="middle" class="vdb-mut">embedding</text>
          <text x="58" y="212" font-size="11" text-anchor="middle" class="vdb-mut">chữ → vector</text>
          <rect x="10" y="262" width="96" height="112" rx="8" class="vdb-doc" :class="{ live: step >= 3 }"/>
          <text x="58" y="252" font-size="12.5" text-anchor="middle" font-weight="600">Câu hỏi</text>
          <text x="58" y="364" font-size="10.5" text-anchor="middle" class="vdb-mut">{{ step >= 3 ? 'cùng mô hình' : 'chưa hỏi' }}</text>
        </g>

        <g :key="'l' + lineKey">
          <line v-for="c in chunks" :key="c.no" v-show="lineOn(c)" :x1="qPos[0]" :y1="qPos[1]" :x2="c.x" :y2="c.y"
                pathLength="1" class="vdb-ray" :class="{ hot: step >= 5 && keptNos.has(c.no), cut: step >= 5 && !keptNos.has(c.no) }"
                :style="{ strokeOpacity: step >= 5 ? 1 : lineOpacity(c) }"/>
        </g>

        <g :key="'r' + lineKey" v-if="step === 4" :transform="'translate(' + qPos[0] + ',' + qPos[1] + ')'">
          <circle r="40" class="vdb-ripple"/>
          <circle r="40" class="vdb-ripple two"/>
        </g>

        <g v-for="(c, i) in chunks" :key="c.no" class="vdb-dot" :class="[dotCls(c), { sel: sel === c.no }]" :style="dotStyle(c, i)"
           @click="pick(c.no)" tabindex="0" @keydown.enter="pick(c.no)" role="button" :aria-label="'Đoạn ' + c.no + ': ' + c.text">
          <circle r="13" class="vdb-hit"/>
          <circle r="10"/>
          <text y="4" font-size="10.5" text-anchor="middle">{{ c.no }}</text>
          <text v-if="showScore(c)" x="15" y="-9" font-size="11" class="vdb-score">{{ scoreText(c) }}</text>
          <text v-if="step >= 5 && topNos.has(c.no)" x="-15" y="-9" font-size="11" text-anchor="end" class="vdb-rank">#{{ ranked.indexOf(c) + 1 }}</text>
        </g>

        <g class="vdb-q" :style="{ transform: 'translate(' + (step >= 3 ? qPos[0] : askPos[0]) + 'px,' + (step >= 3 ? qPos[1] : askPos[1]) + 'px)', opacity: step >= 3 ? 1 : 0.25 }">
          <polygon points="0,-15 4.4,-4.6 15,-4.6 6.4,2.4 9.3,13 0,6.6 -9.3,13 -6.4,2.4 -15,-4.6 -4.4,-4.6" class="vdb-star"/>
        </g>
      </svg>
    </div>

    <div class="vdb-sel" v-if="selChunk">
      <b>Đoạn #{{ selChunk.no }} – {{ selChunk.muc }}:</b> {{ selChunk.text }}
      <span class="vdb-vec">vector [{{ selChunk.v.map(num).join(' · ') }}]</span>
      <span v-if="step >= 4"> · độ gần với câu hỏi: <b>{{ num(selChunk.score) }}</b></span>
      <button type="button" class="vdb-x" @click="sel = null" aria-label="Đóng">×</button>
    </div>

    <div class="vdb-panel">
      <template v-if="step === 0">
        <h4>Kho tài liệu đang trống</h4>
        <p>Bên trái là tài liệu <em>chinh_sach_doi_tra_gia_lap.md</em> của Nhà Xanh. Bên phải là “bản đồ nghĩa” của Vector Database,
          nơi mỗi đoạn văn sẽ thành một chấm. Bấm <b>▶ Tự chạy</b> hoặc từng bước 1 → 6 để xem một câu hỏi được trả lời ra sao.</p>
      </template>

      <template v-else-if="step === 1">
        <h4>Bước 1 – Cắt tài liệu thành 13 đoạn, mỗi đoạn đổi thành một vector</h4>
        <p>Mô hình embedding chấm điểm mỗi đoạn theo các “chiều nghĩa”. Ở đây rút gọn còn 6 chiều có tên
          ({{ dims.join(', ') }}); mô hình thật dùng hàng trăm đến hàng nghìn chiều không tên. Vector Database lưu <b>đoạn chữ + vector</b>.</p>
        <div class="vdb-cards">
          <div v-for="c in chunks" :key="c.no" class="vdb-card" :class="{ sel: sel === c.no }" @click="pick(c.no)">
            <span class="vdb-bars" :title="c.v.map((v, i) => dims[i] + ': ' + num(v)).join(' · ')"><i v-for="(v, i) in c.v" :key="i" :style="bar(v)"></i></span>
            <span><b>#{{ c.no }}</b> {{ c.text }}</span>
          </div>
        </div>
        <p class="vdb-mut vdb-small">Cột nhỏ bên trái mỗi đoạn = 6 con số của vector, theo thứ tự {{ dims.join(' · ') }}.</p>
      </template>

      <template v-else-if="step === 2">
        <h4>Bước 2 – Đoạn cùng nghĩa tự nằm gần nhau</h4>
        <p>Không ai xếp tay: vì vector giống nhau nên các đoạn về giao hàng gom một chỗ, về hoàn tiền gom một chỗ.
          Đoạn mang hai ý (VD #2 “miễn phí giao hàng” vừa về giao hàng vừa về tiền) nằm lệch về phía cụm còn lại.
          Vùng <b>Nhân sự</b> trống vì kho này không có tài liệu nhân sự.</p>
        <p class="vdb-mut vdb-small">Bấm vào một chấm để xem đoạn văn và vector của nó.</p>
      </template>

      <template v-else-if="step === 3">
        <h4>Bước 3 – Câu hỏi cũng được đổi thành vector, bằng <u>cùng</u> mô hình embedding</h4>
        <p>“{{ cur.q }}” → vector
          <span class="vdb-bars big"><i v-for="(v, i) in cur.v" :key="i" :style="bar(v)" :title="dims[i] + ': ' + num(v)"></i></span>
          [{{ cur.v.map(num).join(' · ') }}]. Ngôi sao rơi vào vùng có nghĩa gần nhất.</p>
        <p class="vdb-mut vdb-small">Đổi câu hỏi ở hàng nút phía trên để xem ngôi sao di chuyển.</p>
      </template>

      <template v-else-if="step === 4">
        <h4 v-if="mode === 'vector'">Bước 4 – Đo độ gần (cosine) giữa câu hỏi và từng đoạn</h4>
        <h4 v-else>Bước 4 – Tìm theo từ khóa: chỉ lấy đoạn có đúng cụm chữ {{ cur.kw.map(w => '“' + w + '”').join(', ') }}</h4>
        <p v-if="mode === 'vector'">Đường càng đậm, đoạn càng gần nghĩa. Điểm gần 1 là rất giống, gần 0 là không liên quan.
          Kho lớn hàng triệu đoạn thì dùng chỉ mục ANN (HNSW) để chỉ đo các vùng gần, không đo hết.</p>
        <p v-else-if="ranked.length">Có {{ ranked.length }} đoạn chứa từ khóa. Bật lại “Theo nghĩa” để so sánh đoạn nào bị bỏ sót, đoạn nào bị bắt nhầm.</p>
        <p v-else>Không đoạn nào chứa đúng cụm chữ này: tìm theo từ khóa trả về rỗng.</p>
        <div class="vdb-list">
          <div v-for="c in (mode === 'vector' ? ranked : chunks)" :key="c.no" class="vdb-row" :class="{ dim: mode === 'keyword' && !c.hits.length }">
            <span class="vdb-no">#{{ c.no }}</span>
            <span class="vdb-meter" v-if="mode === 'vector'"><i :style="{ width: Math.round(c.score * 100) + '%' }"></i></span>
            <b class="vdb-val">{{ mode === 'vector' ? num(c.score) : (c.hits.length ? 'khớp: ' + c.hits.join(', ') : '—') }}</b>
            <span class="vdb-txt">{{ c.text }}</span>
          </div>
        </div>
      </template>

      <template v-else-if="step === 5">
        <h4>Bước 5 – Lấy {{ k }} đoạn đứng đầu{{ mode === 'vector' ? ', bỏ đoạn dưới ngưỡng ' + num(th) : '' }}</h4>
        <div class="tablewrap"><table>
          <thead><tr><th>Hạng</th><th>Đoạn</th><th>{{ mode === 'vector' ? 'Điểm' : 'Khớp' }}</th><th>Kết quả</th></tr></thead>
          <tbody>
            <tr v-for="(c, i) in topK" :key="c.no">
              <td>#{{ i + 1 }}</td><td><b>#{{ c.no }}</b> {{ c.text }}</td>
              <td>{{ mode === 'vector' ? num(c.score) : c.hits.join(', ') }}</td>
              <td :class="keptNos.has(c.no) ? 'vdb-ok' : 'vdb-bad'">{{ keptNos.has(c.no) ? '✓ Giữ' : '✗ Dưới ngưỡng' }}</td>
            </tr>
            <tr v-if="!topK.length"><td colspan="4">Không có đoạn nào.</td></tr>
          </tbody>
        </table></div>
        <p class="vdb-small">{{ cur.note }}</p>
        <p class="vdb-mut vdb-small">Kéo Top-K, Ngưỡng ở trên: K quá nhỏ dễ thiếu ý, K quá lớn kéo theo đoạn nhiễu; ngưỡng quá cao dễ “không tìm thấy”.</p>
      </template>

      <template v-else>
        <h4>Bước 6 – Ghép đoạn đã chọn vào prompt gửi LLM</h4>
        <pre class="flw-code"><code>{{ prompt }}</code></pre>
        <p class="vdb-small" v-if="kept.length">LLM chỉ đọc {{ kept.length }} đoạn này chứ không đọc cả kho. Bốc nhầm đoạn → lỗi truy xuất;
          bốc đúng mà vẫn trả lời sai → lỗi sinh.</p>
        <p class="vdb-small" v-else>Không đoạn nào được gửi: Agent đúng ra phải trả lời “tài liệu không có thông tin này”.</p>
      </template>
    </div>
    <figcaption v-if="caption">{{ caption }}</figcaption>
  </figure>`,
};
