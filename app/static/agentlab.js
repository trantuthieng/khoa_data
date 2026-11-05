/* Lab mini của Buổi 3–5 khóa AI Agent (khối {"t": "widget", "name": "agentlab", "spec": ...}); nội dung chữ sinh từ tools/ai_agent_labs.py.
   Dùng lại DlParam và kiểu dáng .dl-* của difylab.js nên phải nạp sau difylab.js.

   Chạy thật trên trình duyệt: regex phân loại, kiểm tra tham số, công thức điểm xét tuyển, các quy tắc cứng của rubric, xử lý CSV, lọc dữ liệu cá nhân,
   gom nhóm log, tính KPI, và lời gọi HTTP tới API giả lập /api/mock-ts.
   Soạn sẵn hoặc minh họa: quyết định của LLM (phân loại, trích xuất, gọi công cụ, câu trả lời), xác suất bị Prompt Injection, kết quả các phiên bản trong bộ Eval.
   Mỗi lab ghi rõ điều này trên giao diện. */

const alNum = (x, n = 2) => Number(x).toFixed(n).replace('.', ',');
const alRound = x => Math.round(x * 100 + 1e-9) / 100;
const alTok = s => Math.ceil(String(s).length / 3.6);

// khung chung: nhiệm vụ tự đánh dấu khi trạng thái của lab khớp điều kiện when
const AlBase = {
  components: { DlParam },
  props: { spec: Object },
  data() { return { done: {} }; },
  computed: {
    docs() { return this.spec.docs || {}; },
    missions() { return (this.spec.missions || []).map((m, i) => ({ ...m, i, ok: !!this.done[i] })); },
    doneCount() { return this.missions.filter(m => m.ok).length; },
  },
  watch: {
    view: {
      deep: true, immediate: true,
      handler(v) {
        if (!v) return;
        (this.spec.missions || []).forEach((m, i) => { if (!this.done[i] && this.matches(v, m.when)) this.done[i] = true; });
      },
    },
  },
  methods: {
    num: alNum,
    setPath(o, p, v) { const ks = p.split('.'); let c = o; for (const k of ks.slice(0, -1)) c = c[k]; c[ks[ks.length - 1]] = v; },
    getPath(o, p) { return p.split('.').reduce((c, k) => (c == null ? c : c[k]), o); },
    matches(v, when) {
      return Object.entries(when || {}).every(([p, want]) => {
        const got = this.getPath(v, p);
        if (want && typeof want === 'object' && !Array.isArray(want)) {
          if ('lt' in want && !(got < want.lt)) return false;
          if ('gt' in want && !(got > want.gt)) return false;
          if ('in' in want && !want.in.includes(got)) return false;
          return true;
        }
        return got === want;
      });
    },
  },
};
const AL_MISSIONS = `
  <div v-if="missions.length" class="dl-missions">
    <div class="dl-mhead">🔬 Nhiệm vụ <span>{{ doneCount }}/{{ missions.length }}</span></div>
    <div v-for="m in missions" :key="m.i" class="dl-mission" :class="{ ok: m.ok }">
      <span class="dl-check" aria-hidden="true">{{ m.ok ? '✓' : '○' }}</span>
      <div><span v-html="m.t"></span><p v-if="m.ok" class="dl-why" v-html="m.why"></p></div>
    </div>
  </div>`;
const AL_HEAD = `<div class="dl-sidehead"><span>⚙ Bảng tham số</span><button type="button" class="btn sm ghost" @click="reset">↺ Về cấu hình bài</button></div>`;

/* ---- Phân loại: Question Classifier (Buổi 3), Router (Buổi 5) ---- */
const AlClassify = {
  name: 'AlClassify', mixins: [AlBase],
  data() { return { st: this.initial(), open: 0 }; },
  computed: {
    rows() {
      const s = this.spec, re = s.rule && this.st.t[s.rule.k] ? new RegExp(s.rule.re, 'iu') : null;
      return s.msgs.map(m => {
        let pred = m.p.base, by = 'LLM';
        for (const tg of s.toggles) {
          const key = this.st.t[tg.k] ? tg.k : '!' + tg.k;
          if (key in m.p) pred = m.p[key];
        }
        if (re && re.test(m.t)) { pred = s.rule.cls; by = 'quy tắc'; }
        return { ...m, pred, by, ok: pred === m.truth };
      });
    },
    wrong() { return this.rows.filter(r => !r.ok); },
    view() {
      const crit = this.rows.filter(r => r.critical && !r.ok).length;
      return { t: this.st.t, out: { acc: this.rows.filter(r => r.ok).length, total: this.rows.length, crit, wrong: this.wrong.map(r => r.id) } };
    },
    cur() { return this.rows[this.open] || this.rows[0]; },
  },
  methods: {
    initial() { const t = {}; for (const g of this.spec.toggles) t[g.k] = !!g.on; return { t }; },
    reset() { this.st = this.initial(); },
    label(id) { const c = this.spec.classes.find(x => x.id === id); return c ? c.lb : id; },
  },
  template: `
  <div class="dl-core">
    <div class="dl-grid">
      <div class="dl-side">${AL_HEAD}
        <h5>{{ spec.node }}</h5>
        <dl-param v-for="d in spec.show" :key="d[0]" :k="d[0]" :label="d[1]" :docs="docs"><span class="dl-mut">{{ d[2] }}</span></dl-param>
        <h5>Lớp (mô tả là thứ LLM đọc để chọn)</h5>
        <div class="al-classes"><div v-for="c in spec.classes" :key="c.id"><b>{{ c.lb }}</b> <span class="dl-small dl-mut" v-html="c.desc"></span></div></div>
        <h5>Thử đổi</h5>
        <dl-param v-for="g in spec.toggles" :key="g.k" :k="g.doc" :label="g.lb" :docs="docs"><input type="checkbox" v-model="st.t[g.k]"></dl-param>
      </div>
      <div class="dl-main">
        <div class="dl-stats sm">
          <div :class="{ warn: wrong.length }"><b>{{ rows.length - wrong.length }}/{{ rows.length }}</b><span>đúng</span></div>
          <div :class="{ warn: view.out.crit }"><b>{{ view.out.crit }}</b><span>ca cần người bị bỏ sót</span></div>
        </div>
        <div class="tablewrap"><table class="dl-vars al-tbl"><thead><tr><th>Tin nhắn</th><th>Máy chọn</th><th>Đúng phải là</th></tr></thead><tbody>
          <tr v-for="(r, i) in rows" :key="r.id" :class="{ 'al-bad': !r.ok }" @click="open = i">
            <td>{{ r.t }}</td><td><b>{{ label(r.pred) }}</b><span v-if="r.by === 'quy tắc'" class="dl-tag">quy tắc</span></td><td>{{ r.ok ? '✓' : label(r.truth) }}</td>
          </tr></tbody></table></div>
        <h6 class="dl-h6">Đầu ra của khối cho dòng đang chọn</h6>
        <div class="dl-json"><div><b>class_name:</b> {{ (spec.classes.find(c => c.id === cur.pred) || {}).plain }}</div><div><b>class_label:</b> {{ label(cur.pred) }}</div></div>
        <p class="dl-small dl-mut">Quyết định của LLM ở đây soạn sẵn theo hành vi thường gặp, số câu đúng chỉ để so sánh giữa các cấu hình. Quy tắc từ khóa thì chạy thật. Đo thật bằng bộ đề của bạn trên Dify.</p>
      </div>
    </div>
    ${AL_MISSIONS}
  </div>`,
};

