/* Dùng chung cho trang học viên và giảng viên */
const store = {
  get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
  set(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* chế độ riêng tư */ } },
  del(k) { try { localStorage.removeItem(k); } catch (e) { /* bỏ qua */ } },
};

async function api(method, url, body, token) {
  const headers = { 'X-Requested-With': 'fetch' };
  if (body !== undefined) headers['Content-Type'] = 'application/json';
  if (token) headers['Authorization'] = 'Bearer ' + token;
  let res;
  try {
    res = await fetch(url, { method, headers, body: body === undefined ? undefined : JSON.stringify(body), credentials: 'same-origin' });
  } catch (e) {
    throw new Error('Không thể kết nối tới hệ thống. Vui lòng kiểm tra kết nối mạng rồi thử lại.');
  }
  let data = null;
  try { data = await res.json(); } catch (e) { /* không có JSON */ }
  if (!res.ok) {
    let msg = data && data.detail;
    if (typeof msg !== 'string') msg = res.status >= 500
      ? 'Hệ thống chưa xử lý được yêu cầu. Vui lòng thử lại sau.'
      : 'Thông tin chưa hợp lệ. Vui lòng kiểm tra rồi thử lại.';
    const err = new Error(msg);
    err.status = res.status; err.data = data;
    throw err;
  }
  return data;
}

const STATUS_LABEL = { hidden: 'Chưa mở', open: 'Đang nhận bài', closed: 'Đã đóng bài', revealed: 'Đã công bố' };
const TYPE_LABEL = { mcq: 'Trắc nghiệm', multi: 'Chọn nhiều đáp án', open: 'Tự luận', practice: 'Thực hành' };

function fmtTime(t) {
  if (!t) return '';
  const d = new Date(t * 1000);
  return d.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' }) + ' ' + d.toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit' });
}

/* Tạo khung bài làm rỗng (hoặc từ bài đã lưu) cho một hoạt động */
function initPayload(act, existing) {
  const p = existing ? JSON.parse(JSON.stringify(existing)) : {};
  if (act.type === 'practice') {
    p.fields = p.fields || {};
    for (const f of act.fields) {
      const v = p.fields[f.key];
      if (f.type === 'table') {
        const n = f.rows ? f.rows.length : Math.max(f.min_rows || 1, Array.isArray(v) ? v.length : 0);
        const rows = Array.isArray(v) ? v.slice(0, f.rows ? n : undefined) : [];
        while (rows.length < n) rows.push({});
        p.fields[f.key] = rows;
      } else if (f.type === 'checklist') {
        p.fields[f.key] = Array.isArray(v) ? v : f.items.map(() => false);
      } else if (typeof v !== 'string') {
        p.fields[f.key] = '';
      }
    }
  } else {
    p.answers = p.answers || {};
    if (act.type === 'multi') for (const q of act.questions) if (!Array.isArray(p.answers[q.id])) p.answers[q.id] = [];
  }
  return p;
}