/* ---- Trích xuất và rẽ nhánh: Parameter Extractor + IF/ELIF/ELSE ---- */
const AlExtract = {
  name: 'AlExtract', mixins: [AlBase],
  data() { return { st: this.initial() }; },
  computed: {
    msg() { return this.spec.msgs.find(m => m.id === this.st.q); },
    vals() { const m = this.msg, o = {}; for (const p of this.spec.params) { o[p.k] = String(m.vals[p.k] ?? ''); if (!this.st.strict && m.guess && m.guess[p.k] !== undefined) o[p.k] = String(m.guess[p.k]); } return o; },
    guessed() { return !this.st.strict && !!this.msg.guess; },
    missing() { return this.spec.params.filter(p => this.st.req[p.k] && (this.vals[p.k] === '')); },
    conflict() { const c = this.msg.claim; return c && this.st.elif && this.vals[c.k] !== '' && String(this.vals[c.k]) !== String(c.doc) ? c : null; },
    branch() { return this.conflict ? 'if' : this.missing.length ? 'elif' : 'else'; },
    reply() {
      if (this.branch === 'elif') return 'Để trả lời chính xác, bạn cho mình biết thêm: ' + this.missing.map(p => p.lb).join(', ') + ' nhé.';
      if (this.branch === 'if') return this.conflict.reply;
      return this.guessed ? this.msg.badNext : this.msg.next;
    },
    json() { const du = Object.values(this.vals).every(v => v !== ''); return JSON.stringify({ ...this.vals, __is_success: du ? 1 : 0, __reason: du ? '' : 'Invalid number of parameters' }, null, 1); },
    view() { return { q: this.st.q, req: this.st.req, strict: this.st.strict, elif: this.st.elif, out: { branch: this.branch, missing: this.missing.length, guessed: this.guessed } }; },
  },
  methods: {
    initial() { const req = {}; for (const p of this.spec.params) req[p.k] = !!p.req; return { q: this.spec.msgs[0].id, req, strict: true, elif: true }; },
    reset() { this.st = this.initial(); },
    val(v) { return v === '' ? 'trống' : v; },
  },
  template: `
  <div class="dl-core">
    <div class="dl-grid">
      <div class="dl-side">${AL_HEAD}
        <h5>Parameter Extractor</h5>
        <dl-param k="peInput" label="Input Variable" :docs="docs"><code>sys.query</code></dl-param>
        <dl-param k="peStrict" label="Instruction: không nêu thì để trống" :docs="docs"><input type="checkbox" v-model="st.strict"></dl-param>
        <dl-param v-for="p in spec.params" :key="p.k" k="peRequired" :label="'IF kiểm tra ' + p.k + ' (' + p.type + ')'" :docs="docs"><input type="checkbox" v-model="st.req[p.k]"></dl-param>
        <h5>IF/ELIF/ELSE</h5>
        <dl-param k="ifelif" label="Có nhánh mâu thuẫn" :docs="docs"><input type="checkbox" v-model="st.elif"></dl-param>
      </div>
      <div class="dl-main">
        <div class="dl-ask"><span class="dl-label">Tin nhắn:</span>
          <button v-for="m in spec.msgs" :key="m.id" type="button" class="vdb-chip" :class="{ on: st.q === m.id }" @click="st.q = m.id">{{ m.lb }}</button></div>
        <p class="dl-qtext">“{{ msg.t }}”</p>
        <h6 class="dl-h6">Đầu ra của Parameter Extractor <span class="dl-tag">LLM, soạn sẵn</span></h6>
        <pre class="dl-rawbox al-json">{{ json }}</pre>
        <h6 class="dl-h6">Nhánh đi <span class="dl-tag">điều kiện chạy thật</span></h6>
        <div class="al-branches">
          <div :class="{ on: branch === 'if' }"><b>IF mâu thuẫn</b><span v-if="msg.claim">“{{ msg.claim.k }}” bạn nêu {{ val(vals[msg.claim.k]) }}, tài liệu ghi {{ msg.claim.doc }}</span><span v-else>không có số tự nêu</span></div>
          <div :class="{ on: branch === 'elif' }"><b>ELIF thiếu dữ liệu</b><span>{{ missing.length ? 'thiếu: ' + missing.map(p => p.k).join(', ') : 'đủ tham số cần kiểm tra' }}</span></div>
          <div :class="{ on: branch === 'else' }"><b>ELSE đủ dữ liệu</b><span>đi tiếp khối Code, tìm kho, LLM</span></div>
        </div>
        <div class="dl-chat"><div class="dl-bubble" :class="(guessed && branch === 'else') || (msg.claim && !st.elif) || (branch === 'else' && msg.partial) ? 't-bad' : 't-ok'">{{ reply }}</div></div>
      </div>
    </div>
    ${AL_MISSIONS}
  </div>`,
};

/* ---- Khối Code: công thức điểm xét tuyển, chạy thật ---- */
const AlCode = {
  name: 'AlCode', mixins: [AlBase],
  data() { return { st: this.initial() }; },
  computed: {
    combos() {
      return this.spec.combos.map(c => {
        const vals = c.mon.map(m => this.st.diem[m]);
        const du = vals.every(v => v !== '' && v !== null && !Number.isNaN(Number(v)));
        return { ...c, du, tong: du ? alRound(vals.reduce((a, v) => a + Number(v), 0)) : null };
      });
    },
    tong() { const t = this.combos.filter(c => c.du).map(c => c.tong); return t.length ? Math.max(...t) : null; },
    invalid() { return Object.values(this.st.diem).some(v => v !== '' && (Number(v) < 0 || Number(v) > 10)) || this.st.muc < 0 || this.tong === null; },
    ut() { if (this.invalid) return null; return this.tong >= 22.5 ? (30 - this.tong) / 7.5 * this.st.muc : this.st.muc; },
    dxt() { return this.invalid ? null : alRound(this.tong + this.ut); },
    utShow() { return this.invalid ? null : alRound(this.ut); },
    nham() { return this.invalid ? null : alRound(this.tong + Number(this.st.muc)); },
    view() {
      return { diem: this.st.diem, muc: this.st.muc, fail: this.st.fail, out: { dxt: this.dxt, ut: this.utShow, tong: this.tong, invalid: this.invalid, san: this.tong !== null && this.tong >= 15, hb: this.tong !== null && this.tong >= 25, lech: this.dxt !== null && this.nham !== this.dxt } };
    },
  },
  methods: {
    initial() { return { diem: { ...this.spec.init }, muc: this.spec.muc, fail: 'none' }; },
    reset() { this.st = this.initial(); },
  },
  template: `
  <div class="dl-core">
    <div class="dl-grid">
      <div class="dl-side">${AL_HEAD}
        <h5>Điểm từng môn (để ra tổng cao nhất)</h5>
        <div class="al-scores"><label v-for="m in spec.mon" :key="m[0]">{{ m[1] }}<input type="text" inputmode="decimal" v-model="st.diem[m[0]]" placeholder="không thi"></label></div>
        <h5>Input Variables</h5>
        <dl-param k="codeInput" label="tong_diem" :docs="docs"><code>{{ tong === null ? 'thiếu' : num(tong, 1) }}</code></dl-param>
        <dl-param k="codeInput" label="muc_uu_tien" :docs="docs"><input type="range" min="0" max="2.75" step=".25" v-model.number="st.muc"><output>{{ num(st.muc) }}</output></dl-param>
        <h5>Cấu hình khối</h5>
        <dl-param k="codeLang" label="Language" :docs="docs"><span class="dl-mut">Python 3</span></dl-param>
        <dl-param k="codeOut" label="Output Variables" :docs="docs"><span class="dl-mut">4 biến</span></dl-param>
        <dl-param k="codeErr" label="Error Handling" :docs="docs"><select v-model="st.fail"><option value="none">None</option><option value="branch">Fail Branch</option></select></dl-param>
      </div>
      <div class="dl-main">
        <div class="tablewrap"><table class="dl-vars"><thead><tr><th>Tổ hợp</th><th>Môn</th><th>Tổng</th></tr></thead><tbody>
          <tr v-for="c in combos" :key="c.id" :class="{ 'al-off': !c.du }"><td><b>{{ c.id }}</b></td><td>{{ c.ten }}</td><td>{{ c.du ? num(c.tong, 1) : 'thiếu môn, bỏ qua' }}</td></tr></tbody></table></div>
        <template v-if="!invalid">
          <div class="dl-stats sm">
            <div><b>{{ num(tong, 1) }}</b><span>tổng cao nhất</span></div>
            <div><b>{{ num(utShow) }}</b><span>điểm ưu tiên</span></div>
            <div><b>{{ num(dxt) }}</b><span>điểm xét tuyển</span></div>
          </div>
          <p class="dl-small"><b>Công thức đang áp dụng:</b> {{ tong >= 22.5 ? '(30 − ' + num(tong, 1) + ') ÷ 7,5 × ' + num(st.muc) + ' = ' + num(utShow) : 'tổng dưới 22,5 nên điểm ưu tiên bằng mức ưu tiên ' + num(st.muc) }}</p>
          <p class="dl-small" :class="view.out.lech ? 'n-warn' : ''" v-if="view.out.lech"><b>Nếu cộng thẳng mức ưu tiên:</b> {{ num(nham) }}, lệch {{ num(nham - dxt) }}. Đây là kiểu sai có thể xảy ra khi để LLM tự tính.</p>
          <div class="al-flags"><span :class="view.out.san ? 'ok' : 'bad'">{{ view.out.san ? '✓' : '✗' }} Ngưỡng 15,00</span><span :class="view.out.hb ? 'ok' : ''">{{ view.out.hb ? '✓ Đủ điểm xét học bổng 25, còn cần học lực giỏi' : '– Chưa đủ 25 điểm xét học bổng' }}</span></div>
        </template>
        <div v-else class="dl-chat"><div class="dl-bubble" :class="st.fail === 'branch' ? 't-warn' : 't-bad'">{{ st.fail === 'branch' ? 'Nhánh lỗi chạy: trợ lý hỏi lại “Bạn kiểm tra lại điểm các môn giúp mình nhé.”' : 'Khối báo lỗi và cả luồng dừng: người dùng thấy lỗi hệ thống.' }}</div></div>
        <details class="dl-pv"><summary>Mã Python dán vào khối Code</summary><pre>{{ spec.code }}</pre></details>
      </div>
    </div>
    ${AL_MISSIONS}
  </div>`,
};

/* ---- Rubric và vòng sửa: Evaluator (Buổi 3), Editor (Buổi 5). Quy tắc cứng chạy thật trên chữ, kể cả chữ người học tự sửa ---- */
function alCheck(rule, text, evidence) {
  const nums = s => (s.match(/\d+(?:[.,:/]\d+)*/g) || []).map(x => x.replace(/[.,]$/, ''));
  if (rule.kind === 'numbers') {
    const ok = new Set(nums(evidence)); const bad = [...new Set(nums(text))].filter(n => !ok.has(n));
    return { pass: !bad.length, why: bad.length ? 'số không có trong nguồn: ' + bad.join(', ') : '' };
  }
  if (rule.kind === 'must') {
    const miss = rule.all.filter(a => !new RegExp(a[0], 'iu').test(text)).map(a => a[1]);
    return { pass: !miss.length, why: miss.length ? 'thiếu: ' + miss.join(', ') : '' };
  }
  if (rule.kind === 'ban') {
    const hit = text.match(new RegExp(rule.re, 'iu'));
    return { pass: !hit, why: hit ? 'có “' + hit[0] + '”' : '' };
  }
  if (rule.kind === 'excl') {
    const n = (text.match(/!/g) || []).length;
    return { pass: n <= rule.max, why: n > rule.max ? n + ' dấu chấm than' : '' };
  }
  if (rule.kind === 'title') {
    const n = text.split('\n')[0].trim().split(/\s+/).filter(Boolean).length;
    return { pass: n <= rule.max, why: n > rule.max ? 'tiêu đề ' + n + ' tiếng' : '' };
  }
  if (rule.kind === 'words') {
    const n = text.trim().split(/\s+/).filter(Boolean).length;
    return { pass: n >= rule.min && n <= rule.max, why: n < rule.min || n > rule.max ? n + ' chữ' : '' };
  }
  return { pass: true, why: '' };
}
const AlReview = {
  name: 'AlReview', mixins: [AlBase],
  data() { return { st: this.initial() }; },
  computed: {
    rules() { return this.spec.rules.filter(r => this.st.on[r.id]); },
    source() { return this.st.genFix ? [this.spec.fixedDraft] : this.spec.drafts; },
    rounds() {
      const out = [], list = this.st.custom.trim() ? [this.st.custom] : this.source, max = this.st.custom.trim() ? 1 : this.st.loop;
      for (let i = 0; i < max && i < list.length; i += 1) {
        const text = list[i], checks = this.rules.map(r => ({ r, ...alCheck(r, text, this.spec.evidence) }));
        const fails = checks.filter(c => !c.pass);
        out.push({ i: i + 1, text, checks, fails, pass: !fails.length });
        if (!fails.length) break;
      }
      return out;
    },
    last() { return this.rounds[this.rounds.length - 1]; },
    tokens() { return this.rounds.reduce((a, r) => a + 2 * alTok(r.text) + 180, 0); },
    truthBad() { return this.spec.truth ? alCheck({ kind: 'numbers' }, this.last.text, this.spec.evidence).pass === false || new RegExp(this.spec.truth, 'iu').test(this.last.text) : false; },
    view() {
      return { on: this.st.on, loop: this.st.loop, genFix: this.st.genFix, out: { pass: this.last.pass, rounds: this.rounds.length, human: !this.last.pass, tokens: this.tokens, leak: this.last.pass && this.truthBad, custom: !!this.st.custom.trim(), customPass: !!this.st.custom.trim() && this.last.pass } };
    },
  },
  methods: {
    initial() { const on = {}; for (const r of this.spec.rules) on[r.id] = r.on !== false; return { on, loop: this.spec.loop || 3, genFix: false, custom: '' }; },
    reset() { this.st = this.initial(); },
  },
  template: `
  <div class="dl-core">
    <div class="dl-grid">
      <div class="dl-side">${AL_HEAD}
        <h5>{{ spec.node }}: checklist</h5>
        <div class="dl-rules"><label v-for="r in spec.rules" :key="r.id"><input type="checkbox" v-model="st.on[r.id]"> {{ r.lb }} <span class="dl-tag">{{ r.tag || 'quy tắc cứng' }}</span></label></div>
        <h5>Vòng sửa</h5>
        <dl-param k="loopMax" label="Maximum Loop Count" :docs="docs"><input type="range" min="1" max="5" v-model.number="st.loop"><output>{{ st.loop }}</output></dl-param>
        <dl-param k="genFix" :label="spec.genFixLb" :docs="docs"><input type="checkbox" v-model="st.genFix"></dl-param>
        <h5>Nguồn để đối chiếu</h5>
        <pre class="dl-rawbox al-src">{{ spec.evidence }}</pre>
      </div>
      <div class="dl-main">
        <div class="dl-stats sm">
          <div><b>{{ rounds.length }}</b><span>vòng đã chạy</span></div>
          <div><b>{{ tokens }}</b><span>token (ước lượng)</span></div>
          <div :class="{ warn: !last.pass }"><b>{{ last.pass ? 'ĐẠT' : 'CHUYỂN NGƯỜI' }}</b><span>kết quả</span></div>
        </div>
        <div v-for="r in rounds" :key="r.i" class="al-round" :class="r.pass ? 'ok' : 'bad'">
          <div class="dl-chead">Vòng {{ r.i }} · {{ r.pass ? 'DAT' : 'CHUA_DAT' }}</div>
          <pre>{{ r.text }}</pre>
          <ul class="dl-small dl-list"><li v-for="c in r.checks" :key="c.r.id"><b>{{ c.pass ? '✓' : '✗' }}</b> {{ c.r.lb }}<span v-if="c.why" class="n-bad"> ({{ c.why }})</span></li></ul>
        </div>
        <p v-if="view.out.leak" class="dl-small n-bad">Bài đã qua Evaluator nhưng vẫn chứa lỗi: tiêu chí kiểm tra lỗi này đang tắt.</p>
        <p v-if="!last.pass" class="dl-small n-warn">Hết số vòng mà chưa đạt: chuyển cho người, kèm bản cuối và danh sách lỗi.</p>
        <h6 class="dl-h6">Tự viết bản nháp để thử rubric (chấm thật)</h6>
        <textarea v-model="st.custom" class="al-area" rows="3" :placeholder="spec.customHint" aria-label="Bản nháp tự viết"></textarea>
        <p class="dl-small dl-mut">Các bản nháp có sẵn là soạn sẵn, không gọi mô hình. Ô chấm được đánh dấu “LLM” là mô phỏng bằng mẫu từ khóa; Evaluator thật hiểu nghĩa tốt hơn nhưng cũng có thể sai.</p>
      </div>
    </div>
    ${AL_MISSIONS}
  </div>`,
};