const ContentBlocks = {
  props: { blocks: Array, teacher: Boolean, revealed: Array, stage: Number },
  methods: {
    kind(b) {
      if (!this.teacher) return '';
      if (b.teacher) return 'Chỉ giảng viên';
      if (b.reveal) return 'Gợi ý chữa bài – hiện khi công bố';
      if (b.stage) return 'Đợt ' + b.stage;
      return '';
    },
    // chỉ ghi nhãn ở khối đầu tiên của một đoạn liền nhau cùng loại
    flag(b, i) {
      const k = this.kind(b);
      return k && (i === 0 || this.kind(this.blocks[i - 1]) !== k) ? k : '';
    },
    cls(b) {
      const f = this.kind(b);
      if (!f) return '';
      let c = 'flagged ' + (b.teacher ? 'teacher-only' : b.reveal ? 'reveal' : 'stage');
      // khi trình chiếu: ẩn đáp án chưa công bố và đợt diễn tập chưa mở
      if (b.reveal && !(this.revealed || []).includes(b.reveal)) c += ' unrevealed';
      if (b.stage && this.stage !== undefined && b.stage > this.stage) c += ' unrevealed';
      return c;
    },
  },
  template: `
  <div class="blocks">
    <div v-for="(b, i) in blocks" :key="i" :class="cls(b)">
      <span v-if="flag(b, i)" class="flag">{{ flag(b, i) }}</span>
      <h3 v-if="b.t === 'h3'">{{ b.text }}</h3>
      <h4 v-else-if="b.t === 'h4' || b.t === 'h5'">{{ b.text }}</h4>
      <p v-else-if="b.t === 'p'" :class="b.callout ? 'callout ' + b.callout : ''" v-html="b.html"></p>
      <ol v-else-if="b.t === 'list' && b.ordered"><li v-for="(it, j) in b.items" :key="j" :class="'lvl' + it.level" v-html="it.html"></li></ol>
      <ul v-else-if="b.t === 'list'"><li v-for="(it, j) in b.items" :key="j" :class="'lvl' + it.level" v-html="it.html"></li></ul>
      <div v-else-if="b.t === 'table'" class="tablewrap"><table>
        <thead><tr><th v-for="(c, j) in b.rows[0]" :key="j" :colspan="c.span || 1" v-html="c.html"></th></tr></thead>
        <tbody><tr v-for="(r, k) in b.rows.slice(1)" :key="k"><td v-for="(c, j) in r" :key="j" :colspan="c.span || 1" v-html="c.html"></td></tr></tbody>
      </table></div>
      <pre v-else-if="b.t === 'code'"><code>{{ b.text }}</code></pre>
      <blockquote v-else-if="b.t === 'quote'" v-html="b.html"></blockquote>
      <img v-else-if="b.t === 'img'" :src="b.src" alt="Hình minh họa trong giáo trình" loading="lazy">
      <div v-else-if="b.t === 'activity'" class="act-slot">
        <slot name="activity" :b="b">
          <div class="card act-embed">
            <span class="eyebrow">{{ b.inline ? 'Học viên trả lời ngay trong bài' : 'Thẻ mở bài làm' }}</span>
            <div><b>{{ b.title }}</b></div>
            <ol v-if="b.questions"><li v-for="(q, j) in b.questions" :key="j">{{ q }}</li></ol>
          </div>
        </slot>
      </div>
    </div>
  </div>`,
};