/* ---- Bộ nhớ: Conversation Variables + Variable Assigner ---- */
const AlMemory = {
  name: 'AlMemory', mixins: [AlBase],
  data() { return { st: this.initial() }; },
  computed: {
    run() {
      const vals = {}, log = [];
      for (const v of this.spec.vars) vals[v.k] = v.type === 'array' ? [] : '';
      if (this.st.session > 1 && this.st.db) for (const v of this.spec.vars) if (v.db) vals[v.k] = this.spec.dbVal[v.k];
      const turns = this.spec.turns.slice(0, this.st.step);
      const start = this.st.session > 1 ? this.spec.turns.length - 1 : 0;
      turns.forEach((t, i) => {
        if (this.st.session > 1 && i < start) return;
        for (const [k, val] of Object.entries(t.sets || {})) {
          if (!this.st.save[k]) continue;
          const op = this.st.op[k], cur = vals[k];
          if (op === 'clear') vals[k] = Array.isArray(cur) ? [] : '';
          else if (op === 'append') vals[k] = Array.isArray(cur) ? [...cur, val] : val;
          else vals[k] = Array.isArray(cur) ? [val] : val;
        }
        const need = t.needs || [], histOk = !t.hist || (this.st.win >= t.hist && this.st.session === 1);
        const has = need.every(k => (Array.isArray(vals[k]) ? vals[k].length >= ((t.needMin || {})[k] || 1) : vals[k]));
        const ok = has && histOk;
        log.push({ i, u: t.u, reply: ok ? t.ok : t.miss, ok, snap: JSON.parse(JSON.stringify(vals)) });
      });
      return { vals, log };
    },
    pii() { return this.spec.vars.filter(v => v.pii && this.st.save[v.k] && this.run.vals[v.k]).length; },
    view() {
      return { save: this.st.save, op: this.st.op, win: this.st.win, session: this.st.session, db: this.st.db, step: this.st.step, out: { pii: this.pii, miss: this.run.log.filter(l => !l.ok).length, count: this.run.log.length, full: this.st.step >= this.spec.turns.length,
        nganh: (this.run.vals.nganh_quan_tam || []).length } };
    },
  },
  methods: {
    initial() { const save = {}, op = {}; for (const v of this.spec.vars) { save[v.k] = v.save !== false; op[v.k] = v.op || 'overwrite'; } return { save, op, win: 10, session: 1, db: false, step: 1 }; },
    reset() { this.st = this.initial(); },
    next() { if (this.st.step < this.spec.turns.length) this.st.step += 1; },
    newSession() { this.st.session = 2; this.st.step = this.spec.turns.length; },
    show(v) { return Array.isArray(v) ? (v.length ? v.join(', ') : '(trống)') : (v || '(trống)'); },
  },
  template: `
  <div class="dl-core">
    <div class="dl-grid">
      <div class="dl-side">${AL_HEAD}
        <h5>Conversation Variables + Variable Assigner</h5>
        <div v-for="v in spec.vars" :key="v.k" class="al-var">
          <label><input type="checkbox" v-model="st.save[v.k]"> <code>{{ v.k }}</code> <span class="dl-mut">{{ v.type }}</span></label>
          <select v-model="st.op[v.k]" :aria-label="'Operation của ' + v.k"><option value="overwrite">Overwrite</option><option v-if="v.type === 'array'" value="append">Append</option><option value="clear">Clear</option></select>
        </div>
        <dl-param k="vaOp" label="Operation Mode" :docs="docs"><span class="dl-mut">chọn cho từng biến</span></dl-param>
        <h5>Memory của khối LLM</h5>
        <dl-param k="rwwin" label="Window Size" :docs="docs"><input type="range" min="0" max="10" v-model.number="st.win"><output>{{ st.win }}</output></dl-param>
        <h5>Qua phiên chat</h5>
        <dl-param k="vaDb" label="Lưu hồ sơ ra cơ sở dữ liệu ngoài" :docs="docs"><input type="checkbox" v-model="st.db"></dl-param>
      </div>
      <div class="dl-main">
        <div class="dl-runbar"><button type="button" class="btn sm primary" :disabled="st.step >= spec.turns.length" @click="next">▶ Lượt tiếp</button>
          <button type="button" class="btn sm" @click="newSession">🆕 Mở phiên chat mới</button><span class="dl-small dl-mut">Phiên {{ st.session }}, lượt {{ st.step }}/{{ spec.turns.length }}</span></div>
        <div class="dl-chat tall"><template v-for="l in run.log" :key="l.i"><div class="dl-bubble user">{{ l.u }}</div><div class="dl-bubble" :class="l.ok ? 't-ok' : 't-bad'">{{ l.reply }}</div></template></div>
        <h6 class="dl-h6">Giá trị biến lúc này</h6>
        <div class="tablewrap"><table class="dl-vars"><tbody><tr v-for="v in spec.vars" :key="v.k" :class="{ 'al-bad': v.pii && st.save[v.k] && run.vals[v.k] }"><td><code>{{ v.k }}</code></td><td>{{ show(run.vals[v.k]) }}</td></tr></tbody></table></div>
        <p v-if="pii" class="dl-small n-bad">Biến này đang giữ dữ liệu cá nhân. Không có lý do nghiệp vụ thì không lưu.</p>
        <p class="dl-small dl-mut">Biến và phép gán chạy thật. Câu trả lời soạn sẵn theo việc biến có giá trị hay không.</p>
      </div>
    </div>
    ${AL_MISSIONS}
  </div>`,
};

/* ---- Truy vết cả luồng: cài lỗi, chạy, chỉ ra chỗ sai đầu tiên. Dùng cho Chatflow, Agent và đội Agent ---- */
const AlTrace = {
  name: 'AlTrace', mixins: [AlBase],
  data() { return { st: this.initial(), pick: '', caught: {}, tick: 99 }; },
  created() { this.timers = []; },
  beforeUnmount() { this.timers.forEach(clearTimeout); },
  computed: {
    sc() { return this.spec.scenarios.find(s => s.id === this.st.sc); },
    fault() { return this.spec.faults.find(f => f.id === this.st.fault) || null; },
    patch() { return (this.fault && this.fault.on && this.fault.on[this.st.sc]) || null; },
    result() {
      const p = this.patch || {}, steps = [];
      let acts = 0, stopped = false;
      for (const s of this.sc.steps) {
        if ((p.skip || []).includes(s.n)) { steps.push({ ...s, skip: true }); continue; }
        if (this.spec.limit && s.loop) { acts += 1; if (acts > this.st.limit) { stopped = true; break; } }
        const e = (p.edit || {})[s.n];
        steps.push(e ? { ...s, ...e, edited: true } : s);
      }
      if (stopped) return { steps, final: this.spec.limit.final, tone: 'warn', stopped };
      return { steps, final: p.final || this.sc.final, tone: p.tone || this.sc.tone, stopped };
    },
    tokens() { return this.result.steps.filter(s => !s.skip).reduce((a, s) => a + (s.tok || 0), 0); },
    view() {
      const firstBad = this.patch && this.fault ? this.fault.node : '';
      return { sc: this.st.sc, fault: this.st.fault, limit: this.st.limit, out: { tone: this.result.tone, stopped: this.result.stopped, steps: this.result.steps.filter(s => !s.skip).length, caught: !!this.caught[this.st.fault + '/' + this.st.sc], affected: !!this.patch, firstBad, tokens: this.tokens } };
    },
  },
  watch: {
    'st.sc'() { this.pick = ''; }, 'st.fault'() { this.pick = ''; },
  },
  methods: {
    initial() { return { sc: this.spec.scenarios[0].id, fault: '', limit: this.spec.limit ? this.spec.limit.def : 0 }; },
    reset() { this.st = this.initial(); this.pick = ''; },
    run() {
      this.timers.forEach(clearTimeout); this.timers = []; this.tick = 0;
      const n = this.result.steps.length;
      const go = () => { this.tick += 1; if (this.tick < n) this.timers.push(setTimeout(go, 320)); };
      this.timers.push(setTimeout(go, 100));
    },
    pickNode(id) {
      this.pick = id;
      if (this.fault && this.patch && id === this.fault.node) this.caught = { ...this.caught, [this.st.fault + '/' + this.st.sc]: true };
    },
  },
  template: `
  <div class="dl-core">
    <div class="dl-grid">
      <div class="dl-side">${AL_HEAD}
        <h5>Câu chạy thử</h5>
        <div class="al-pick"><button v-for="s in spec.scenarios" :key="s.id" type="button" class="vdb-chip" :class="{ on: st.sc === s.id }" @click="st.sc = s.id">{{ s.lb }}</button></div>
        <h5>Cài một lỗi</h5>
        <select v-model="st.fault" aria-label="Chọn lỗi cần cài" class="al-sel"><option value="">Không cài lỗi</option><option v-for="f in spec.faults" :key="f.id" :value="f.id">{{ f.lb }}</option></select>
        <template v-if="spec.limit"><h5>Cấu hình</h5><dl-param k="maxIter" :label="spec.limit.lb" :docs="docs"><input type="range" min="1" :max="spec.limit.max" v-model.number="st.limit"><output>{{ st.limit }}</output></dl-param></template>
        <template v-if="spec.show"><h5>Các khối trong luồng</h5><ul class="dl-small dl-list"><li v-for="n in spec.nodes" :key="n[0]">{{ n[1] }}</li></ul></template>
      </div>
      <div class="dl-main">
        <p class="dl-qtext">“{{ sc.q }}”</p>
        <div class="dl-runbar"><button type="button" class="btn primary" @click="run">▶ Chạy</button><span class="dl-small dl-mut">{{ fault ? 'Đọc từng khối rồi bấm vào khối đầu tiên bị sai.' : 'Đọc dữ liệu vào, ra của từng khối.' }}</span></div>
        <div class="dl-trace">
          <div v-for="(s, i) in result.steps" :key="s.n + i" class="dl-tstep" :class="[s.skip ? 'skip' : '', i < tick ? 'done' : 'wait', pick === s.n ? (fault && patch && s.n === fault.node ? 'al-right' : 'al-wrong') : '']" role="button" tabindex="0" @click="pickNode(s.n)" @keydown.enter.prevent="pickNode(s.n)">
            <div class="dl-thead"><b>{{ s.lb }}</b><span class="dl-tag" v-if="s.skip">không chạy</span><span class="dl-tag" v-if="s.tok">{{ s.tok }} token</span></div>
            <div class="dl-tbody" v-if="!s.skip && i < tick"><div><span class="dl-label">Vào:</span> {{ s.i }}</div><div><span class="dl-label">Ra:</span> {{ s.o }}</div></div>
          </div>
        </div>
        <template v-if="tick >= result.steps.length">
          <div class="dl-chat"><div class="dl-bubble" :class="'t-' + result.tone">{{ result.final }}</div></div>
          <p v-if="result.stopped" class="dl-small n-warn">Dừng vì hết số vòng cho phép, chưa có câu trả lời đầy đủ.</p>
          <p v-if="fault && !patch" class="dl-small dl-mut">Lỗi này không ảnh hưởng tới câu đang chọn, đổi sang câu khác để thấy.</p>
          <p v-if="pick && fault && patch" class="dl-small" :class="pick === fault.node ? 'n-ok' : 'n-warn'">{{ pick === fault.node ? fault.why : 'Chưa phải. Khối này chỉ nhận lại dữ liệu sai từ trước; hãy đi ngược lên.' }}</p>
        </template>
        <p class="dl-small dl-mut">Dấu vết soạn sẵn để luyện đọc log; trên Dify bạn đọc đúng các ô này trong Workflow Process.</p>
      </div>
    </div>
    ${AL_MISSIONS}
  </div>`,
};

/* ---- Function Calling: LLM đề nghị, runtime kiểm tra tham số thật, công cụ trả kết quả ---- */
const AlTool = {
  name: 'AlTool', mixins: [AlBase],
  data() { return { st: this.initial() }; },
  computed: {
    msg() { return this.spec.msgs.find(m => m.id === this.st.q); },
    plan() {
      let d = this.msg.d.base;
      for (const k of Object.keys(this.st.t)) { const key = this.st.t[k] ? k : '!' + k; if (key in this.msg.d) d = this.msg.d[key]; }
      return d;
    },
    tool() { return this.plan.tool ? this.spec.tools.find(t => t.name === this.plan.tool) : null; },
    errors() {
      if (!this.tool || !this.st.check) return [];
      const errs = [];
      for (const p of this.tool.params) {
        const v = (this.plan.args || {})[p.k];
        if (p.req && (v === undefined || v === null || v === '')) errs.push(`thiếu ${p.k}`);
        else if (v !== undefined && p.fmt && !new RegExp(p.fmt).test(String(v))) errs.push(`${p.k} sai định dạng: ${v}`);
      }
      return errs;
    },
    action() { return !this.tool ? this.plan.a : this.errors.length ? 'blocked' : 'call'; },
    bypass() { return this.tool && !this.st.check && this.plan.danger; },
    final() { if (this.action === 'blocked') return this.msg.blocked || 'Mã bạn đưa chưa đúng dạng, bạn kiểm tra lại giúp mình.'; return this.bypass ? this.plan.danger : this.plan.text; },
    tokens() { return this.spec.toolTok * this.spec.tools.length + (this.tool ? 240 : 90); },
    view() { return { q: this.st.q, t: this.st.t, check: this.st.check, out: { action: this.action, tool: this.plan.tool || '', errors: this.errors.length, bad: !!this.plan.bad, bypass: !!this.bypass } }; },
  },
  methods: {
    initial() { const t = {}; for (const g of this.spec.toggles) t[g.k] = true; return { q: this.spec.msgs[0].id, t, check: true }; },
    reset() { this.st = this.initial(); },
    schema(t) { const props = {}; for (const p of t.params) props[p.k] = { type: p.type || 'string', description: p.desc }; return JSON.stringify({ name: t.name, description: (this.st.t.neg ? t.desc + ' ' + t.neg : t.desc), parameters: { properties: props, required: this.st.t.req ? t.params.filter(p => p.req).map(p => p.k) : [] } }, null, 1); },
  },
  template: `
  <div class="dl-core">
    <div class="dl-grid">
      <div class="dl-side">${AL_HEAD}
        <h5>Mô tả công cụ gửi cho LLM</h5>
        <dl-param v-for="g in spec.toggles" :key="g.k" :k="g.doc" :label="g.lb" :docs="docs"><input type="checkbox" v-model="st.t[g.k]"></dl-param>
        <h5>Runtime</h5>
        <dl-param k="rtCheck" label="Kiểm tra tham số trước khi gọi" :docs="docs"><input type="checkbox" v-model="st.check"></dl-param>
        <details class="dl-pv"><summary>Xem mô tả {{ spec.tools.length }} công cụ (LLM chỉ thấy phần này, không thấy mã)</summary><pre v-for="t in spec.tools" :key="t.name">{{ schema(t) }}</pre></details>
      </div>
      <div class="dl-main">
        <div class="dl-ask"><span class="dl-label">Thí sinh nhắn:</span><button v-for="m in spec.msgs" :key="m.id" type="button" class="vdb-chip" :class="{ on: st.q === m.id }" @click="st.q = m.id">{{ m.lb }}</button></div>
        <p class="dl-qtext">“{{ msg.t }}”</p>
        <div class="dl-trace">
          <div class="dl-tstep done"><div class="dl-thead"><b>1. LLM quyết định</b><span class="dl-tag">soạn sẵn</span></div><div class="dl-tbody"><pre class="al-json">{{ tool ? JSON.stringify({ name: plan.tool, arguments: plan.args }) : (action === 'ask' ? 'Không gọi hàm: thiếu thông tin, hỏi lại.' : 'Không gọi hàm: yêu cầu không thuộc công cụ nào.') }}</pre></div></div>
          <div class="dl-tstep" :class="tool ? 'done' : 'skip'"><div class="dl-thead"><b>2. Runtime kiểm tra</b><span class="dl-tag">chạy thật</span></div><div class="dl-tbody" v-if="tool"><span v-if="!st.check" class="n-warn">Đã tắt kiểm tra, gửi thẳng tới công cụ.</span><span v-else-if="errors.length" class="n-bad">Chặn: {{ errors.join('; ') }}</span><span v-else class="n-ok">Đúng định dạng, đúng tham số bắt buộc.</span></div></div>
          <div class="dl-tstep" :class="action === 'call' ? 'done' : 'skip'"><div class="dl-thead"><b>3. Công cụ trả kết quả</b></div><div class="dl-tbody" v-if="action === 'call'"><pre class="al-json">{{ plan.result }}</pre></div></div>
        </div>
        <h6 class="dl-h6">4. LLM trả lời</h6>
        <div class="dl-chat"><div class="dl-bubble" :class="plan.bad || bypass ? 't-bad' : 't-ok'">{{ final }}</div></div>
        <p class="dl-small dl-mut">Mô tả {{ spec.tools.length }} công cụ gửi kèm mỗi lượt, khoảng {{ tokens }} token. Kết quả công cụ lấy từ dữ liệu của API giả lập, quyết định của LLM soạn sẵn.</p>
      </div>
    </div>
    ${AL_MISSIONS}
  </div>`,
};