/* Form làm bài: trắc nghiệm, chọn nhiều, tự luận, thực hành */
const ActivityForm = {
  props: { act: Object, payload: Object, readonly: Boolean, showAnswers: Boolean, stats: Object },
  emits: ['dirty'],
  methods: {
    pick(q, o, ev) {
      if (this.readonly) return;
      if (this.act.type === 'multi') {
        const arr = this.payload.answers[q.id] || [];
        const i = arr.indexOf(o.key);
        if (ev.target.checked && i < 0) arr.push(o.key);
        if (!ev.target.checked && i >= 0) arr.splice(i, 1);
        this.payload.answers[q.id] = arr;
      } else {
        this.payload.answers[q.id] = o.key;
      }
      this.$emit('dirty');
    },
    checked(q, o) {
      const v = this.payload.answers && this.payload.answers[q.id];
      return Array.isArray(v) ? v.includes(o.key) : v === o.key;
    },
    optCls(q, o) {
      if (!this.showAnswers || q.correct === undefined) return '';
      const right = Array.isArray(q.correct) ? q.correct.includes(o.key) : q.correct === o.key;
      if (right) return 'right';
      return this.checked(q, o) ? 'wrong' : '';
    },
    pct(q, o) {
      const s = this.stats && this.stats.questions && this.stats.questions[q.id];
      if (!s || !s.n) return 0;
      return Math.round(100 * s.counts[o.key] / s.n);
    },
    optText(o) { return o.text.startsWith(o.key + ' ') ? o.text : o.key + '. ' + o.text; },
    addRow(f) { this.payload.fields[f.key].push({}); this.$emit('dirty'); },
    delRow(f, i) { this.payload.fields[f.key].splice(i, 1); this.$emit('dirty'); },
    touch() { this.$emit('dirty'); },
  },
  template: `
  <div class="activity-form">
    <template v-if="act.type === 'mcq' || act.type === 'multi'">
      <div v-for="(q, qi) in act.questions" :key="q.id" class="q">
        <div class="qtext"><b>Câu {{ qi + 1 }}.</b> {{ q.text }} <span v-if="q.module && act.id.endsWith('-exam')" class="tag">Buổi {{ q.module }}</span></div>
        <label v-for="o in q.options" :key="o.key" class="opt" :class="optCls(q, o)">
          <input :type="act.type === 'multi' ? 'checkbox' : 'radio'" :name="act.id + q.id" :checked="checked(q, o)" :disabled="readonly" @change="pick(q, o, $event)">
          <span class="grow">{{ optText(o) }}</span>
          <span v-if="stats" class="pct">{{ pct(q, o) }}%</span>
        </label>
        <div v-if="showAnswers && q.explain" class="explain">{{ q.explain }}</div>
      </div>
    </template>
    <template v-else-if="act.type === 'open'">
      <div v-for="(q, qi) in act.questions" :key="q.id" class="q">
        <div class="qtext"><b>Câu {{ qi + 1 }}.</b> {{ q.text }}</div>
        <textarea v-model="payload.answers[q.id]" :readonly="readonly" rows="3" @input="touch" placeholder="Câu trả lời của bạn"></textarea>
        <div v-if="showAnswers && q.answer" class="answer"><b>Gợi ý trả lời:</b> {{ q.answer }}</div>
      </div>
    </template>
    <template v-else-if="act.type === 'practice'">
      <div v-for="f in act.fields" :key="f.key" class="pfield">
        <label class="field">{{ f.label }} <div v-if="f.hint" class="hint">{{ f.hint }}</div></label>
        <input v-if="f.type === 'text'" v-model="payload.fields[f.key]" :readonly="readonly" @input="touch">
        <textarea v-else-if="f.type === 'textarea'" v-model="payload.fields[f.key]" :readonly="readonly" rows="4" @input="touch"></textarea>
        <div v-else-if="f.type === 'checklist'" class="checklist">
          <label v-for="(it, i) in f.items" :key="i"><input type="checkbox" v-model="payload.fields[f.key][i]" :disabled="readonly" @change="touch"> <span>{{ it }}</span></label>
        </div>
        <div v-else-if="f.type === 'table'" class="tablewrap">
          <table class="formtable">
            <thead><tr><th v-if="f.rows"></th><th v-for="c in f.columns" :key="c.key">{{ c.label }}</th><th v-if="!f.rows && !readonly"></th></tr></thead>
            <tbody>
              <tr v-for="(r, i) in payload.fields[f.key]" :key="i">
                <td v-if="f.rows" class="rowlabel">{{ f.rows[i] }}</td>
                <td v-for="c in f.columns" :key="c.key">
                  <select v-if="c.options" v-model="r[c.key]" :disabled="readonly" @change="touch">
                    <option :value="undefined">–</option>
                    <option v-for="o in c.options" :key="o" :value="o">{{ o }}</option>
                  </select>
                  <textarea v-else v-model="r[c.key]" :readonly="readonly" rows="2" @input="touch"></textarea>
                </td>
                <td v-if="!f.rows && !readonly"><button class="btn sm ghost" title="Xóa dòng" @click="delRow(f, i)">✕</button></td>
              </tr>
            </tbody>
          </table>
          <div v-if="!f.rows && !readonly" style="padding:6px"><button class="btn sm" @click="addRow(f)">+ Thêm dòng</button></div>
        </div>
      </div>
    </template>
  </div>`,
};

function themeInit() {
  const t = store.get('theme');
  if (t) document.documentElement.dataset.theme = t;
}
function themeToggle() {
  const cur = document.documentElement.dataset.theme
    || (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  const next = cur === 'dark' ? 'light' : 'dark';
  document.documentElement.dataset.theme = next;
  store.set('theme', next);
}
themeInit();

// Giữ mục lục ngay dưới thanh đầu trang khi thanh này xuống dòng ở màn hình hẹp.
window.addEventListener('DOMContentLoaded', () => {
  if (typeof ResizeObserver === 'undefined') return;
  let observedHeader = null;
  const sizeObserver = new ResizeObserver(() => {
    if (observedHeader) document.documentElement.style.setProperty('--topbar-height', observedHeader.offsetHeight + 'px');
  });
  const bindHeader = () => {
    const header = document.querySelector('.topbar');
    if (header === observedHeader) return;
    sizeObserver.disconnect(); observedHeader = header;
    if (header) sizeObserver.observe(header);
  };
  bindHeader();
  new MutationObserver(bindHeader).observe(document.querySelector('#app') || document.body, { childList: true, subtree: true });
});

const LOGO = `<svg width="22" height="22" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 2 4 5v6c0 5 3.4 9.4 8 11 4.6-1.6 8-6 8-11V5l-8-3Zm1 4-4 7h3l-1 5 4-7h-3l1-5Z"/></svg>`;