/* ---- HTTP Request: gọi thật tới API giả lập của khóa học ---- */
const AlHttp = {
  name: 'AlHttp', mixins: [AlBase],
  data() { return { st: this.initial(), res: null, busy: false, seen: [], err: '', same: false }; },
  computed: {
    ep() { return this.spec.endpoints.find(e => e.id === this.st.ep); },
    url() {
      if (this.ep.method === 'POST') return this.spec.base + this.ep.path;
      const q = this.ep.params.map(p => `${p.k}=${encodeURIComponent(this.st.v[p.k] ?? '')}`).join('&');
      return this.spec.base + this.ep.path + (q ? '?' + q : '');
    },
    body() { return this.ep.method === 'POST' ? JSON.stringify(Object.fromEntries(this.ep.params.map(p => [p.k, this.st.v[p.k] ?? ''])), null, 1) : ''; },
    view() {
      return { ep: this.st.ep, auth: this.st.auth, fail: this.st.fail, v: this.st.v, out: { status: this.res ? this.res.status : 0, sent: !!this.res, same: this.same } };
    },
  },
  methods: {
    initial() { const v = {}; for (const e of this.spec.endpoints) for (const p of e.params) v[p.k] = p.def ?? ''; return { ep: this.spec.endpoints[0].id, auth: true, v, fail: 'none' }; },
    reset() { this.st = this.initial(); this.res = null; this.same = false; this.seen = []; },
    async send() {
      this.busy = true; this.err = '';
      try {
        const headers = this.st.auth ? { 'X-Api-Key': this.spec.key } : {};
        if (this.ep.method === 'POST') headers['Content-Type'] = 'application/json';
        const r = await fetch(this.url, { method: this.ep.method, headers, body: this.ep.method === 'POST' ? this.body : undefined });
        const text = await r.text();
        let pretty = text;
        try { pretty = JSON.stringify(JSON.parse(text), null, 1); } catch (e) { /* giữ nguyên chữ */ }
        this.res = { status: r.status, body: pretty, size: text.length };
        if (this.ep.method === 'POST' && r.ok) {
          const id = JSON.parse(text).ma_nhap;
          if (this.seen.includes(id)) this.same = true;
          this.seen.push(id);
        }
      } catch (e) { this.err = 'Chưa gọi được máy chủ. Kiểm tra kết nối rồi thử lại.'; }
      this.busy = false;
    },
  },
  template: `
  <div class="dl-core">
    <div class="dl-grid">
      <div class="dl-side">${AL_HEAD}
        <h5>HTTP Request</h5>
        <dl-param k="httpUrl" label="Điểm gọi" :docs="docs"><select v-model="st.ep"><option v-for="e in spec.endpoints" :key="e.id" :value="e.id">{{ e.method }} {{ e.path }}</option></select></dl-param>
        <dl-param v-for="p in ep.params" :key="p.k" k="httpParams" :label="p.k" :docs="docs"><input type="text" v-model="st.v[p.k]" :aria-label="p.k"></dl-param>
        <dl-param k="httpAuth" label="Authorization: X-Api-Key" :docs="docs"><input type="checkbox" v-model="st.auth"></dl-param>
        <dl-param k="httpErr" label="Error Handling" :docs="docs"><select v-model="st.fail"><option value="none">None</option><option value="branch">Fail Branch</option></select></dl-param>
      </div>
      <div class="dl-main">
        <div class="dl-runbar"><button type="button" class="btn primary" :disabled="busy" @click="send">▶ Gửi yêu cầu thật</button><span class="dl-small dl-mut">{{ ep.note }}</span></div>
        <pre class="dl-rawbox al-json">{{ ep.method }} {{ url }}{{ st.auth ? '\\nX-Api-Key: ' + spec.key : '' }}{{ body ? '\\n\\n' + body : '' }}</pre>
        <p v-if="err" class="dl-err">{{ err }}</p>
        <template v-if="res">
          <h6 class="dl-h6">Đầu ra của khối</h6>
          <div class="dl-stats sm"><div :class="{ warn: res.status >= 400 }"><b>{{ res.status }}</b><span>status_code</span></div><div><b>{{ res.size }}</b><span>byte trong body</span></div></div>
          <pre class="dl-rawbox al-json">{{ res.body }}</pre>
          <p v-if="res.status >= 400" class="dl-small" :class="st.fail === 'branch' ? 'n-ok' : 'n-warn'">{{ st.fail === 'branch' ? 'Nhánh lỗi chạy: trợ lý báo lịch sự và đề nghị liên hệ cán bộ.' : 'Không có nhánh lỗi: khối LLM phía sau nhận body báo lỗi, có thể diễn giải sai. Nên đọc status_code rồi mới đi tiếp.' }}</p>
          <p v-if="same" class="dl-small n-ok">Gửi lại cùng khoa_yeu_cau nhận lại đúng mã nháp cũ: không sinh bản nháp thứ hai.</p>
        </template>
      </div>
    </div>
    ${AL_MISSIONS}
  </div>`,
};

/* ---- Phân tích CSV: tính thật trên file phát cho học viên ---- */
const AlCsv = {
  name: 'AlCsv', mixins: [AlBase],
  data() { return { st: { dedupe: false, blank: false, outlier: false }, rows: null, err: '' }; },
  async mounted() {
    try {
      const r = await fetch(this.spec.file);
      if (!r.ok) throw new Error();
      const lines = (await r.text()).replace(/^﻿/, '').trim().split(/\r?\n/).slice(1);
      this.rows = lines.map(l => { const c = l.split(','); return { ngay: c[0], ma: c[1], nganh: c[2], so: c[3] }; });
    } catch (e) { this.err = 'Chưa tải được file CSV.'; }
  },
  computed: {
    clean() {
      let list = this.rows || [];
      if (this.st.dedupe) { const seen = new Set(); list = list.filter(r => { const k = r.ngay + r.ma; if (seen.has(k)) return false; seen.add(k); return true; }); }
      if (this.st.outlier) list = list.filter(r => !this.isOutlier(r));
      return list;
    },
    issues() {
      if (!this.rows) return [];
      const seen = new Set(), out = [];
      for (const r of this.rows) {
        const k = r.ngay + r.ma;
        if (seen.has(k)) out.push(`Dòng trùng: ${r.nganh}, ngày ${r.ngay}`);
        seen.add(k);
        if (r.so === '') out.push(`Ô trống: ${r.nganh}, ngày ${r.ngay}`);
        if (this.isOutlier(r)) out.push(`Giá trị bất thường: ${r.nganh}, ngày ${r.ngay}, số ${r.so}`);
      }
      return out;
    },
    table() {
      return this.spec.nganh.map(n => {
        const rs = this.clean.filter(r => r.ma === n[0] && r.so !== '');
        const tong = rs.reduce((a, r) => a + Number(r.so), 0);
        const dung = this.spec.answer[n[0]];
        return { ma: n[0], ten: n[1], ct: n[2], tong, tile: tong / n[2] * 100, sai: tong !== dung, dung };
      });
    },
    code() {
      const c = ['import pandas as pd', 'df = pd.read_csv("dang_ky_xet_tuyen_gia_lap.csv")'];
      if (this.st.dedupe) c.push('df = df.drop_duplicates(["ngay_tong_hop", "ma_xet_tuyen"])');
      c.push(this.st.blank ? '# ô trống: không điền số, ghi chú trong báo cáo\ndf = df.dropna(subset=["so_nguyen_vong_moi"])' : '# chưa quyết định cách xử lý ô trống');
      if (this.st.outlier) c.push('# lớn hơn 5 lần trung vị của ngành: loại khỏi phép cộng, hỏi lại đơn vị nhập\ntv = df.groupby("ma_xet_tuyen").so_nguyen_vong_moi.transform("median")\ndf = df[df.so_nguyen_vong_moi <= 5 * tv]');
      c.push('kq = df.groupby("ma_xet_tuyen").so_nguyen_vong_moi.sum()');
      return c.join('\n');
    },
    view() { return this.rows ? { dedupe: this.st.dedupe, blank: this.st.blank, outlier: this.st.outlier, out: { bad: this.table.filter(t => t.sai).length, toan: (this.table.find(t => t.ma === this.spec.toan) || {}).tong, issues: this.issues.length } } : null; },
  },
  methods: {
    reset() { this.st = { dedupe: false, blank: false, outlier: false }; },
    median(ma) {
      const v = this.rows.filter(r => r.ma === ma && r.so !== '').map(r => Number(r.so)).sort((a, b) => a - b);
      return v.length ? v[Math.floor(v.length / 2)] : 0;
    },
    isOutlier(r) { return r.so !== '' && Number(r.so) > 5 * this.median(r.ma); },
  },
  template: `
  <div class="dl-core">
    <p v-if="err" class="dl-err">{{ err }}</p>
    <div v-else-if="rows" class="dl-grid">
      <div class="dl-side">${AL_HEAD}
        <h5>Các bước làm sạch</h5>
        <label class="dl-op"><input type="checkbox" v-model="st.dedupe"> Bỏ dòng trùng</label>
        <label class="dl-op"><input type="checkbox" v-model="st.blank"> Xử lý ô trống, ghi chú lại</label>
        <label class="dl-op"><input type="checkbox" v-model="st.outlier"> Loại giá trị bất thường</label>
        <h5>Máy kiểm tra thấy</h5>
        <ul class="dl-small dl-list"><li v-for="x in issues" :key="x">{{ x }}</li></ul>
        <details class="dl-pv"><summary>Mã Python tương ứng</summary><pre>{{ code }}</pre></details>
      </div>
      <div class="dl-main">
        <div class="dl-stats sm"><div :class="{ warn: view.out.bad }"><b>{{ view.out.bad }}</b><span>ngành có số sai</span></div><div><b>{{ clean.length }}</b><span>dòng đang tính</span></div></div>
        <div class="tablewrap"><table class="dl-vars"><thead><tr><th>Ngành</th><th>Chỉ tiêu</th><th>Đăng ký</th><th>Tỉ lệ</th></tr></thead><tbody>
          <tr v-for="t in table" :key="t.ma" :class="{ 'al-bad': t.sai }"><td>{{ t.ten }}</td><td>{{ t.ct }}</td><td><b>{{ t.tong }}</b><span v-if="t.sai" class="dl-small"> (đúng: {{ t.dung }})</span></td><td>{{ num(t.tile, 1) }}%</td></tr></tbody></table></div>
        <p class="dl-small dl-mut">Phép tính chạy thật trên file. Chỉ tiêu là số thật của thông báo, số đăng ký là giả lập.</p>
      </div>
    </div>
    <p v-else class="dl-mut">Đang tải file…</p>
    ${AL_MISSIONS}
  </div>`,
};

/* ---- Guardrails: nhiều lớp phòng thủ. Xác suất là minh họa; bộ lọc dữ liệu cá nhân và logic hậu quả chạy thật ---- */
const AlGuard = {
  name: 'AlGuard', mixins: [AlBase],
  data() { return { st: this.initial(), runs: null }; },
  computed: {
    pObey() { let p = .6; if (this.st.tag) p *= .55; if (this.st.rule) p *= .5; return p; },
    canHarm() { return this.st.tool === 'send' && !this.st.hitl; },
    pHarm() { return this.canHarm ? this.pObey : 0; },
    exfil() { return this.canHarm; },
    triple() { return this.st.priv && this.st.untrusted && this.exfil; },
    filtered() { return this.st.filter ? this.spec.sample.replace(/\b\d{12}\b/g, '[đã che số định danh]').replace(/\b0\d{9}\b/g, '[đã che số điện thoại]') : this.spec.sample; },
    leaks() { return (this.filtered.match(/\b\d{12}\b|\b0\d{9}\b/g) || []).length; },
    view() {
      return { tag: this.st.tag, rule: this.st.rule, tool: this.st.tool, hitl: this.st.hitl, filter: this.st.filter, priv: this.st.priv, untrusted: this.st.untrusted,
        out: { pHarm: this.pHarm, triple: this.triple, leaks: this.leaks, ran: !!this.runs, harms: this.runs ? this.runs.harm : 0, obeys: this.runs ? this.runs.obey : 0 } };
    },
  },
  methods: {
    initial() { return { tag: false, rule: false, tool: 'send', hitl: false, filter: false, priv: true, untrusted: true }; },
    reset() { this.st = this.initial(); this.runs = null; },
    simulate() {
      let obey = 0, harm = 0;
      for (let i = 0; i < 100; i += 1) if (Math.random() < this.pObey) { obey += 1; if (this.canHarm) harm += 1; }
      this.runs = { obey, harm };
    },
  },
  template: `
  <div class="dl-core">
    <div class="dl-grid">
      <div class="dl-side">${AL_HEAD}
        <h5>Lớp đầu vào</h5>
        <dl-param k="gTag" label="Bọc nội dung ngoài trong thẻ dữ liệu" :docs="docs"><input type="checkbox" v-model="st.tag"></dl-param>
        <dl-param k="gRule" label="Luật: không làm theo lệnh trong dữ liệu" :docs="docs"><input type="checkbox" v-model="st.rule"></dl-param>
        <h5>Lớp quyền hạn</h5>
        <dl-param k="gTool" label="Quyền của công cụ" :docs="docs"><select v-model="st.tool"><option value="read">Chỉ đọc</option><option value="draft">Đọc và tạo nháp</option><option value="send">Đọc và tự gửi đi</option></select></dl-param>
        <h5>Lớp hành động</h5>
        <dl-param k="gHitl" label="Người duyệt trước khi gửi" :docs="docs"><input type="checkbox" v-model="st.hitl"></dl-param>
        <h5>Lớp đầu ra</h5>
        <dl-param k="gFilter" label="Lọc dữ liệu cá nhân" :docs="docs"><input type="checkbox" v-model="st.filter"></dl-param>
        <h5>Bộ ba nguy hiểm</h5>
        <label class="dl-op"><input type="checkbox" v-model="st.priv"> Trợ lý đọc được hồ sơ thí sinh</label>
        <label class="dl-op"><input type="checkbox" v-model="st.untrusted"> Trợ lý đọc nội dung bên ngoài</label>
      </div>
      <div class="dl-main">
        <h6 class="dl-h6">Nội dung trợ lý vừa đọc</h6>
        <pre class="dl-rawbox al-src">{{ spec.content }}</pre>
        <div class="dl-stats sm">
          <div><b>{{ Math.round(pObey * 100) }}%</b><span>LLM làm theo lệnh (minh họa)</span></div>
          <div :class="{ warn: pHarm > 0 }"><b>{{ Math.round(pHarm * 100) }}%</b><span>gây hậu quả thật</span></div>
          <div :class="{ warn: triple }"><b>{{ triple ? 'CÓ' : 'KHÔNG' }}</b><span>đủ bộ ba nguy hiểm</span></div>
        </div>
        <div class="dl-runbar"><button type="button" class="btn sm primary" @click="simulate">▶ Thử 100 lần</button><span v-if="runs" class="dl-small">LLM làm theo lệnh <b>{{ runs.obey }}</b> lần, gây hậu quả thật <b>{{ runs.harm }}</b> lần.</span></div>
        <h6 class="dl-h6">Câu trả lời mẫu đi qua lớp đầu ra <span class="dl-tag">bộ lọc chạy thật</span></h6>
        <div class="dl-chat"><div class="dl-bubble" :class="leaks ? 't-bad' : 't-ok'">{{ filtered }}</div></div>
        <p class="dl-small dl-mut">Các tỉ lệ chỉ để thấy logic nhiều lớp, không phải số đo mô hình nào. Điểm cần nhìn: hậu quả về 0 khi bỏ quyền gửi, còn lời dặn trong prompt chỉ làm tỉ lệ giảm xuống.</p>
      </div>
    </div>
    ${AL_MISSIONS}
  </div>`,
};

/* ---- Xếp mức rủi ro hành động ---- */
const AlTiers = {
  name: 'AlTiers', mixins: [AlBase],
  data() { return { st: { picks: {} }, checked: false }; },
  computed: {
    correct() { return this.spec.items.filter((it, i) => this.st.picks[i] === it.ans).length; },
    view() { return { out: { checked: this.checked, correct: this.correct, total: this.spec.items.length } }; },
  },
  methods: { reset() { this.st = { picks: {} }; this.checked = false; } },
  template: `
  <div class="dl-core">
    <div class="tablewrap"><table class="dl-vars"><thead><tr><th>Hành động của trợ lý</th><th>Mức</th><th v-if="checked">Vì sao</th></tr></thead><tbody>
      <tr v-for="(it, i) in spec.items" :key="i" :class="{ 'al-bad': checked && st.picks[i] !== it.ans }"><td>{{ it.t }}</td>
        <td><select v-model="st.picks[i]" :aria-label="'Mức của: ' + it.t"><option v-for="l in spec.levels" :key="l" :value="l">{{ l }}</option></select></td>
        <td v-if="checked" class="dl-small"><b>{{ it.ans }}.</b> {{ it.why }}</td></tr></tbody></table></div>
    <div class="dl-runbar"><button type="button" class="btn sm primary" @click="checked = true">Kiểm tra</button><span v-if="checked" class="dl-small">Đúng <b>{{ correct }}/{{ spec.items.length }}</b>.</span><button type="button" class="btn sm ghost" @click="reset">↺ Làm lại</button></div>
    ${AL_MISSIONS}
  </div>`,
};

/* ---- Bộ Eval: KPI tính thật từ bảng kết quả, kết quả từng đề của từng phiên bản là minh họa ---- */
const AlEval = {
  name: 'AlEval', mixins: [AlBase],
  data() { return { st: { v: this.spec.versions[0].id, base: this.spec.versions[0].id, n: this.spec.cases.length, rep: 1 }, runs: {} }; },
  computed: {
    cases() { return this.spec.cases.slice(0, this.st.n); },
    ver() { return this.spec.versions.find(v => v.id === this.st.v); },
    rows() {
      return this.cases.map(c => {
        const cur = c.r[this.st.v], base = c.r[this.st.base];
        const run = this.runs[this.st.v] && this.runs[this.st.v][c.id];
        const pass = run !== undefined ? run : (cur === 'f' ? 1 : cur);
        const basePass = base === 'f' ? 1 : base;
        return { ...c, pass, cur, reg: basePass === 1 && pass === 0, fix: basePass === 0 && pass === 1, flaky: cur === 'f' };
      });
    },
    score() { return this.rows.filter(r => r.pass).length; },
    pct() { return this.score / this.cases.length * 100; },
    regs() { return this.rows.filter(r => r.reg); },
    perCase() { return 100 / this.cases.length; },
    cost() { return this.ver.tok * this.spec.price / 1000 * 1000; },
    view() { return { v: this.st.v, base: this.st.base, n: this.st.n, out: { pct: this.pct, score: this.score, regs: this.regs.length, flaky: this.rows.filter(r => r.flaky).length, perCase: this.perCase, ran: !!this.runs[this.st.v], tok: this.ver.tok } }; },
  },
  methods: {
    reset() { this.st = { v: this.spec.versions[0].id, base: this.spec.versions[0].id, n: this.spec.cases.length, rep: 1 }; this.runs = {}; },
    rerun() { const r = {}; for (const c of this.cases) { const x = c.r[this.st.v]; r[c.id] = x === 'f' ? (Math.random() < .55 ? 1 : 0) : x; } this.runs = { ...this.runs, [this.st.v]: r }; },
  },
  template: `
  <div class="dl-core">
    <div class="dl-grid">
      <div class="dl-side">${AL_HEAD}
        <h5>Phiên bản</h5>
        <div class="al-pick"><button v-for="v in spec.versions" :key="v.id" type="button" class="vdb-chip" :class="{ on: st.v === v.id }" @click="st.v = v.id">{{ v.id }}</button></div>
        <p class="dl-small">{{ ver.change }}</p>
        <dl-param k="evBase" label="So với" :docs="docs"><select v-model="st.base"><option v-for="v in spec.versions" :key="v.id" :value="v.id">{{ v.id }}</option></select></dl-param>
        <dl-param k="evSize" label="Số đề dùng" :docs="docs"><input type="range" min="8" :max="spec.cases.length" step="4" v-model.number="st.n"><output>{{ st.n }}</output></dl-param>
        <button type="button" class="btn sm" @click="rerun">🎲 Chạy lại phiên bản này</button>
        <p class="dl-small dl-mut">LLM có tính xác suất: đề đánh dấu “chập chờn” có thể đổi kết quả giữa các lần chạy.</p>
      </div>
      <div class="dl-main">
        <div class="dl-stats sm">
          <div><b>{{ score }}/{{ cases.length }}</b><span>đạt ({{ num(pct, 0) }}%)</span></div>
          <div><b>{{ num(perCase, 1) }}%</b><span>mỗi đề chiếm</span></div>
          <div :class="{ warn: regs.length }"><b>{{ regs.length }}</b><span>đề suy thoái so với {{ st.base }}</span></div>
          <div><b>{{ ver.tok }}</b><span>token mỗi câu</span></div>
          <div><b>{{ ver.lat }}s</b><span>thời gian</span></div>
        </div>
        <div class="tablewrap al-scroll"><table class="dl-vars"><thead><tr><th>Đề</th><th>Loại</th><th>Câu hỏi</th><th>Kết quả</th></tr></thead><tbody>
          <tr v-for="r in rows" :key="r.id" :class="{ 'al-bad': r.reg, 'al-good': r.fix }"><td>{{ r.id }}</td><td>{{ r.type }}</td><td>{{ r.q }}</td><td><b>{{ r.pass ? 'Đạt' : 'Trượt' }}</b><span v-if="r.reg" class="dl-tag bad">suy thoái</span><span v-if="r.fix" class="dl-tag">mới đạt</span><span v-if="r.flaky" class="dl-tag warn">chập chờn</span></td></tr></tbody></table></div>
        <p class="dl-small dl-mut">Kết quả từng đề là minh họa để luyện đọc, không phải lần chạy mô hình thật. KPI cộng thật từ bảng này. Bộ đề và đáp án là thật, lấy từ thông báo 2805.</p>
      </div>
    </div>
    ${AL_MISSIONS}
  </div>`,
};

/* ---- Đọc log: gom nhóm thật trên bảng log giả lập ---- */
const AlLog = {
  name: 'AlLog', mixins: [AlBase],
  data() { return { st: { fix: '', by: 'ly_do' } }; },
  computed: {
    rows() { return this.spec.rows.map(r => { const f = this.st.fix && r.after && r.after[this.st.fix]; return f ? { ...r, ...f } : r; }); },
    groups() {
      const m = {};
      for (const r of this.rows) { if (r.vong1) continue; m[r.ly_do] = (m[r.ly_do] || 0) + 1; }
      return Object.entries(m).sort((a, b) => b[1] - a[1]);
    },
    kpi() {
      const n = this.rows.length, v1 = this.rows.filter(r => r.vong1).length, human = this.rows.filter(r => r.status === 'human').length;
      return { n, v1: v1 / n * 100, human, tok: Math.round(this.rows.reduce((a, r) => a + r.tok, 0) / n), vong: this.rows.reduce((a, r) => a + r.vong, 0) / n };
    },
    fix() { return this.spec.fixes.find(f => f.id === this.st.fix); },
    view() { return { fix: this.st.fix, out: { v1: this.kpi.v1, human: this.kpi.human, tok: this.kpi.tok, top: this.groups[0] ? this.groups[0][0] : '' } }; },
  },
  methods: { reset() { this.st = { fix: '', by: 'ly_do' }; } },
  template: `
  <div class="dl-core">
    <div class="dl-grid">
      <div class="dl-side">${AL_HEAD}
        <h5>Thử một cách sửa</h5>
        <select v-model="st.fix" class="al-sel" aria-label="Cách sửa"><option value="">Chưa sửa gì</option><option v-for="f in spec.fixes" :key="f.id" :value="f.id">{{ f.lb }}</option></select>
        <p v-if="fix" class="dl-small" :class="fix.good ? 'n-ok' : 'n-warn'">{{ fix.note }}</p>
        <h5>Bị trả lại vì lý do gì</h5>
        <div class="dl-probs"><div v-for="g in groups" :key="g[0]" class="dl-prob"><span>{{ g[0] }}</span><i><u :style="{ width: Math.round(g[1] / rows.length * 100) + '%' }"></u></i><b>{{ g[1] }}</b></div></div>
        <p v-if="!groups.length" class="dl-small n-ok">Không còn bài nào bị trả lại.</p>
      </div>
      <div class="dl-main">
        <div class="dl-stats sm">
          <div :class="{ warn: kpi.v1 < 80 }"><b>{{ num(kpi.v1, 0) }}%</b><span>duyệt ngay vòng 1 (mục tiêu &gt; 80%)</span></div>
          <div><b>{{ num(kpi.vong, 1) }}</b><span>vòng trung bình</span></div>
          <div :class="{ warn: kpi.human }"><b>{{ kpi.human }}</b><span>chuyển người</span></div>
          <div><b>{{ kpi.tok }}</b><span>token mỗi bài</span></div>
        </div>
        <div class="tablewrap al-scroll"><table class="dl-vars"><thead><tr><th>Bài</th><th>Vòng</th><th>Lý do trả lại đầu tiên</th><th>Kết quả</th></tr></thead><tbody>
          <tr v-for="r in rows" :key="r.id" :class="{ 'al-bad': r.status === 'human' }"><td>{{ r.id }}</td><td>{{ r.vong }}</td><td>{{ r.vong1 ? '–' : r.ly_do }}</td><td>{{ r.status === 'human' ? 'Chuyển người' : 'Duyệt' }}</td></tr></tbody></table></div>
        <p class="dl-small dl-mut">Log là giả lập, các phép gom nhóm và KPI tính thật trên bảng này.</p>
      </div>
    </div>
    ${AL_MISSIONS}
  </div>`,
};

const AgentLab = {
  name: 'AgentLab',
  components: { AlClassify, AlExtract, AlCode, AlReview, AlMemory, AlTrace, AlTool, AlHttp, AlCsv, AlGuard, AlTiers, AlEval, AlLog },
  props: { spec: Object, caption: String },
  computed: { tag() { return 'al-' + this.spec.lab; } },
  template: `
  <figure class="vdb dl" :aria-label="spec.title">
    <div class="dl-head"><span class="dl-badge">🧪 Lab mini</span><strong>{{ spec.title }}</strong></div>
    <p v-if="spec.intro" class="dl-intro" v-html="spec.intro"></p>
    <component :is="tag" :spec="spec"></component>
    <figcaption v-if="caption">{{ caption }}</figcaption>
  </figure>`,
};
