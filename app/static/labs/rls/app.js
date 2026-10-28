/* Phòng thí nghiệm RLS – giao diện mô phỏng Power BI Desktop và Power BI service. */
(function () {
  'use strict';
  const { createApp } = Vue;
  const E = RLSEngine, D = RLSData;
  const clone = o => JSON.parse(JSON.stringify(o));
  const NHAN = ['Công khai', 'Nội bộ', 'Mật', 'Hạn chế cao'];
  const WS_ROLES = ['Admin', 'Member', 'Contributor', 'Viewer'];
  const PUBLIC = '__public__';

  function stamp() {
    const d = new Date(), p = n => String(n).padStart(2, '0');
    return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}`;
  }
  function fmt(v) {
    if (v === null || v === undefined) return '';
    if (typeof v === 'object' && 'err' in v) return 'Error';
    if (typeof v === 'number') return v.toLocaleString('vi-VN', { maximumFractionDigits: 2 });
    if (typeof v === 'boolean') return v ? 'True' : 'False';
    return String(v);
  }
  const store = {
    get(k) { try { return JSON.parse(localStorage.getItem(k)); } catch (e) { return null; } },
    set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) { /* trình duyệt chặn lưu: vẫn chạy bình thường */ } },
    del(k) { try { localStorage.removeItem(k); } catch (e) { /* bỏ qua */ } }
  };
  function copyText(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) return navigator.clipboard.writeText(text).catch(() => fallback());
    fallback();
    return Promise.resolve();
    function fallback() {
      const t = document.createElement('textarea'); t.value = text; document.body.appendChild(t); t.select();
      try { document.execCommand('copy'); } catch (e) { /* bỏ qua */ }
      t.remove();
    }
  }
  function download(name, text) {
    const a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob(['﻿' + text], { type: 'text/csv;charset=utf-8' }));
    a.download = name; a.click();
    setTimeout(() => URL.revokeObjectURL(a.href), 1000);
  }
  const csvCell = v => /[",\n;]/.test(String(v)) ? '"' + String(v).replace(/"/g, '""') + '"' : String(v);

  // Nhận kiểu dữ liệu khi dán bằng Enter data (giống tự nhận kiểu của Power Query).
  function detectType(vals) {
    const v = vals.filter(x => x !== '');
    if (v.length && v.every(x => /^-?\d+$/.test(x))) return 'Whole number';
    if (v.length && v.every(x => /^-?\d+([.,]\d+)?$/.test(x))) return 'Decimal number';
    if (v.length && v.every(x => /^\d{4}-\d{2}-\d{2}$/.test(x))) return 'Date';
    return 'Text';
  }
  function parseTsv(text) {
    const lines = String(text || '').replace(/\r/g, '').split('\n').filter(l => l.trim() && !/^```/.test(l.trim()));
    if (!lines.length) return null;
    const split = l => (l.includes('\t') ? l.split('\t') : l.split(/,|;| {2,}/)).map(x => x.trim());
    const head = split(lines[0]);
    const rows = lines.slice(1).map(split);
    return { head, rows };
  }

  // ---------- Hình ảnh trên báo cáo ----------
  const VisualBox = {
    props: ['v', 'res', 'selected', 'editable', 'service', 'sel'],
    emits: ['select', 'toggle', 'menu', 'remove'],
    computed: {
      title() {
        const v = this.v;
        if (v.title) return v.title;
        if (v.type === 'card') return v.measure || 'Card';
        if (v.type === 'slicer') return v.field ? E.parseField(v.field).col : 'Slicer';
        const f = (v.fields || []).map(x => E.parseField(x).col);
        if (v.type === 'bar') return (v.measures[0] || 'Giá trị') + (f.length ? ' theo ' + f[0] : '');
        return f.concat(v.measures || []).join(', ') || 'Table';
      },
      maxBar() {
        const r = this.res;
        if (!r.rows) return 1;
        return Math.max(1, ...r.rows.map(x => Number(x[r.nFields]) || 0));
      },
      hint() {
        return { card: 'Chọn một thước đo trong khung Visualizations', slicer: 'Chọn một trường cho slicer',
          table: 'Thêm trường hoặc thước đo', bar: 'Chọn trục và giá trị' }[this.v.type];
      }
    },
    methods: { fmt },
    template: `
    <div class="vis" :class="['vis-' + v.type, { selected }]" :style="{ gridColumn: 'span ' + (v.w || 4) }" @click="$emit('select')">
      <div class="vis-head"><span class="vis-title">{{ title }}</span>
        <span class="vis-actions">
          <button v-if="service && v.type !== 'slicer'" class="icon" title="Thêm tùy chọn (Export data)" @click.stop="$emit('menu')">⋯</button>
          <button v-if="editable" class="icon" title="Xóa hình ảnh" @click.stop="$emit('remove')">✕</button>
        </span>
      </div>
      <div v-if="res.error === 'denied'" class="vis-err"><b>Không thể tải dữ liệu cho hình ảnh này</b>
        <span>Bạn không có quyền xem dữ liệu này: tài khoản chưa thuộc role bảo mật nào của mô hình.</span></div>
      <div v-else-if="res.error" class="vis-err"><b>Không thể hiển thị hình ảnh này</b><span>{{ res.error }}</span></div>
      <div v-else-if="res.empty" class="vis-empty">{{ hint }}</div>
      <template v-else-if="v.type === 'card'">
        <div class="card-val">{{ fmt(res.value) || '(Trống)' }}</div><div class="card-lbl">{{ v.measure }}</div>
      </template>
      <div v-else-if="v.type === 'slicer'" class="slicer">
        <label v-for="x in res.values" :key="String(x)" @click.stop>
          <input type="checkbox" :checked="!!sel && sel.some(s => s === x)" @change="$emit('toggle', x)"> {{ fmt(x) || '(Trống)' }}
        </label>
        <div v-if="!res.values.length" class="muted">(Không có giá trị)</div>
      </div>
      <div v-else-if="v.type === 'bar'" class="bars">
        <div v-for="(r, i) in res.rows" :key="i" class="bar-row">
          <span class="bar-lbl">{{ fmt(r[0]) || '(Trống)' }}</span>
          <span class="bar-track"><span class="bar" :style="{ width: (100 * (Number(r[res.nFields]) || 0) / maxBar) + '%' }"></span></span>
          <span class="bar-val">{{ fmt(r[res.nFields]) }}</span>
        </div>
        <div v-if="!res.rows.length" class="muted">(Trống)</div>
      </div>
      <div v-else class="tbl-wrap">
        <table class="grid"><thead><tr><th v-for="h in res.headers" :key="h">{{ h }}</th></tr></thead>
          <tbody>
            <tr v-for="(r, i) in res.rows" :key="i"><td v-for="(c, j) in r" :key="j" :class="{ num: typeof c === 'number' }">{{ fmt(c) }}</td></tr>
            <tr v-if="res.total" class="total"><td>Total</td><td v-for="j in res.nFields - 1" :key="'e' + j"></td>
              <td v-for="(c, j) in res.total" :key="'t' + j" class="num">{{ fmt(c) }}</td></tr>
          </tbody>
        </table>
        <div v-if="!res.rows.length" class="muted">(Trống)</div>
      </div>
    </div>`
  };

  const Canvas = {
    components: { VisualBox },
    props: ['model', 'page', 'sec', 'slicers', 'editable', 'selectedId', 'service'],
    emits: ['select', 'toggle', 'menu', 'remove'],
    methods: {
      filtersFor(v) {
        const f = (this.page.filters || []).filter(x => x.values && x.values.length).map(x => ({ field: x.field, values: x.values }));
        for (const o of this.page.visuals) {
          if (o.type === 'slicer' && o.id !== v.id && o.field && (this.slicers[o.id] || []).length) f.push({ field: o.field, values: this.slicers[o.id] });
        }
        return f;
      },
      res(v) { return E.visualData(this.model, this.sec, v, this.filtersFor(v)); }
    },
    template: `
    <div class="canvas"><div class="page-grid">
      <visual-box v-for="v in page.visuals" :key="v.id" :v="v" :res="res(v)" :selected="selectedId === v.id" :editable="editable"
        :service="service" :sel="slicers[v.id]" @select="$emit('select', v.id)" @toggle="x => $emit('toggle', v, x)"
        @menu="$emit('menu', v, filtersFor(v))" @remove="$emit('remove', v)"></visual-box>
      <div v-if="!page.visuals.length" class="canvas-empty">Trang trống. Thêm hình ảnh ở khung <b>Visualizations</b> bên phải.</div>
    </div></div>`
  };

  // ---------- Bài tập và tự kiểm tra ----------
  const relOk = (m, a, ac, b, bc) => m.relationships.some(r => r.from === a && r.fromCol === ac && r.to === b && r.toCol === bc && r.active && r.cross === 'Single');
  const tbl = (m, n) => m.tables.find(t => t.name === n);
  const colType = (m, t, c) => { const x = tbl(m, t); const k = x && x.columns.find(y => y.name === c); return k && k.type; };
  function measureWith(m, re, expect) {
    const sec = E.security(m, { roles: [] });
    return m.measures.find(x => re.test(x.expr.replace(/\s+/g, '')) && E.evalMeasureByName(m, sec, x.name) === expect);
  }
  const visuals = (sc) => sc.desktop.report.pages.flatMap(p => p.visuals);
  function ruleRows(m, role, table, upn) {
    const r = m.roles.find(x => x.name === role);
    if (!r || !r.filters[table]) return null;
    const res = E.checkRule(m, table, r.filters[table], upn);
    if (res.error) return null;
    const sec = E.security(m, { roles: [role], upn });
    return [...new Set(sec.base[table].map(x => x.MaDonVi))].sort().join(',');
  }
  const testHas = (tests, f) => tests.some(f);
  const same = (a, b) => JSON.stringify([...a].sort()) === JSON.stringify([...b].sort());

  const BAI = {
    bi01: {
      intro: 'Dùng Home → Enter data để tạo ba bảng. Dữ liệu để dán nằm ngay dưới đây.',
      steps: ['Home → Enter data: dán khối DimDonVi, đặt tên bảng DimDonVi, Load. Lặp lại với DimNgay và FactDien.',
        'Table view: kiểm tra kiểu dữ liệu từng cột (Ngay là Date ở cả hai bảng, kWh là Whole number, MaKH/MaDonVi là Text).',
        'Ghi số dòng của từng bảng vào bài nộp.'],
      data: true,
      checks: (sc) => {
        const m = sc.desktop.model;
        const n = t => (tbl(m, t) ? tbl(m, t).source.length : -1);
        return [
          ['Có ba bảng DimDonVi (3 dòng), DimNgay (2 dòng), FactDien (8 dòng)', n('DimDonVi') === 3 && n('DimNgay') === 2 && n('FactDien') === 8],
          ['Ngay là Date ở DimNgay và FactDien', colType(m, 'DimNgay', 'Ngay') === 'Date' && colType(m, 'FactDien', 'Ngay') === 'Date'],
          ['kWh là Whole number; MaKH và MaDonVi là Text', colType(m, 'FactDien', 'kWh') === 'Whole number' && colType(m, 'FactDien', 'MaKH') === 'Text' && colType(m, 'FactDien', 'MaDonVi') === 'Text']];
      }
    },
    bi02: {
      intro: 'Ba bảng đã nạp. Tự phát hiện quan hệ (Autodetect) được giả định là đang tắt.',
      steps: ['Model view hoặc Modeling → Manage relationships → New.', 'Nối DimDonVi[MaDonVi] (1) → FactDien[MaDonVi] (*), hướng lọc Single, đang hoạt động.',
        'Nối DimNgay[Ngay] (1) → FactDien[Ngay] (*). Thử nối theo Thang để thấy vì sao không được.'],
      checks: (sc) => {
        const m = sc.desktop.model;
        return [['DimDonVi[MaDonVi] (1) → FactDien[MaDonVi] (*), Single, đang hoạt động', relOk(m, 'DimDonVi', 'MaDonVi', 'FactDien', 'MaDonVi')],
          ['DimNgay[Ngay] (1) → FactDien[Ngay] (*), Single, đang hoạt động', relOk(m, 'DimNgay', 'Ngay', 'FactDien', 'Ngay')]];
      }
    },
    bi03: {
      intro: 'Mô hình đã có quan hệ. Trang báo cáo đang trống.',
      steps: ['Home → New measure: Tong kWh = SUM(FactDien[kWh]).', 'Visualizations → Card, chọn thước đo Tong kWh.',
        'Thêm Table gồm DimDonVi[MaDonVi] và Tong kWh. Đối chiếu tổng các đơn vị với Card.'],
      checks: (sc) => {
        const m = sc.desktop.model;
        const ms = measureWith(m, /^SUM\(FactDien\[kWh\]\)$/i, 1770);
        const vs = visuals(sc);
        return [['Có thước đo SUM(FactDien[kWh]) ra 1.770', !!ms],
          ['Có Card dùng thước đo đó', !!ms && vs.some(v => v.type === 'card' && v.measure === ms.name)],
          ['Có Table gồm DimDonVi[MaDonVi] và thước đo', !!ms && vs.some(v => v.type === 'table' && v.fields.includes('DimDonVi[MaDonVi]') && v.measures.includes(ms.name))]];
      }
    },
    bi04: {
      intro: 'Đã có Tong kWh. Tạo hai thước đo đếm.',
      steps: ['New measure: So KH = DISTINCTCOUNT(FactDien[MaKH]).', 'New measure: So dong = COUNTROWS(FactDien).', 'Đưa cả hai lên Card. Giải thích vì sao 6 khác 8.'],
      checks: (sc) => {
        const m = sc.desktop.model, vs = visuals(sc);
        const a = measureWith(m, /^DISTINCTCOUNT\(FactDien\[MaKH\]\)$/i, 6), b = measureWith(m, /^COUNTROWS\(FactDien\)$/i, 8);
        return [['Thước đo DISTINCTCOUNT ra 6', !!a], ['Thước đo COUNTROWS ra 8', !!b],
          ['Cả hai nằm trên Card', !!a && !!b && vs.some(v => v.type === 'card' && v.measure === a.name) && vs.some(v => v.type === 'card' && v.measure === b.name)]];
      }
    },
    bi05: {
      intro: 'Slicer là công cụ phân tích, không phải phân quyền.',
      steps: ['Thêm Slicer với trường DimDonVi[MaDonVi].', 'Chọn riêng DV_A, ghi Tong kWh và So KH. Bỏ chọn rồi ghi lại.',
        'Giải thích vì sao lưu báo cáo đang lọc DV_A không giới hạn được người xem.'],
      checks: (sc, t, ev) => [['Có Slicer trên DimDonVi[MaDonVi]', visuals(sc).some(v => v.type === 'slicer' && v.field === 'DimDonVi[MaDonVi]')],
        ['Đã chọn riêng DV_A trên slicer', !!ev['slicer:DimDonVi[MaDonVi]=DV_A']], ['Đã bỏ chọn để xem lại toàn bộ', !!ev['slicer:DimDonVi[MaDonVi]=']]]
    },
    bi06: {
      intro: 'Tạo RLS tĩnh rồi dùng View as.',
      steps: ['Modeling → Manage roles → Create: DonVi_A, bảng DimDonVi, biểu thức [MaDonVi] = "DV_A". Tạo DonVi_B tương tự. Save.',
        'Modeling → View as → chọn DonVi_A → OK. Ghi Tong kWh và đơn vị còn thấy. Stop viewing, làm lại với DonVi_B.',
        'Khi đang View as DonVi_A, thử tìm DV_B trên slicer.'],
      checks: (sc, t) => {
        const m = sc.desktop.model;
        return [['DonVi_A chỉ còn DV_A', ruleRows(m, 'DonVi_A', 'DimDonVi') === 'DV_A'], ['DonVi_B chỉ còn DV_B', ruleRows(m, 'DonVi_B', 'DimDonVi') === 'DV_B'],
          ['Đã View as DonVi_A (560 kWh)', testHas(t, x => x.env === 'Desktop – View as' && same(x.roles, ['DonVi_A']) && x.kwh === 560)],
          ['Đã View as DonVi_B (810 kWh)', testHas(t, x => x.env === 'Desktop – View as' && same(x.roles, ['DonVi_B']) && x.kwh === 810)]];
      }
    },
    bi07: {
      intro: 'Thấy vì sao RLS cần quan hệ đúng. Bài làm trên mô phỏng nên không cần lưu bản sao.',
      steps: ['Model view: chọn quan hệ DimDonVi–FactDien, bỏ đánh dấu “Make this relationship active”.',
        'View as DonVi_A. So sánh Card Tong kWh với lúc quan hệ còn hoạt động. Xem cả slicer.',
        'Bật lại quan hệ, View as DonVi_A lần nữa và ghi bằng chứng đã sửa (560).'],
      checks: (sc, t) => {
        const i = t.findIndex(x => x.env === 'Desktop – View as' && same(x.roles, ['DonVi_A']) && x.relOff);
        return [['Đã View as DonVi_A khi quan hệ đang tắt', i >= 0],
          ['Sau đó bật lại quan hệ và View as DonVi_A ra 560', i >= 0 && t.slice(i + 1).some(x => x.env === 'Desktop – View as' && same(x.roles, ['DonVi_A']) && !x.relOff && x.kwh === 560)],
          ['Quan hệ DimDonVi–FactDien hiện đang hoạt động', relOk(sc.desktop.model, 'DimDonVi', 'MaDonVi', 'FactDien', 'MaDonVi')]];
      }
    },
    bi08: {
      intro: 'Một người thuộc hai role thì thấy hợp quyền, không phải phần giao.',
      steps: ['Modeling → View as: đánh dấu cả DonVi_A và DonVi_B, bỏ mọi lựa chọn trên slicer.', 'Ghi đơn vị, Tong kWh, So KH thấy được.',
        'Nếu người xem chỉ cần A, ghi phần cấu hình cần rà lại (thành viên role, nhóm, quyền workspace).'],
      checks: (sc, t) => [['Đã View as đồng thời DonVi_A và DonVi_B (1.370 kWh)', testHas(t, x => x.env === 'Desktop – View as' && same(x.roles, ['DonVi_A', 'DonVi_B']) && x.kwh === 1370)]]
    },
    bi09: {
      intro: 'Lọc theo ngày bằng bảng DimNgay.',
      steps: ['Thêm Slicer với DimNgay[Ngay].', 'Chọn riêng 2026-09-01 rồi riêng 2026-09-02; ghi Tong kWh và So KH.', 'Bỏ lọc ngày. Giải thích vì sao cộng số khách hai ngày không ra số khách duy nhất của cả kỳ.'],
      checks: (sc, t, ev) => [['Có Slicer trên DimNgay[Ngay]', visuals(sc).some(v => v.type === 'slicer' && v.field === 'DimNgay[Ngay]')],
        ['Đã chọn riêng 2026-09-01', !!ev['slicer:DimNgay[Ngay]=2026-09-01']], ['Đã chọn riêng 2026-09-02', !!ev['slicer:DimNgay[Ngay]=2026-09-02']]]
    },
    bi10: {
      intro: 'Phân biệt View as trên Desktop với quyền người dùng thật trên service.',
      steps: ['Home → Publish lên workspace thực hành.', 'Service → Security của semantic model: thêm nguoixem.a vào DonVi_A, nguoixem.b vào DonVi_B.',
        'Workspace → Manage access: thêm ba người xem (nguoixem.a, nguoixem.b, khong.gan) với vai trò Viewer. Thêm thanhvien làm Member để tái hiện lỗi.',
        'Đổi “Đang đăng nhập” sang từng tài khoản, mở báo cáo, ghi kết quả vào ma trận kiểm thử.'],
      checks: (sc, t) => {
        const s = sc.service;
        const svcTest = u => testHas(t, x => x.env === 'Service – đăng nhập' && x.who === u);
        return [['Đã Publish', !!s.model], ['nguoixem.a thuộc DonVi_A, nguoixem.b thuộc DonVi_B',
          (s.security.DonVi_A || []).includes('nguoixem.a@lab.example') && (s.security.DonVi_B || []).includes('nguoixem.b@lab.example')],
          ['Đã đăng nhập thử nguoixem.a, nguoixem.b và khong.gan', svcTest('nguoixem.a@lab.example') && svcTest('nguoixem.b@lab.example') && svcTest('khong.gan@lab.example')],
          ['Đã thử một tài khoản Member/Contributor/Admin khác và thấy RLS không áp', testHas(t, x => x.env === 'Service – đăng nhập' && x.bypass && x.who !== s.owner)]];
      }
    },
    th8: {
      intro: 'Dựng lại dashboard chương 7, lần này có kiểm thử. Số kiểm tra: DV_A 826.436; DV_B 742.030; cả hai 1.568.466 kWh.',
      steps: ['Model view: giữ DimDonVi → FactDien và DimThang → FactDien. Không nối PhanQuyen với bảng nào (xóa quan hệ tự phát hiện nếu có).',
        'Tạo thước đo Tong kWh và So KH binh quan thang (mục 2.5).',
        'Báo cáo: biểu đồ cột Tong kWh theo TenDonVi; Card So KH binh quan thang; Table Phuong – Thang – Tong kWh; Slicer TenDonVi.',
        'Manage roles: DonVi_A, DonVi_B (tĩnh); NguoiXem (động) với hai quy tắc trên DimDonVi và PhanQuyen. Ẩn bảng PhanQuyen (Data pane → 👁).',
        'View as từng role; View as Other user: minh.kehoach, ha.kehoach, moi.vao (cùng role NguoiXem).',
        'Publish. Trên service: gán người vào role (Security), cấp quyền xem (Manage access hoặc App), đăng nhập thử người xem A, người không gán role và một Member.'],
      checks: (sc, t) => {
        const m = sc.desktop.model, vs = visuals(sc);
        const sec = E.security(m, { roles: [] });
        const val = n => E.evalMeasureByName(m, sec, n);
        const tk = m.measures.find(x => val(x.name) === 1568466 && /SUM/i.test(x.expr));
        const kh = m.measures.find(x => val(x.name) === 1437);
        const pq = tbl(m, 'PhanQuyen');
        const dyn = m.roles.find(r => r.name === 'NguoiXem');
        const view = (pred) => testHas(t, x => x.env === 'Desktop – View as' && pred(x));
        return [
          ['Quan hệ DimDonVi → FactDien và DimThang → FactDien đang hoạt động', relOk(m, 'DimDonVi', 'MaDonVi', 'FactDien', 'MaDonVi') && relOk(m, 'DimThang', 'Thang', 'FactDien', 'Thang')],
          ['PhanQuyen không nối với bảng nào', !m.relationships.some(r => r.from === 'PhanQuyen' || r.to === 'PhanQuyen')],
          ['Tong kWh ra 1.568.466; So KH binh quan thang ra 1.437', !!tk && !!kh],
          ['Có biểu đồ cột, Card số khách, Table theo phường – tháng, Slicer TenDonVi',
            vs.some(v => v.type === 'bar') && !!kh && vs.some(v => v.type === 'card' && v.measure === kh.name) &&
            vs.some(v => v.type === 'table' && v.fields.includes('FactDien[Phuong]') && v.fields.includes('FactDien[Thang]')) &&
            vs.some(v => v.type === 'slicer' && v.field === 'DimDonVi[TenDonVi]')],
          ['DonVi_A chỉ DV_A, DonVi_B chỉ DV_B', ruleRows(m, 'DonVi_A', 'DimDonVi') === 'DV_A' && ruleRows(m, 'DonVi_B', 'DimDonVi') === 'DV_B'],
          ['NguoiXem: anh Minh thấy DV_A, DV_B; trưởng phòng Điện lực Y chỉ DV_B', ruleRows(m, 'NguoiXem', 'DimDonVi', 'minh.kehoach@minhan.example') === 'DV_A,DV_B' &&
            ruleRows(m, 'NguoiXem', 'DimDonVi', 'truongphong@dly.example') === 'DV_B'],
          ['PhanQuyen có quy tắc riêng trong NguoiXem và đã ẩn khỏi báo cáo', !!dyn && !!(dyn.filters.PhanQuyen || '').trim() && !!pq && pq.hidden],
          ['Đã View as DonVi_A và DonVi_B', view(x => same(x.roles, ['DonVi_A'])) && view(x => same(x.roles, ['DonVi_B']))],
          ['Đã View as Other user: minh.kehoach, ha.kehoach, moi.vao', ['minh.kehoach@minhan.example', 'ha.kehoach@dly.example', 'moi.vao@dlx.example']
            .every(u => view(x => x.upn === u && x.roles.includes('NguoiXem')))],
          ['Service: đã thử người xem có role, người không gán role và một Member', testHas(t, x => x.env === 'Service – đăng nhập' && !x.bypass && x.roles.length) &&
            testHas(t, x => x.env === 'Service – đăng nhập' && x.denied) && testHas(t, x => x.env === 'Service – đăng nhập' && x.ws === 'Member')]];
      }
    },
    rasoat: {
      intro: 'Báo cáo SanLuong_Q3 đã chạy từ tháng 8/2026. Trước khi mở rộng cho 30 đơn vị, lãnh đạo yêu cầu rà soát toàn bộ việc phân quyền và các đường dữ liệu đi ra ngoài.',
      steps: ['Đọc “ai cần thấy gì” trong Microsoft Entra ID (cột Ghi chú của từng người).',
        'Kiểm tra từng lớp: Workspace (Manage access), App, liên kết chia sẻ, Security (role và thành viên), mô hình trên Desktop (quan hệ, quy tắc, bảng/cột ẩn), Admin portal, Nhật ký hoạt động.',
        'Đăng nhập thử bằng từng tài khoản, ghi số liệu thực tế vào ma trận kiểm thử. Thử cả Export data, Analyze in Excel và mở bằng “Người ngoài internet”.',
        'Với mỗi phát hiện: bằng chứng, nguyên nhân, cách sửa, bài học liên quan (buổi 1–7). Sửa trên mô phỏng rồi kiểm thử lại.'],
      checks: null
    }
  };

  // ---------- Ứng dụng ----------
  const params = new URLSearchParams(location.search);
  const startId = D.SCENARIOS[params.get('bai')] ? params.get('bai') : 'th8';

  createApp({
    components: { RcCanvas: Canvas },
    data() {
      return Object.assign(this.fresh(startId, true), {
        baiOpen: window.innerWidth > 1100, matrixOpen: false, toast: '', toastTimer: null
      });
    },
    computed: {
      groups() {
        const g = {};
        for (const [id, s] of Object.entries(D.SCENARIOS)) (g[s.group] = g[s.group] || []).push({ id, title: s.title });
        return Object.entries(g).map(([name, items]) => ({ name, items }));
      },
      bai() { return BAI[this.scenarioId]; },
      baiTitle() { return D.SCENARIOS[this.scenarioId].title; },
      checks() { return this.bai && this.bai.checks ? this.bai.checks(this.sc, this.tests, this.events) : []; },
      model() { return this.sc.desktop.model; },
      report() { return this.sc.desktop.report; },
      svc() { return this.sc.service; },
      owner() { return this.svc.owner; },
      dPage() { return this.report.pages[this.d.page] || this.report.pages[0]; },
      dSec() {
        const va = this.d.viewAs;
        if (!va) return E.security(this.model, { roles: [] });
        const s = E.security(this.model, { roles: va.roles, upn: va.other ? va.upn : this.owner, noRoleMeans: 'all' });
        s.upn = va.other ? va.upn : this.owner;
        return s;
      },
      viewAsLabel() {
        const va = this.d.viewAs;
        if (!va) return '';
        return [va.other ? va.upn : null].concat(va.roles).filter(Boolean).join(', ') || 'None';
      },
      selVisual() { return this.dPage.visuals.find(v => v.id === this.d.sel) || null; },
      allFields() {
        return this.model.tables.flatMap(t => t.columns.filter(c => !(t.steps || []).some(s => s.op === 'remove' && s.col === c.name)).map(c => `${t.name}[${c.name}]`));
      },
      reportFields() {
        return this.model.tables.filter(t => !t.hidden).flatMap(t => t.columns.filter(c => !c.hidden && !(t.steps || []).some(s => s.op === 'remove' && s.col === c.name)).map(c => `${t.name}[${c.name}]`));
      },
      dirty() {
        if (!this.svc.model) return true;
        return JSON.stringify([this.model, this.report]) !== JSON.stringify([this.svc.model, this.svc.report]);
      },
      calcErrors() { try { return E.materialize(this.model).calcErrors || {}; } catch (e) { return {}; } },
      tableView() {
        const t = this.model.tables.find(x => x.name === this.d.table) || this.model.tables[0];
        if (!t) return null;
        const M = E.materialize(this.model);
        const T = M.tables[t.name];
        return { t, cols: t.columns.filter(c => T.cols.includes(c.name)), rows: T.rows.slice(0, 60), total: T.rows.length };
      },
      modelLayout() {
        const ts = this.model.tables;
        const many = new Set(this.model.relationships.map(r => r.to));
        const one = new Set(this.model.relationships.map(r => r.from));
        const colOf = t => (many.has(t.name) && !one.has(t.name) ? 1 : one.has(t.name) ? 0 : 2);
        const yNext = [20, 20, 20], pos = {};
        const W = 190;
        for (const t of ts) {
          const c = colOf(t);
          const h = 34 + 20 * t.columns.length;
          pos[t.name] = { x: 20 + c * 290, y: yNext[c], w: W, h };
          yNext[c] += h + 30;
        }
        const lines = this.model.relationships.map(r => {
          const a = pos[r.from], b = pos[r.to];
          if (!a || !b) return null;
          const ax = a.x + (b.x >= a.x ? a.w : 0), bx = b.x + (b.x >= a.x ? 0 : b.w);
          const ay = a.y + 34 + 20 * Math.max(0, this.colIndex(r.from, r.fromCol)) + 10, by = b.y + 34 + 20 * Math.max(0, this.colIndex(r.to, r.toCol)) + 10;
          return { r, ax, ay, bx, by, mx: (ax + bx) / 2, my: (ay + by) / 2 };
        }).filter(Boolean);
        return { pos, lines, h: Math.max(...yNext, 200) + 20, w: 20 + 3 * 290 };
      },
      // Phiên mở báo cáo trên service
      sv() {
        const o = this.s.open;
        if (!o) return null;
        const item = o.report === 'main' ? { name: this.reportName, model: this.svc.model, report: this.svc.report } : this.svc.extra.find(x => x.id === o.report);
        if (!item || !item.model) return { error: 'Báo cáo chưa được publish.' };
        let sec, acc = null, banner;
        if (o.as === PUBLIC) {
          sec = E.security(item.model, { bypass: true });
          banner = 'Người ngoài internet mở mã nhúng công khai: không cần đăng nhập, không có RLS.';
        } else if (o.test) {
          const t = o.test;
          let roles = t.roles.slice();
          if (t.upn && !roles.length) roles = E.access(this.svc, t.upn).roles || [];
          sec = E.security(item.model, { roles, upn: t.upn || this.owner, noRoleMeans: 'none' });
          banner = 'Now viewing as: ' + [t.upn].concat(roles).filter(Boolean).join(', ');
        } else {
          acc = E.access(this.svc, o.as);
          if (!acc.signIn || !acc.open) return { item, acc, denied: true };
          if (o.report !== 'main') {
            if (!acc.ws) return { item, acc, denied: true };
            sec = E.security(item.model, { bypass: true });
          } else {
            sec = E.security(item.model, { roles: acc.roles, upn: o.as, bypass: acc.bypass, noRoleMeans: 'none' });
          }
        }
        sec.upn = o.test ? (o.test.upn || this.owner) : o.as;
        return { item, sec, acc, banner, page: item.report.pages[o.page] || item.report.pages[0] };
      },
      signedInUser() { return this.svc.directory.users.find(u => u.upn === this.svc.signedIn) || null; },
      isOwner() { return this.svc.signedIn === this.owner; },
      myAccess() { return this.svc.signedIn === PUBLIC ? null : E.access(this.svc, this.svc.signedIn); },
      reportName() { return this.scenarioId === 'rasoat' || this.scenarioId === 'th8' ? 'SanLuong_Q3' : 'bai_BI_ca_nhan'; },
      principals() { return this.svc.directory.users.map(u => u.upn).concat(this.svc.directory.groups.map(g => g.name)); },
      permissionsList() {
        // “Manage permissions” của semantic model: ai có quyền đọc và qua đâu.
        return this.svc.directory.users.map(u => ({ u, a: E.access(this.svc, u.upn) })).filter(x => x.a.open);
      },
      resultText() {
        const m = this.model, L = [];
        L.push(`Bài: ${this.baiTitle} (phòng thí nghiệm RLS – mô phỏng)`);
        L.push('Quan hệ: ' + (m.relationships.map(r => `${r.from}[${r.fromCol}] (1) → ${r.to}[${r.toCol}] (*), ${r.cross}${r.active ? '' : ', ĐANG TẮT'}`).join('; ') || '(chưa có)'));
        L.push('Thước đo: ' + (m.measures.map(x => `${x.name} = ${x.expr.replace(/\s+/g, ' ')}`).join('; ') || '(chưa có)'));
        for (const r of m.roles) L.push(`Role ${r.name}: ` + Object.entries(r.filters).filter(([, e]) => e.trim()).map(([t, e]) => `${t}: ${e.replace(/\s+/g, ' ')}`).join(' | '));
        if (this.svc.model) {
          L.push('Thành viên role trên service: ' + Object.entries(this.svc.security).map(([r, mem]) => `${r}: ${mem.join(', ') || '(trống)'}`).join('; '));
          L.push('Workspace: ' + this.svc.workspace.access.map(a => `${a.principal} = ${a.role}`).join('; '));
        }
        L.push('');
        L.push(this.matrixTsv());
        return L.join('\n');
      }
    },
    watch: {
      sc: { deep: true, handler() { this.persist(); } },
      tests: { deep: true, handler() { this.persist(); } },
      'svc.signedIn'() { this.s.open = null; this.s.page = 'home'; }
    },
    methods: {
      fmt,
      fresh(id, useStore) {
        const saved = useStore ? store.get('rlslab:' + id) : null;
        const sc = saved && saved.v === 2 ? saved.sc : D.SCENARIOS[id].build();
        return {
          scenarioId: id, sc, tests: (saved && saved.tests) || [], events: (saved && saved.events) || {},
          mode: id === 'rasoat' ? 'service' : (id === 'bi10' ? 'desktop' : 'desktop'),
          d: { view: 'report', page: 0, sel: null, slicers: {}, viewAs: null, table: null, rel: null, ribbon: 'Home', editSrc: false, newRow: {} },
          s: { page: 'home', open: null, slicers: {}, testPick: { roles: [], upn: '' } },
          dlg: null, formula: null
        };
      },
      persist() { store.set('rlslab:' + this.scenarioId, { v: 2, sc: this.sc, tests: this.tests, events: this.events }); },
      loadScenario() {
        const id = this.scenarioId;
        Object.assign(this, this.fresh(id, true));
        const u = new URL(location.href); u.searchParams.set('bai', id); history.replaceState(null, '', u);
      },
      reset() {
        if (!confirm('Làm lại từ đầu bài này? Mọi thay đổi và ma trận kiểm thử của bài sẽ bị xóa.')) return;
        store.del('rlslab:' + this.scenarioId);
        Object.assign(this, this.fresh(this.scenarioId, false));
        this.persist();
      },
      say(msg) { this.toast = msg; clearTimeout(this.toastTimer); this.toastTimer = setTimeout(() => { this.toast = ''; }, 3500); },
      colIndex(t, c) { const x = tbl(this.model, t); return x ? x.columns.findIndex(k => k.name === c) : 0; },
      audit(action, item, detail, user) {
        this.svc.audit.push({ at: stamp(), user: user || this.svc.signedIn, action, item, detail: detail || '' });
      },

      // ----- Kiểm thử -----
      addTest(o) {
        const m = o.model, sec = o.sec;
        let kwh = null, units = '';
        if (sec.denied) units = 'Không thấy dữ liệu';
        else if (m.tables.some(t => t.name === 'FactDien')) {
          const rows = E.rowsOf(m, sec, 'FactDien');
          const ok = rows.filter(r => typeof r.kWh === 'number');
          kwh = ok.length ? ok.reduce((a, r) => a + r.kWh, 0) : null;
          const dim = E.rowsOf(m, E.security(m, { bypass: true }), 'DimDonVi');
          const name = id => { const h = dim.find(x => x.MaDonVi === id); return h ? h.TenDonVi : id; };
          units = [...new Set(rows.map(r => r.MaDonVi))].sort().map(name).join(', ') || 'Không thấy dữ liệu';
        }
        const relOff = !m.relationships.some(r => r.from === 'DimDonVi' && r.to === 'FactDien' && r.active);
        const row = { at: stamp(), env: o.env, who: o.who || '', upn: o.upn || '', ws: o.ws || '', roles: o.roles || [], bypass: !!o.bypass,
          denied: !!sec.denied, units, kwh, relOff, note: o.note || '', expected: '', pass: '' };
        const last = this.tests[this.tests.length - 1];
        if (last && JSON.stringify([last.env, last.who, last.upn, last.roles, last.kwh, last.units, last.relOff]) ===
          JSON.stringify([row.env, row.who, row.upn, row.roles, row.kwh, row.units, row.relOff])) return;
        this.tests.push(row);
      },
      matrixTsv() {
        const head = ['Lần', 'Môi trường', 'Tài khoản / danh tính', 'Vai trò truy cập', 'Role RLS áp dụng', 'Đơn vị thấy', 'Tổng kWh', 'Ghi chú', 'Kỳ vọng', 'Đạt?'];
        const rows = this.tests.map((t, i) => [i + 1, t.env, t.who || t.upn || '', t.ws || '', t.bypass ? 'Không áp RLS' : (t.roles.join(', ') || '(không)'),
          t.units, t.kwh === null ? '' : fmt(t.kwh), t.note, t.expected, t.pass]);
        return [head].concat(rows).map(r => r.join('\t')).join('\n');
      },
      copyMatrix() { copyText(this.matrixTsv()).then(() => this.say('Đã chép ma trận (dán được vào Excel hoặc ô bài nộp).')); },
      downloadMatrix() {
        const text = this.matrixTsv().split('\n').map(l => l.split('\t').map(csvCell).join(',')).join('\n');
        download('ma_tran_kiem_thu_RLS.csv', text);
      },
      copyResult() { copyText(this.resultText).then(() => this.say('Đã chép kết quả. Dán vào ô “Kết quả và cách đối chiếu” của bài nộp.')); },
      copyData(name) { copyText(D.ENTER_DATA[name]).then(() => this.say(`Đã chép dữ liệu ${name}. Mở Home → Enter data và dán.`)); },

      // ----- Desktop: báo cáo -----
      toggleSlicer(bag, v, x) {
        const cur = bag[v.id] || [];
        bag[v.id] = cur.some(y => y === x) ? cur.filter(y => y !== x) : cur.concat([x]);
        const sel = bag[v.id];
        this.events[`slicer:${v.field}=${sel.length === 1 ? sel[0] : sel.length ? '*' : ''}`] = true;
        this.persist();
      },
      addVisual(type) {
        const id = 'v' + Date.now().toString(36) + Math.random().toString(36).slice(2, 6);
        const v = { id, type, w: type === 'table' ? 6 : type === 'bar' ? 5 : 3, fields: [], measures: [] };
        if (type === 'card') v.measure = '';
        if (type === 'slicer') v.field = '';
        this.dPage.visuals.push(v);
        this.d.sel = id;
      },
      removeVisual(v) { const p = this.dPage; p.visuals.splice(p.visuals.indexOf(v), 1); if (this.d.sel === v.id) this.d.sel = null; },
      addTo(list, value) { if (value && !list.includes(value)) list.push(value); },
      addPage() { this.report.pages.push({ name: 'Page ' + (this.report.pages.length + 1), visuals: [], filters: [] }); this.d.page = this.report.pages.length - 1; },
      addPageFilter(field) { if (field) this.dPage.filters.push({ field, values: [], locked: false, hidden: false }); },
      filterValues(field) {
        const p = E.parseField(field);
        return [...new Set(E.rowsOf(this.model, this.dSec, p.table).map(r => r[p.col]))].sort((a, b) => String(a).localeCompare(String(b), 'vi'));
      },
      toggleIn(list, x) { const i = list.indexOf(x); if (i >= 0) list.splice(i, 1); else list.push(x); },

      // ----- Desktop: thanh công thức -----
      newMeasure(table) {
        const t = table || (this.model.tables.find(x => x.name === 'FactDien') || this.model.tables[0] || {}).name;
        if (!t) return this.say('Chưa có bảng nào. Nạp dữ liệu trước (Home → Enter data).');
        this.formula = { kind: 'measure', table: t, text: 'Measure = ', err: '', edit: null };
      },
      editMeasure(m) { this.formula = { kind: 'measure', table: m.table, text: `${m.name} = ${m.expr}`, err: '', edit: m.name }; },
      newColumn(table) {
        const t = table || (this.d.view === 'table' && this.tableView ? this.tableView.t.name : (this.model.tables[0] || {}).name);
        if (!t) return this.say('Chưa có bảng nào.');
        this.formula = { kind: 'column', table: t, text: 'Column = ', err: '', edit: null };
      },
      commitFormula() {
        const f = this.formula;
        const i = f.text.indexOf('=');
        if (i < 1) { f.err = 'Cú pháp: Tên = biểu thức'; return; }
        const name = f.text.slice(0, i).trim().replace(/^\[|\]$/g, ''), expr = f.text.slice(i + 1).trim();
        if (!name) { f.err = 'Thiếu tên.'; return; }
        if (f.kind === 'measure') {
          const others = this.model.measures.filter(x => x.name !== f.edit);
          if (others.some(x => x.name.toLowerCase() === name.toLowerCase())) { f.err = `Đã có thước đo tên ${name}.`; return; }
          const trial = clone(this.model);
          trial.measures = others.concat([{ name, table: f.table, expr }]);
          const r = E.checkMeasure(trial, expr);
          if (r.error) { f.err = r.error; return; }
          const old = this.model.measures.find(x => x.name === f.edit);
          if (old) {
            if (old.name !== name) this.report.pages.forEach(p => p.visuals.forEach(v => {
              if (v.measure === old.name) v.measure = name;
              v.measures = (v.measures || []).map(x => (x === old.name ? name : x));
            }));
            Object.assign(old, { name, expr });
          } else this.model.measures.push({ name, table: f.table, expr });
          this.say(`Thước đo ${name} = ${fmt(r.value) || '(Trống)'} khi chưa lọc.`);
        } else {
          const t = tbl(this.model, f.table);
          if (t.columns.some(c => c.name.toLowerCase() === name.toLowerCase())) { f.err = `Bảng ${f.table} đã có cột ${name}.`; return; }
          const r = E.checkCalcColumn(this.model, f.table, expr);
          if (r.error) { f.err = r.error; return; }
          t.columns.push({ name, type: typeof r.sample === 'number' ? 'Decimal number' : 'Text', hidden: false, calc: expr });
          this.say(`Đã thêm cột tính toán ${f.table}[${name}].`);
        }
        this.formula = null;
      },
      deleteMeasure(m) {
        if (!confirm(`Xóa thước đo ${m.name}?`)) return;
        this.model.measures.splice(this.model.measures.indexOf(m), 1);
      },

      // ----- Desktop: hộp thoại -----
      open(kind, extra) { this.dlg = Object.assign({ kind }, extra || {}); },
      openEnter() { this.open('enter', { name: 'Table', text: '', err: '' }); },
      enterPreview() { return parseTsv(this.dlg.text); },
      loadEnter() {
        const g = this.dlg, p = parseTsv(g.text);
        const name = g.name.trim();
        if (!name) { g.err = 'Đặt tên bảng.'; return; }
        if (!p || !p.head.length || !p.rows.length) { g.err = 'Dán dữ liệu có dòng tiêu đề và ít nhất một dòng.'; return; }
        if (this.model.tables.some(t => t.name.toLowerCase() === name.toLowerCase())) { g.err = `Đã có bảng ${name}. Đặt tên khác hoặc xóa bảng cũ trong Table view.`; return; }
        if (new Set(p.head).size !== p.head.length) { g.err = 'Tên cột bị trùng.'; return; }
        const cols = p.head.map((h, i) => ({ name: h, type: detectType(p.rows.map(r => r[i] || '')), hidden: false }));
        this.model.tables.push({ name, hidden: false, columns: cols, steps: [],
          source: p.rows.map(r => Object.fromEntries(p.head.map((h, i) => [h, r[i] === undefined ? '' : r[i]]))) });
        this.dlg = null;
        this.say(`Đã nạp bảng ${name}: ${p.rows.length} dòng. Kiểm tra kiểu dữ liệu trong Table view.`);
      },
      openPQ() {
        if (!this.model.tables.length) return this.say('Chưa có bảng nào.');
        this.open('pq', { table: (this.model.tables.find(t => t.name === 'DSKhachHang') || this.model.tables[0]).name });
      },
      pqTable() { return tbl(this.model, this.dlg.table); },
      pqCols() { const t = this.pqTable(); return t.columns.filter(c => !c.calc && !t.steps.some(s => s.op === 'remove' && s.col === c.name)); },
      pqRows() { const M = E.materialize(this.model); return M.tables[this.dlg.table].rows.slice(0, 8); },
      pqStep(op, col) {
        const t = this.pqTable();
        if (op === 'remove' && t.columns.some(c => c.calc && c.calc.includes('[' + col + ']'))) {
          if (!confirm(`Cột tính toán đang dùng [${col}]. Xóa cột nguồn sẽ làm cột tính toán bị lỗi. Tiếp tục?`)) return;
        }
        t.steps.push({ op, col });
        if (op === 'remove') {
          const f = `${t.name}[${col}]`;
          this.report.pages.forEach(p => p.visuals.forEach(v => { v.fields = (v.fields || []).filter(x => x !== f); if (v.field === f) v.field = ''; }));
        }
      },
      stepLabel(s) { return s.op === 'remove' ? `Removed Columns: ${s.col}` : s.op === 'mask' ? `Replaced Value (che): ${s.col}` : `${s.op}: ${s.col}`; },
      openRoles() {
        if (!this.model.tables.length) return this.say('Chưa có bảng nào.');
        const roles = clone(this.model.roles);
        this.open('roles', { roles, role: roles[0] ? roles[0].name : null, table: this.model.tables[0].name, msg: '', err: '', newName: roles[0] ? roles[0].name : '', testUpn: '' });
      },
      roleSel() { return this.dlg.roles.find(r => r.name === this.dlg.role); },
      roleCreate() {
        let n = 1;
        while (this.dlg.roles.some(r => r.name === 'Untitled' + (n > 1 ? n : ''))) n++;
        const name = 'Untitled' + (n > 1 ? n : '');
        this.dlg.roles.push({ name, filters: {}, ols: {} });
        this.dlg.role = name; this.dlg.newName = name;
      },
      roleRename() {
        const r = this.roleSel(), n = this.dlg.newName.trim();
        if (!r || !n || n === r.name) return;
        if (this.dlg.roles.some(x => x.name === n)) { this.dlg.err = 'Đã có role cùng tên.'; return; }
        r.name = n; this.dlg.role = n; this.dlg.err = '';
      },
      roleDelete() { const r = this.roleSel(); if (r) { this.dlg.roles.splice(this.dlg.roles.indexOf(r), 1); this.dlg.role = this.dlg.roles[0] ? this.dlg.roles[0].name : null; } },
      roleCheck() {
        const r = this.roleSel(); if (!r) return;
        const expr = r.filters[this.dlg.table] || '';
        if (!expr.trim()) { this.dlg.msg = 'Bảng này chưa có quy tắc: role không lọc bảng này.'; this.dlg.err = ''; return; }
        const upn = (this.dlg.testUpn || '').trim() || this.owner;
        const res = E.checkRule(this.model, this.dlg.table, expr, upn);
        if (res.error) { this.dlg.err = res.error; this.dlg.msg = ''; }
        else { this.dlg.err = ''; this.dlg.msg = `Không có lỗi cú pháp. Với USERPRINCIPALNAME() = ${upn}: giữ ${res.count}/${res.total} dòng của ${this.dlg.table}.`; }
      },
      roleSave() {
        for (const r of this.dlg.roles) {
          for (const [t, e] of Object.entries(r.filters)) {
            if (!e.trim()) { delete r.filters[t]; continue; }
            const res = E.checkRule(this.model, t, e, this.owner);
            if (res.error) { this.dlg.role = r.name; this.dlg.table = t; this.dlg.err = `Role ${r.name}, bảng ${t}: ${res.error}`; return; }
          }
        }
        const oldNames = this.model.roles.map(r => r.name);
        this.model.roles = this.dlg.roles;
        const gone = oldNames.filter(n => !this.model.roles.some(r => r.name === n));
        if (this.d.viewAs) this.d.viewAs.roles = this.d.viewAs.roles.filter(n => !gone.includes(n));
        this.dlg = null;
        this.say('Đã lưu role. Dùng Modeling → View as để kiểm tra.');
      },
      setOls(key, val) { const o = this.roleSel().ols; if (val === 'None') o[key] = 'None'; else delete o[key]; },
      olsCols() { const t = tbl(this.model, this.dlg.table); return t ? t.columns : []; },
      openViewAs() {
        if (!this.model.roles.length) this.say('Mô hình chưa có role. View as chỉ thử được “Other user”.');
        const va = this.d.viewAs;
        this.open('viewas', { roles: va ? va.roles.slice() : [], other: va ? va.other : false, upn: va && va.upn ? va.upn : '' });
      },
      applyViewAs() {
        const g = this.dlg;
        if (g.other && !g.upn.trim()) { this.say('Nhập tên người dùng (email) cho Other user.'); return; }
        this.d.viewAs = { roles: g.roles.filter(r => this.model.roles.some(x => x.name === r)), other: g.other, upn: g.upn.trim() };
        this.dlg = null;
        this.$nextTick(() => {
          const va = this.d.viewAs;
          this.addTest({ env: 'Desktop – View as', who: [va.other ? va.upn : null].concat(va.roles).filter(Boolean).join(' + ') || 'None',
            upn: va.other ? va.upn : '', roles: va.roles, model: this.model, sec: this.dSec,
            note: va.roles.length ? '' : 'Desktop: không chọn role nào thì không áp RLS' });
        });
      },
      stopViewAs() { this.d.viewAs = null; },

      // ----- Desktop: quan hệ -----
      openRels() { this.open('rels', { from: '', fromCol: '', to: '', toCol: '', msg: '', err: '' }); },
      colsOf(t) { const x = tbl(this.model, t); return x ? x.columns.filter(c => !c.calc).map(c => c.name) : []; },
      relCheck() {
        const g = this.dlg;
        const r = E.checkRelationship(this.model, g.from, g.fromCol, g.to, g.toCol);
        g.err = r.error || ''; g.msg = r.error ? '' : [r.cardinality ? 'Bản số: ' + r.cardinality : '', r.warn || '', r.info || ''].filter(Boolean).join(' ');
        return r;
      },
      relCreate() {
        const g = this.dlg, r = this.relCheck();
        if (r.error) return;
        if (r.cardinality === '*:*' && !confirm(r.warn + '\nVẫn tạo quan hệ nhiều–nhiều?')) return;
        let [a, ac, b, bc] = [g.from, g.fromCol, g.to, g.toCol];
        if (r.swap) [a, ac, b, bc] = [b, bc, a, ac];
        const active = !this.model.relationships.some(x => x.active && ((x.from === a && x.to === b) || (x.from === b && x.to === a)));
        this.model.relationships.push({ id: `${a}.${ac}-${b}.${bc}-${Date.now().toString(36)}`, from: a, fromCol: ac, to: b, toCol: bc, active, cross: r.cardinality === '*:*' ? 'Both' : 'Single', secBoth: false, many: r.cardinality === '*:*' });
        g.from = g.fromCol = g.to = g.toCol = '';
        g.msg = active ? 'Đã tạo quan hệ.' : 'Đã tạo quan hệ ở trạng thái không hoạt động vì giữa hai bảng đã có một đường hoạt động.';
      },
      relDelete(r) { if (confirm('Xóa quan hệ này?')) { this.model.relationships.splice(this.model.relationships.indexOf(r), 1); this.d.rel = null; } },
      relLabel(r) { return `${r.from}[${r.fromCol}] ${r.many ? '*' : '1'} → * ${r.to}[${r.toCol}]`; },
      srcCols() { const t = this.tableView.t; return t.columns.filter(c => !c.calc).map(c => c.name); },
      addSourceRow() {
        const t = this.tableView.t, row = {};
        for (const c of this.srcCols()) row[c] = (this.d.newRow[c] || '').trim();
        if (Object.values(row).every(v => !v)) return;
        t.source.push(row);
        this.d.newRow = {};
      },
      deleteSourceRow(i) { this.tableView.t.source.splice(i, 1); },
      deleteTable(t) {
        if (!confirm(`Xóa bảng ${t.name} khỏi mô hình? Quan hệ và hình ảnh dùng bảng này cũng bị xóa.`)) return;
        this.model.tables.splice(this.model.tables.indexOf(t), 1);
        this.model.relationships = this.model.relationships.filter(r => r.from !== t.name && r.to !== t.name);
        this.report.pages.forEach(p => p.visuals.forEach(v => {
          v.fields = (v.fields || []).filter(f => !f.startsWith(t.name + '['));
          if (v.field && v.field.startsWith(t.name + '[')) v.field = '';
        }));
        this.d.table = null;
      },

      // ----- Publish -----
      publish() {
        if (!this.model.tables.length) return this.say('Chưa có gì để publish.');
        const first = !this.svc.model;
        this.svc.model = clone(this.model);
        this.svc.report = clone(this.report);
        this.svc.publishedAt = stamp();
        for (const r of this.svc.model.roles) if (!this.svc.security[r.name]) this.svc.security[r.name] = [];
        for (const k of Object.keys(this.svc.security)) if (!this.svc.model.roles.some(r => r.name === k)) delete this.svc.security[k];
        this.audit('PublishReport', this.reportName, first ? 'Publish lần đầu' : 'Publish lại (giữ thành viên của các role cùng tên)', this.owner);
        this.say(first ? `Đã publish ${this.reportName} lên workspace. Sang Power BI service để gán người vào role.` : 'Đã publish lại. Thành viên role được giữ nguyên theo tên role.');
      },

      // ----- Service -----
      openReport(report, as, test) {
        this.s.open = { report, as: as || this.svc.signedIn, test: test || null, page: 0 };
        this.s.slicers = {};
        this.s.page = 'report';
        this.$nextTick(() => this.logOpen());
      },
      logOpen() {
        const sv = this.sv, o = this.s.open;
        if (!sv || sv.error) return;
        if (o.as === PUBLIC) {
          this.addTest({ env: 'Publish to web', who: 'Người ngoài internet', model: sv.item.model, sec: sv.sec, note: 'Không đăng nhập, không RLS' });
          return;
        }
        if (o.test) {
          const roles = sv.sec.roles;
          this.addTest({ env: 'Service – Test as role', who: [o.test.upn].concat(o.test.roles).filter(Boolean).join(' + '), upn: o.test.upn,
            roles, model: sv.item.model, sec: sv.sec, note: 'Test as role: chưa kiểm tra quyền mở báo cáo của tài khoản' });
          return;
        }
        const a = sv.acc;
        if (a && (!a.signIn || !a.open)) {
          this.addTest({ env: 'Service – đăng nhập', who: o.as, upn: o.as, ws: '', model: sv.item.model, sec: { denied: true, base: {} }, note: a.reason });
          return;
        }
        this.audit('ViewReport', sv.item.name, a ? a.paths.join('; ') : '', o.as);
        this.addTest({ env: 'Service – đăng nhập', who: o.as, upn: o.as, ws: a.ws || (a.paths || []).join(', '), roles: a.bypass ? [] : a.roles,
          bypass: a.bypass, model: sv.item.model, sec: sv.sec, note: a.bypass ? `${a.ws}: RLS không áp dụng` : (sv.sec.denied ? 'Chưa thuộc role nào: mặc định từ chối' : (a.paths || []).join('; ')) });
      },
      closeReport() { this.s.open = null; this.s.page = this.isOwner ? 'workspace' : 'home'; },
      testAs() {
        const t = this.s.testPick;
        if (!t.roles.length && !t.upn) return this.say('Chọn ít nhất một role hoặc nhập một người để xem dưới tên họ.');
        this.openReport('main', this.owner, { roles: t.roles.slice(), upn: t.upn.trim() });
      },
      addMember(role, p) {
        if (!p) return;
        const list = this.svc.security[role] = this.svc.security[role] || [];
        if (!list.includes(p)) { list.push(p); this.audit('AddRoleMember', role, p); }
      },
      removeMember(role, p) { const l = this.svc.security[role]; l.splice(l.indexOf(p), 1); this.audit('RemoveRoleMember', role, p); },
      addAccess(p, role) {
        if (!p) return;
        const ex = this.svc.workspace.access.find(a => a.principal === p);
        if (ex) ex.role = role; else this.svc.workspace.access.push({ principal: p, role });
        this.audit('UpdateWorkspaceAccess', this.svc.workspace.name, `${p} = ${role}`);
      },
      removeAccess(a) {
        if (a.principal === this.owner && a.role === 'Admin') return this.say('Không gỡ Admin cuối cùng của workspace.');
        this.svc.workspace.access.splice(this.svc.workspace.access.indexOf(a), 1);
        this.audit('DeleteWorkspaceAccess', this.svc.workspace.name, a.principal);
      },
      openShare() { this.open('share', { type: 'people', recipients: [], pick: '', reshare: false, build: false }); },
      createShare() {
        const g = this.dlg;
        if (g.type === 'people' && !g.recipients.length) return this.say('Thêm ít nhất một người nhận.');
        this.svc.shares.push({ id: 'sh' + Date.now().toString(36), type: g.type, recipients: g.recipients.slice(), reshare: g.reshare, build: g.build, by: this.svc.signedIn, at: stamp() });
        this.audit('ShareReport', this.reportName, (g.type === 'org' ? 'Liên kết: Mọi người trong tổ chức' : 'Người cụ thể: ' + g.recipients.join(', ')) + (g.reshare ? ', cho chia sẻ lại' : '') + (g.build ? ', cho Build' : ''));
        this.dlg = null;
        this.say('Đã tạo liên kết chia sẻ.');
      },
      shareLabel(s) { return (s.type === 'org' ? 'Mọi người trong tổ chức có liên kết' : 'Người cụ thể: ' + s.recipients.join(', ')) + (s.reshare ? ' · chia sẻ lại' : '') + (s.build ? ' · Build' : ''); },
      removeShare(s) { this.svc.shares.splice(this.svc.shares.indexOf(s), 1); this.audit('DeleteShareLink', this.reportName, this.shareLabel(s)); },
      publishToWeb(reportId) {
        const item = reportId === 'main' ? { name: this.reportName, model: this.svc.model } : this.svc.extra.find(x => x.id === reportId);
        if (!this.svc.tenant.publishToWeb) return this.open('msg', { title: 'Publish to web', text: 'Quản trị viên đã tắt Publish to web trong Admin portal. Không tạo được mã nhúng công khai.' });
        if (item.model.roles.length) return this.open('msg', { title: 'Không thể Publish to web', text: 'Báo cáo này dùng bảo mật cấp dòng (RLS) nên không thể tạo mã nhúng công khai. Lưu ý: người khác vẫn có thể tạo bản sao mô hình không có RLS rồi publish bản sao.' });
        this.open('ptw', { reportId, name: item.name });
      },
      confirmPtw() {
        const g = this.dlg;
        this.svc.embeds.push({ id: 'e' + Date.now().toString(36), report: g.reportId, by: this.svc.signedIn, at: stamp(), url: 'https://app.powerbi.example/view?r=' + Math.random().toString(36).slice(2, 12) });
        this.audit('PublishToWebReport', g.name, 'Tạo mã nhúng công khai');
        this.dlg = null;
        this.say('Đã tạo mã nhúng: bất kỳ ai có liên kết đều xem được, không cần đăng nhập.');
      },
      deleteEmbed(e) { this.svc.embeds.splice(this.svc.embeds.indexOf(e), 1); this.audit('DeleteEmbedCode', this.embedName(e), e.url); },
      embedName(e) { return e.report === 'main' ? this.reportName : ((this.svc.extra.find(x => x.id === e.report) || {}).name || e.report); },
      deleteExtra(x) {
        if (!confirm(`Xóa ${x.name} (báo cáo và mô hình) khỏi workspace? Mã nhúng của nó cũng mất hiệu lực.`)) return;
        this.svc.extra.splice(this.svc.extra.indexOf(x), 1);
        this.svc.embeds = this.svc.embeds.filter(e => e.report !== x.id);
        this.audit('DeleteReport', x.name, 'Xóa bản sao và mô hình đi kèm');
      },
      visualMenu(v, filters) {
        const sv = this.sv;
        const can = this.canExport();
        this.open('export', { v, filters, mode: 'summarized', can });
      },
      canExport() {
        const sv = this.sv, o = this.s.open, t = this.svc.tenant;
        const build = o.as === PUBLIC ? false : o.test ? true : (sv.acc ? (sv.acc.build || sv.acc.bypass) : true);
        return { summarized: t.exportSummarized, underlying: t.exportUnderlying && build, build };
      },
      exportData() {
        const g = this.dlg, sv = this.sv, model = sv.item.model;
        if (g.mode === 'summarized') {
          const res = E.visualData(model, sv.sec, g.v, g.filters);
          if (res.error) return { error: res.error === 'denied' ? 'Không có dữ liệu để xuất.' : res.error };
          if ('value' in res) return { headers: [g.v.measure], rows: [[res.value]] };
          if (res.values) return { headers: [g.v.field], rows: res.values.map(x => [x]) };
          return { headers: res.headers, rows: res.rows };
        }
        // Dữ liệu gốc: mọi cột không ẩn của bảng chi tiết nhất dùng trong hình ảnh, theo RLS và bộ lọc.
        const fields = (g.v.fields || []).concat(g.v.field ? [g.v.field] : []);
        const ms = (g.v.measures || []).concat(g.v.measure ? [g.v.measure] : []);
        const tables = [...new Set(fields.map(f => E.parseField(f).table).concat(ms.map(n => (model.measures.find(x => x.name === n) || {}).table).filter(Boolean)))];
        const anchor = tables.find(a => model.relationships.some(r => r.to === a)) || tables[0];
        if (!anchor) return { error: 'Không xác định được dữ liệu gốc.' };
        const t = model.tables.find(x => x.name === anchor);
        const cols = t.columns.filter(c => !c.hidden && !sv.sec.olsHidden.has(`${anchor}[${c.name}]`) && !(t.steps || []).some(s => s.op === 'remove' && s.col === c.name)).map(c => c.name);
        const base = sv.sec.base[anchor] || [];
        return { headers: cols, rows: base.map(r => cols.map(c => r[c])), note: 'Dữ liệu gốc gồm các cột không ẩn của bảng ' + anchor + ' (đã áp RLS).' };
      },
      doExport() {
        const r = this.exportData();
        if (r.error) return this.say(r.error);
        const name = `${this.sv.item.name} [${this.svc.label}].csv`;
        download(name, [r.headers].concat(r.rows.map(x => x.map(fmt))).map(l => l.map(csvCell).join(',')).join('\n'));
        if (this.s.open.as !== PUBLIC) this.audit('ExportReport', this.sv.item.name, (this.dlg.mode === 'summarized' ? 'Dữ liệu tóm tắt' : 'Dữ liệu gốc') + ` (${r.rows.length} dòng), nhãn ${this.svc.label}`, this.s.open.test ? this.owner : this.s.open.as);
      },
      openAnalyze() {
        const can = this.canExport();
        if (!can.build) return this.open('msg', { title: 'Analyze in Excel', text: 'Bạn không có quyền Build trên semantic model nên không dùng được Analyze in Excel.' });
        this.open('analyze', { table: this.sv.item.model.tables[0].name });
        this.audit('AnalyzeInExcel', this.sv.item.name, '', this.s.open.test ? this.owner : this.s.open.as);
      },
      analyzeData() {
        const sv = this.sv, model = sv.item.model, t = model.tables.find(x => x.name === this.dlg.table);
        const M = E.materialize(model);
        const cols = M.tables[t.name].cols.filter(c => !sv.sec.olsHidden.has(`${t.name}[${c}]`));
        return { cols, rows: (sv.sec.base[t.name] || []).slice(0, 60), hiddenCols: t.columns.filter(c => c.hidden).map(c => c.name), total: (sv.sec.base[t.name] || []).length };
      },
      addAudience(p) { if (p && !this.svc.app.audience.includes(p)) { this.svc.app.audience.push(p); this.audit('UpdateApp', 'App', 'Thêm người xem: ' + p); } },
      groupAdd(g, p) { if (p && !g.members.includes(p) && p !== g.name) { g.members.push(p); this.audit('AddGroupMember', g.name, p); } },
      groupRemove(g, p) { g.members.splice(g.members.indexOf(p), 1); this.audit('RemoveGroupMember', g.name, p); },
      toggleUser(u) { u.status = u.status === 'active' ? 'disabled' : 'active'; this.audit(u.status === 'active' ? 'EnableAccount' : 'DisableAccount', u.upn, ''); },
      userName(p) { const u = this.svc.directory.users.find(x => x.upn === p); return u ? `${u.name} (${p})` : `Nhóm ${p}`; },
      reachable() {
        // Nội dung người đang đăng nhập mở được.
        const me = this.svc.signedIn;
        if (me === PUBLIC) return [];
        const a = this.myAccess, out = [];
        if (!a.signIn) return out;
        if (this.svc.model) out.push({ id: 'main', name: this.reportName, how: a.open ? a.paths.join(' · ') : 'Không có quyền' , ok: a.open });
        for (const x of this.svc.extra) out.push({ id: x.id, name: x.name, how: a.ws ? 'Workspace: ' + a.ws : 'Không có quyền', ok: !!a.ws });
        return out;
      }
    },
    template: `
<div class="app">
  <header class="top">
    <div class="brand"><span class="logo">▮▮▮</span><div><b>Phòng thí nghiệm RLS</b><small>Mô phỏng Power BI để học phân quyền – dữ liệu giả lập, không phải Power BI thật</small></div></div>
    <label class="scen">Bài <select v-model="scenarioId" @change="loadScenario">
      <optgroup v-for="g in groups" :key="g.name" :label="g.name"><option v-for="s in g.items" :key="s.id" :value="s.id">{{ s.title }}</option></optgroup>
    </select></label>
    <div class="modes" role="tablist">
      <button :class="{ on: mode === 'desktop' }" @click="mode = 'desktop'">🖥 Power BI Desktop</button>
      <button :class="{ on: mode === 'service' }" @click="mode = 'service'">☁ Power BI service</button>
    </div>
    <div class="top-right">
      <button @click="matrixOpen = !matrixOpen" :class="{ on: matrixOpen }">🧪 Ma trận kiểm thử ({{ tests.length }})</button>
      <button @click="baiOpen = !baiOpen" :class="{ on: baiOpen }">📋 Đề bài</button>
      <button @click="reset" title="Làm lại bài từ đầu">↺ Làm lại</button>
    </div>
  </header>

  <div class="body">
  <main class="main">
  <!-- ================= DESKTOP ================= -->
  <section v-if="mode === 'desktop'" class="desk">
    <div class="ribbon">
      <div class="rtabs">
        <button v-for="t in ['Home', 'Modeling']" :key="t" :class="{ on: d.ribbon === t }" @click="d.ribbon = t">{{ t }}</button>
        <span class="file">{{ reportName }}.pbix<span v-if="dirty && svc.model" class="dot" title="Có thay đổi chưa publish"> ● chưa publish</span></span>
      </div>
      <div class="rbtns" v-if="d.ribbon === 'Home'">
        <button @click="openEnter"><i>⊞</i>Enter data</button>
        <button @click="openPQ"><i>⚙</i>Transform data</button>
        <button @click="newMeasure()"><i>Σ</i>New measure</button>
        <button @click="newColumn()"><i>ƒ</i>New column</button>
        <span class="sep"></span>
        <button @click="publish" class="pub"><i>⇪</i>Publish</button>
      </div>
      <div class="rbtns" v-else>
        <button @click="openRels"><i>⛓</i>Manage relationships</button>
        <button @click="newMeasure()"><i>Σ</i>New measure</button>
        <span class="sep"></span>
        <button @click="openRoles"><i>🛡</i>Manage roles</button>
        <button @click="openViewAs"><i>👁</i>View as</button>
      </div>
    </div>
    <div v-if="d.viewAs" class="viewas-bar">Now viewing as: <b>{{ viewAsLabel }}</b>
      <span v-if="!d.viewAs.roles.length" class="warn-chip">Không role nào được chọn: Desktop không áp RLS</span>
      <button @click="stopViewAs">Stop viewing</button></div>
    <div v-if="formula" class="formula">
      <span class="fx">{{ formula.kind === 'measure' ? 'Σ' : 'ƒ' }} {{ formula.table }}</span>
      <input v-model="formula.text" @keydown.enter="commitFormula" @keydown.esc="formula = null" spellcheck="false" autofocus>
      <button class="ok" @click="commitFormula" title="Xác nhận (Enter)">✓</button><button @click="formula = null" title="Hủy (Esc)">✕</button>
      <div v-if="formula.err" class="ferr">{{ formula.err }}</div>
    </div>
    <div class="desk-main">
      <nav class="rail">
        <button :class="{ on: d.view === 'report' }" title="Report view" @click="d.view = 'report'">▤<small>Report</small></button>
        <button :class="{ on: d.view === 'table' }" title="Table view" @click="d.view = 'table'">▦<small>Table</small></button>
        <button :class="{ on: d.view === 'model' }" title="Model view" @click="d.view = 'model'">⛓<small>Model</small></button>
      </nav>

      <div class="work">
        <!-- Report view -->
        <template v-if="d.view === 'report'">
          <rc-canvas :model="model" :page="dPage" :sec="dSec" :slicers="d.slicers" :editable="true" :selected-id="d.sel" :service="false"
            @select="id => d.sel = id" @toggle="(v, x) => toggleSlicer(d.slicers, v, x)" @remove="removeVisual"></rc-canvas>
          <div class="pages">
            <button v-for="(p, i) in report.pages" :key="i" :class="{ on: d.page === i }" @click="d.page = i; d.sel = null">{{ p.name }}</button>
            <button @click="addPage" title="Thêm trang">+</button>
          </div>
        </template>

        <!-- Table view -->
        <div v-else-if="d.view === 'table'" class="tableview">
          <div v-if="!tableView" class="empty-note">Chưa có bảng. Dùng Home → Enter data.</div>
          <template v-else>
            <div class="tv-head">
              <label>Bảng <select :value="tableView.t.name" @change="d.table = $event.target.value"><option v-for="t in model.tables" :key="t.name" :value="t.name">{{ t.name }}{{ t.hidden ? ' (ẩn)' : '' }}</option></select></label>
              <span class="muted">{{ tableView.total }} dòng</span>
              <button @click="newColumn(tableView.t.name)">ƒ New column</button>
              <button :class="{ on: d.editSrc }" @click="d.editSrc = !d.editSrc" title="Mô phỏng sửa tệp nguồn (Excel, SharePoint) rồi Refresh">✎ Sửa dữ liệu nguồn</button>
              <button class="danger" @click="deleteTable(tableView.t)">Xóa bảng</button>
            </div>
            <div v-if="d.editSrc" class="src-edit">
              <p class="small muted">Ngoài đời, bảng như PhanQuyen được sửa ở tệp nguồn rồi Refresh. Sửa xong ở đây, nhớ <b>Publish</b> để service dùng dữ liệu mới.</p>
              <div class="add-row"><input v-for="c in srcCols()" :key="c" v-model="d.newRow[c]" :placeholder="c">
                <button @click="addSourceRow">+ Thêm dòng</button></div>
            </div>
            <div class="tbl-wrap big"><table class="grid">
              <thead><tr><th v-for="c in tableView.cols" :key="c.name">
                <div class="th-name">{{ c.calc ? 'ƒ ' : '' }}{{ c.name }}<span v-if="c.hidden" class="tag">ẩn</span></div>
                <select v-if="!c.calc" v-model="c.type" title="Column tools → Data type"><option v-for="t in ['Text', 'Whole number', 'Decimal number', 'Date']" :key="t">{{ t }}</option></select>
                <div v-else class="calc" :title="c.calc">= {{ c.calc }}</div>
                <div v-if="calcErrors[tableView.t.name + '[' + c.name + ']']" class="ferr small">{{ calcErrors[tableView.t.name + '[' + c.name + ']'] }}</div>
              </th><th v-if="d.editSrc"></th></tr></thead>
              <tbody><tr v-for="r in tableView.rows" :key="r.__id"><td v-for="c in tableView.cols" :key="c.name" :class="{ num: typeof r[c.name] === 'number', bad: r[c.name] && r[c.name].err !== undefined }">{{ fmt(r[c.name]) }}</td>
                <td v-if="d.editSrc"><button class="icon" title="Xóa dòng này ở nguồn" @click="deleteSourceRow(r.__id)">✕</button></td></tr></tbody>
            </table></div>
          </template>
        </div>

        <!-- Model view -->
        <div v-else class="modelview">
          <div class="mv-tools"><button @click="openRels">⛓ Manage relationships</button><span class="muted">Bấm vào một đường nối để sửa quan hệ.</span></div>
          <div class="mv-scroll">
          <svg :width="modelLayout.w" :height="modelLayout.h" class="mv">
            <g v-for="l in modelLayout.lines" :key="l.r.id" class="rel" :class="{ off: !l.r.active, sel: d.rel === l.r.id }" @click="d.rel = l.r.id">
              <path :d="'M' + l.ax + ',' + l.ay + ' C' + l.mx + ',' + l.ay + ' ' + l.mx + ',' + l.by + ' ' + l.bx + ',' + l.by" />
              <path class="hit" :d="'M' + l.ax + ',' + l.ay + ' C' + l.mx + ',' + l.ay + ' ' + l.mx + ',' + l.by + ' ' + l.bx + ',' + l.by" />
              <text :x="l.ax + (l.bx > l.ax ? 8 : -14)" :y="l.ay - 4">{{ l.r.many ? '*' : '1' }}</text>
              <text :x="l.bx + (l.bx > l.ax ? -14 : 8)" :y="l.by - 4">*</text>
              <text :x="l.mx - 6" :y="l.my + 4" class="dir">{{ l.r.cross === 'Both' ? '⇄' : (l.bx > l.ax ? '→' : '←') }}</text>
            </g>
            <g v-for="t in model.tables" :key="t.name" :transform="'translate(' + modelLayout.pos[t.name].x + ',' + modelLayout.pos[t.name].y + ')'" class="mtable" :class="{ hid: t.hidden }">
              <rect :width="modelLayout.pos[t.name].w" :height="modelLayout.pos[t.name].h" rx="6" />
              <text x="10" y="21" class="tname">{{ t.name }}{{ t.hidden ? ' 👁‍🗨' : '' }}</text>
              <text v-for="(c, i) in t.columns" :key="c.name" x="12" :y="48 + i * 20" :class="{ hidcol: c.hidden }">{{ c.calc ? 'ƒ ' : '' }}{{ c.name }}</text>
            </g>
          </svg>
          </div>
          <div class="rel-list">
            <h4>Quan hệ ({{ model.relationships.length }})</h4>
            <div v-if="!model.relationships.length" class="muted">Chưa có quan hệ.</div>
            <div v-for="r in model.relationships" :key="r.id" class="rel-item" :class="{ sel: d.rel === r.id }" @click="d.rel = r.id">
              <b>{{ relLabel(r) }}</b><span v-if="r.auto" class="tag">tự phát hiện</span>
              <label><input type="checkbox" v-model="r.active"> Make this relationship active</label>
              <label>Cross filter direction <select v-model="r.cross"><option>Single</option><option>Both</option></select></label>
              <label :class="{ dim: r.cross !== 'Both' }"><input type="checkbox" v-model="r.secBoth" :disabled="r.cross !== 'Both'"> Apply security filter in both directions</label>
              <button class="danger" @click.stop="relDelete(r)">Xóa</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Các khung bên phải -->
      <aside class="panes">
        <section v-if="d.view === 'report'" class="pane">
          <h4>Filters <small>trang {{ dPage.name }}</small></h4>
          <div v-for="(f, i) in dPage.filters" :key="i" class="filter">
            <div class="frow"><b>{{ f.field }}</b>
              <button class="icon" :class="{ on: f.locked }" title="Khóa bộ lọc (người xem không đổi được)" @click="f.locked = !f.locked">{{ f.locked ? '🔒' : '🔓' }}</button>
              <button class="icon" :class="{ on: f.hidden }" title="Ẩn bộ lọc khỏi người xem" @click="f.hidden = !f.hidden">{{ f.hidden ? '🙈' : '👁' }}</button>
              <button class="icon" title="Xóa" @click="dPage.filters.splice(i, 1)">✕</button></div>
            <label v-for="x in filterValues(f.field)" :key="String(x)" class="fv"><input type="checkbox" :checked="f.values.includes(x)" @change="toggleIn(f.values, x)"> {{ fmt(x) || '(Trống)' }}</label>
          </div>
          <select @change="addPageFilter($event.target.value); $event.target.value = ''"><option value="">+ Thêm trường vào bộ lọc trang</option><option v-for="f in reportFields" :key="f">{{ f }}</option></select>
        </section>
        <section v-if="d.view === 'report'" class="pane">
          <h4>Visualizations</h4>
          <div class="vtypes">
            <button @click="addVisual('card')" title="Card">▭<small>Card</small></button>
            <button @click="addVisual('table')" title="Table">▦<small>Table</small></button>
            <button @click="addVisual('bar')" title="Clustered bar chart">▤<small>Bar</small></button>
            <button @click="addVisual('slicer')" title="Slicer">☰<small>Slicer</small></button>
          </div>
          <div v-if="selVisual" class="wells">
            <div class="muted">Đang chọn: {{ selVisual.type }}</div>
            <label>Tiêu đề <input v-model="selVisual.title" placeholder="(tự động)"></label>
            <label>Độ rộng <select v-model.number="selVisual.w"><option v-for="w in [2, 3, 4, 5, 6, 8, 12]" :key="w" :value="w">{{ w }}/12</option></select></label>
            <template v-if="selVisual.type === 'card'">
              <label>Fields <select v-model="selVisual.measure"><option value="">(chọn thước đo)</option><option v-for="m in model.measures" :key="m.name">{{ m.name }}</option></select></label>
            </template>
            <template v-else-if="selVisual.type === 'slicer'">
              <label>Field <select v-model="selVisual.field"><option value="">(chọn trường)</option><option v-for="f in reportFields" :key="f">{{ f }}</option></select></label>
            </template>
            <template v-else>
              <div class="well"><b>{{ selVisual.type === 'bar' ? 'Y-axis (trục)' : 'Columns' }}</b>
                <span v-for="(f, i) in selVisual.fields" :key="f" class="chip">{{ f }} <button @click="selVisual.fields.splice(i, 1)">✕</button></span>
                <select @change="addTo(selVisual.fields, $event.target.value); $event.target.value = ''"><option value="">+ trường</option><option v-for="f in reportFields" :key="f">{{ f }}</option></select>
              </div>
              <div class="well"><b>{{ selVisual.type === 'bar' ? 'X-axis (giá trị)' : 'Values' }}</b>
                <span v-for="(m, i) in selVisual.measures" :key="m" class="chip">Σ {{ m }} <button @click="selVisual.measures.splice(i, 1)">✕</button></span>
                <select @change="addTo(selVisual.measures, $event.target.value); $event.target.value = ''"><option value="">+ thước đo</option><option v-for="m in model.measures" :key="m.name">{{ m.name }}</option></select>
              </div>
            </template>
          </div>
          <div v-else class="muted">Bấm vào một hình ảnh trên trang để sửa trường.</div>
        </section>
        <section class="pane data-pane">
          <h4>Data</h4>
          <div v-if="!model.tables.length" class="muted">Chưa có bảng.</div>
          <details v-for="t in model.tables" :key="t.name" open>
            <summary><b :class="{ hid: t.hidden }">▦ {{ t.name }}</b>
              <button class="icon" :title="t.hidden ? 'Unhide' : 'Hide in report view'" @click.prevent="t.hidden = !t.hidden">{{ t.hidden ? '🙈' : '👁' }}</button>
              <button class="icon" title="New measure trong bảng này" @click.prevent="newMeasure(t.name)">Σ+</button></summary>
            <div v-for="c in t.columns" :key="c.name" class="field" :class="{ hid: c.hidden, gone: (t.steps || []).some(s => s.op === 'remove' && s.col === c.name) }">
              <span>{{ c.calc ? 'ƒ' : '·' }} {{ c.name }}</span><small>{{ c.type }}</small>
              <button class="icon" :title="c.hidden ? 'Unhide' : 'Hide in report view'" @click="c.hidden = !c.hidden">{{ c.hidden ? '🙈' : '👁' }}</button>
            </div>
            <div v-for="m in model.measures.filter(x => x.table === t.name)" :key="m.name" class="field measure">
              <span @click="editMeasure(m)" title="Sửa thước đo">Σ {{ m.name }}</span>
              <button class="icon" title="Xóa thước đo" @click="deleteMeasure(m)">✕</button>
            </div>
          </details>
        </section>
      </aside>
    </div>
  </section>

  <!-- ================= SERVICE ================= -->
  <section v-else class="svc">
    <div class="svc-top">
      <b>Power BI</b><span class="crumb">{{ isOwner ? svc.workspace.name : 'Trang chủ' }}</span>
      <label class="acct">Đang đăng nhập
        <select v-model="svc.signedIn">
          <option v-for="u in svc.directory.users" :key="u.upn" :value="u.upn">{{ u.name }} – {{ u.upn }}{{ u.status !== 'active' ? ' (bị khóa)' : '' }}</option>
          <option :value="'__public__'">Người ngoài internet (không đăng nhập)</option>
        </select></label>
    </div>
    <div class="svc-main">
      <nav class="svc-nav">
        <button :class="{ on: s.page === 'home' }" @click="s.page = 'home'; s.open = null">⌂ Trang chủ</button>
        <template v-if="isOwner">
          <button :class="{ on: s.page === 'workspace' }" @click="s.page = 'workspace'; s.open = null">▣ Workspace</button>
          <button :class="{ on: s.page === 'security' }" @click="s.page = 'security'; s.open = null">🛡 Security (RLS)</button>
          <button :class="{ on: s.page === 'perm' }" @click="s.page = 'perm'; s.open = null">🔑 Manage permissions</button>
          <button :class="{ on: s.page === 'admin' }" @click="s.page = 'admin'; s.open = null">⚙ Admin portal</button>
          <button :class="{ on: s.page === 'dir' }" @click="s.page = 'dir'; s.open = null">👥 Microsoft Entra ID</button>
          <button :class="{ on: s.page === 'audit' }" @click="s.page = 'audit'; s.open = null">📜 Nhật ký hoạt động</button>
        </template>
      </nav>
      <div class="svc-work">
        <!-- Báo cáo đang mở -->
        <template v-if="s.page === 'report' && sv">
          <div v-if="sv.error" class="panel">{{ sv.error }}</div>
          <div v-else-if="sv.denied" class="panel deny">
            <h3>{{ sv.acc && !sv.acc.signIn ? 'Không đăng nhập được' : 'Bạn cần quyền truy cập' }}</h3>
            <p>{{ sv.acc.reason }}</p>
            <p v-if="sv.acc.signIn" class="muted">Trên Power BI thật, người dùng sẽ thấy nút “Request access” gửi yêu cầu tới chủ báo cáo.</p>
            <button @click="closeReport">Quay lại</button>
          </div>
          <template v-else>
            <div class="rep-head">
              <b>{{ sv.item.name }}</b><span class="label" :class="'lb' + NHAN_INDEX(svc.label)">🏷 {{ svc.label }}</span>
              <span class="grow"></span>
              <button @click="openAnalyze" :disabled="s.open.as === '__public__'">Export ▸ Analyze in Excel</button>
              <button v-if="isOwner || (sv.acc && sv.acc.reshare)" @click="openShare" :disabled="!!s.open.test || s.open.report !== 'main'">↗ Share</button>
              <button v-if="isOwner && !s.open.test" @click="publishToWeb(s.open.report)">File ▸ Embed ▸ Publish to web</button>
              <button @click="closeReport">✕ Đóng</button>
            </div>
            <div v-if="sv.banner" class="viewas-bar">{{ sv.banner }} <button v-if="s.open.test" @click="s.page = 'security'; s.open = null">Back to Row-Level Security</button></div>
            <div class="sim-info">
              <b>Thông tin mô phỏng</b> (Power BI thật không hiện khung này):
              <template v-if="s.open.as === '__public__'"> mã nhúng công khai, không RLS.</template>
              <template v-else-if="s.open.test"> Test as role chỉ mô phỏng bộ lọc, không kiểm tra người đó có quyền mở báo cáo hay không.</template>
              <template v-else> {{ s.open.as }} · {{ sv.acc.paths.join(' · ') }} ·
                <b>{{ sv.acc.bypass ? 'RLS KHÔNG áp dụng (' + sv.acc.ws + ')' : (sv.acc.roles.length ? 'RLS: ' + sv.acc.roles.join(' + ') : 'chưa thuộc role nào') }}</b>
                · Build: {{ sv.acc.build || sv.acc.bypass ? 'có' : 'không' }}</template>
            </div>
            <div class="svc-report">
              <rc-canvas :model="sv.item.model" :page="sv.page" :sec="sv.sec" :slicers="s.slicers" :editable="false" :selected-id="null" :service="true"
                @toggle="(v, x) => toggleSlicer(s.slicers, v, x)" @menu="visualMenu"></rc-canvas>
              <aside class="pane filters-read" v-if="sv.page.filters.some(f => !f.hidden)">
                <h4>Filters</h4>
                <div v-for="(f, i) in sv.page.filters.filter(f => !f.hidden)" :key="i" class="filter">
                  <b>{{ f.field }}</b> <span v-if="f.locked">🔒</span>
                  <div class="muted">{{ f.values.length ? f.values.join(', ') : 'Tất cả' }}</div>
                </div>
              </aside>
            </div>
            <div class="pages">
              <button v-for="(p, i) in sv.item.report.pages" :key="i" :class="{ on: s.open.page === i }" @click="s.open.page = i">{{ p.name }}</button>
            </div>
          </template>
        </template>

        <!-- Trang chủ -->
        <div v-else-if="s.page === 'home' || !isOwner" class="panel">
          <template v-if="svc.signedIn === '__public__'">
            <h3>Người ngoài internet</h3>
            <p>Không có tài khoản trong tổ chức. Chỉ mở được những gì đã bị đưa ra công khai bằng Publish to web.</p>
            <div v-if="!svc.embeds.length" class="muted">Không có mã nhúng công khai nào.</div>
            <div v-for="e in svc.embeds" :key="e.id" class="item-row"><span>🌐 {{ e.url }}</span><button @click="openReport(e.report, '__public__')">Mở liên kết</button></div>
          </template>
          <template v-else>
            <h3>Xin chào, {{ signedInUser.name }}</h3>
            <p class="muted">{{ signedInUser.note }}</p>
            <div v-if="!myAccess.signIn" class="deny">{{ myAccess.reason }}</div>
            <template v-else>
              <div v-if="!svc.model" class="muted">Chưa có báo cáo nào được publish. Publish từ Power BI Desktop trước.</div>
              <div v-for="x in reachable()" :key="x.id" class="item-row"><span>📊 <b>{{ x.name }}</b> <small class="muted">{{ x.how }}</small></span>
                <button @click="openReport(x.id)">Mở báo cáo</button></div>
              <p v-if="!isOwner" class="muted small">Muốn thử tài khoản khác? Đổi ở ô “Đang đăng nhập” phía trên. Kết quả tự ghi vào ma trận kiểm thử.</p>
            </template>
          </template>
        </div>

        <!-- Workspace -->
        <div v-else-if="s.page === 'workspace'" class="panel">
          <h3>▣ {{ svc.workspace.name }}</h3>
          <div v-if="!svc.model" class="deny">Chưa publish. Quay lại Desktop → Home → Publish.</div>
          <table class="grid list" v-else>
            <thead><tr><th>Tên</th><th>Loại</th><th>Ghi chú</th><th></th></tr></thead>
            <tbody>
              <tr><td>📊 {{ reportName }}</td><td>Report</td><td>Publish {{ svc.publishedAt }}<span v-if="dirty" class="tag">Desktop có thay đổi chưa publish</span></td>
                <td class="acts"><button @click="openReport('main')">Mở</button><button @click="openShare">Share</button>
                  <button @click="publishToWeb('main')">Publish to web</button><button @click="open('label', {})">Nhãn độ nhạy</button></td></tr>
              <tr><td>🗄 {{ reportName }}</td><td>Semantic model</td><td>{{ svc.model.roles.length }} role RLS</td>
                <td class="acts"><button @click="s.page = 'security'">Security</button><button @click="s.page = 'perm'">Manage permissions</button></td></tr>
              <template v-for="x in svc.extra" :key="x.id">
                <tr><td>📊 {{ x.name }}</td><td>Report</td><td>{{ x.note }}</td>
                  <td class="acts"><button @click="openReport(x.id)">Mở</button><button @click="publishToWeb(x.id)">Publish to web</button><button class="danger" @click="deleteExtra(x)">Xóa</button></td></tr>
                <tr><td>🗄 {{ x.name }}</td><td>Semantic model</td><td>{{ x.model.roles.length ? x.model.roles.length + ' role RLS' : 'Không có RLS' }}</td><td></td></tr>
              </template>
            </tbody>
          </table>

          <div class="cols2">
            <div class="box">
              <h4>Manage access (vai trò workspace)</h4>
              <p class="muted small">Admin, Member, Contributor có quyền sửa nội dung và <b>không bị RLS giới hạn</b>. Người chỉ cần xem: Viewer hoặc App.</p>
              <div v-for="a in svc.workspace.access" :key="a.principal" class="item-row">
                <span>{{ userName(a.principal) }}</span>
                <select v-model="a.role" @change="audit('UpdateWorkspaceAccess', svc.workspace.name, a.principal + ' = ' + a.role)"><option v-for="r in WS_ROLES" :key="r">{{ r }}</option></select>
                <button class="icon" @click="removeAccess(a)" title="Gỡ">✕</button>
              </div>
              <div class="add-row"><select v-model="dlgPick.ws"><option value="">+ người hoặc nhóm</option><option v-for="p in principals" :key="p" :value="p">{{ userName(p) }}</option></select>
                <select v-model="dlgPick.wsRole"><option v-for="r in WS_ROLES" :key="r">{{ r }}</option></select>
                <button @click="addAccess(dlgPick.ws, dlgPick.wsRole); dlgPick.ws = ''">Thêm</button></div>
            </div>
            <div class="box">
              <h4>App</h4>
              <label><input type="checkbox" v-model="svc.app.published" @change="audit('UpdateApp', 'App', svc.app.published ? 'Publish app' : 'Gỡ app')"> App đã publish</label>
              <div class="muted small">Đối tượng xem (audience):</div>
              <span v-for="(p, i) in svc.app.audience" :key="p" class="chip">{{ p }} <button @click="svc.app.audience.splice(i, 1); audit('UpdateApp', 'App', 'Bỏ người xem: ' + p)">✕</button></span>
              <div class="add-row"><select @change="addAudience($event.target.value); $event.target.value = ''"><option value="">+ người hoặc nhóm</option><option v-for="p in principals" :key="p" :value="p">{{ userName(p) }}</option></select></div>
              <label><input type="checkbox" v-model="svc.app.allowBuild"> Cho phép tạo nội dung từ semantic model (Build)</label>
              <label><input type="checkbox" v-model="svc.app.allowReshare"> Cho phép chia sẻ lại</label>
              <h4>Liên kết chia sẻ báo cáo</h4>
              <div v-if="!svc.shares.length" class="muted">Chưa có.</div>
              <div v-for="sh in svc.shares" :key="sh.id" class="item-row"><span>{{ shareLabel(sh) }} <small class="muted">– {{ sh.by }}, {{ sh.at }}</small></span>
                <button class="icon" @click="removeShare(sh)" title="Xóa liên kết">✕</button></div>
            </div>
          </div>
        </div>

        <!-- Security -->
        <div v-else-if="s.page === 'security'" class="panel">
          <h3>🛡 Row-Level Security – {{ reportName }}</h3>
          <div v-if="!svc.model" class="deny">Chưa publish.</div>
          <template v-else>
            <p class="muted small">Gán người hoặc nhóm bảo mật vào role. Quy tắc lọc sửa trên Desktop (Manage roles) rồi publish lại. Người không thuộc role nào sẽ không thấy dữ liệu.</p>
            <div v-if="!svc.model.roles.length" class="deny">Mô hình chưa có role nào.</div>
            <div class="cols2">
              <div v-for="r in svc.model.roles" :key="r.name" class="box">
                <h4>{{ r.name }} <small>({{ (svc.security[r.name] || []).length }})</small></h4>
                <div class="rule" v-for="(e, t) in r.filters" :key="t"><b>{{ t }}</b>: <code>{{ e }}</code></div>
                <div v-for="p in (svc.security[r.name] || [])" :key="p" class="item-row"><span>{{ userName(p) }}</span><button class="icon" @click="removeMember(r.name, p)">✕</button></div>
                <div class="add-row"><select @change="addMember(r.name, $event.target.value); $event.target.value = ''"><option value="">+ thêm người hoặc nhóm</option><option v-for="p in principals" :key="p" :value="p">{{ userName(p) }}</option></select></div>
              </div>
            </div>
            <div class="box">
              <h4>Test as role</h4>
              <label v-for="r in svc.model.roles" :key="r.name" class="inline"><input type="checkbox" :value="r.name" v-model="s.testPick.roles"> {{ r.name }}</label>
              <label>Xem dưới tên người cụ thể (tùy chọn) <input v-model="s.testPick.upn" list="upns" placeholder="email người dùng"></label>
              <datalist id="upns"><option v-for="u in svc.directory.users" :key="u.upn" :value="u.upn"></option></datalist>
              <button @click="testAs">Test as role</button>
              <p class="muted small">Test as role chỉ thử bộ lọc dữ liệu. Muốn biết người đó có mở được báo cáo không, có bị Member/Contributor “vượt” RLS không, phải đăng nhập thử bằng chính tài khoản đó.</p>
            </div>
          </template>
        </div>

        <!-- Manage permissions -->
        <div v-else-if="s.page === 'perm'" class="panel">
          <h3>🔑 Manage permissions – semantic model {{ reportName }}</h3>
          <p class="muted small">Ai đang có quyền đọc báo cáo/mô hình và nhờ đường nào. Danh sách này chưa cho biết họ thấy những dòng nào: phải kiểm thử RLS.</p>
          <table class="grid list"><thead><tr><th>Người dùng</th><th>Đường truy cập</th><th>Quyền</th></tr></thead>
            <tbody><tr v-for="x in permissionsList" :key="x.u.upn"><td>{{ x.u.name }}<br><small class="muted">{{ x.u.upn }}</small></td><td>{{ x.a.paths.join(' · ') }}</td>
              <td>Read{{ x.a.reshare ? ', Reshare' : '' }}{{ x.a.build || x.a.bypass ? ', Build' : '' }}{{ x.a.bypass ? ', Write' : '' }}</td></tr></tbody></table>
        </div>

        <!-- Admin -->
        <div v-else-if="s.page === 'admin'" class="panel">
          <h3>⚙ Admin portal – Tenant settings</h3>
          <label><input type="checkbox" v-model="svc.tenant.publishToWeb" @change="audit('UpdateTenantSetting', 'Publish to web', String(svc.tenant.publishToWeb))"> Publish to web</label>
          <label><input type="checkbox" v-model="svc.tenant.exportSummarized" @change="audit('UpdateTenantSetting', 'Export summarized data', String(svc.tenant.exportSummarized))"> Cho xuất dữ liệu tóm tắt (summarized) ra Excel/CSV</label>
          <label><input type="checkbox" v-model="svc.tenant.exportUnderlying" @change="audit('UpdateTenantSetting', 'Export underlying data', String(svc.tenant.exportUnderlying))"> Cho xuất dữ liệu gốc (underlying data)</label>
          <h4>Embed codes (Publish to web)</h4>
          <div v-if="!svc.embeds.length" class="muted">Không có mã nhúng.</div>
          <table class="grid list" v-else><thead><tr><th>Báo cáo</th><th>Người tạo</th><th>Lúc</th><th>Liên kết</th><th></th></tr></thead>
            <tbody><tr v-for="e in svc.embeds" :key="e.id"><td>{{ embedName(e) }}</td><td>{{ e.by }}</td><td>{{ e.at }}</td><td><small>{{ e.url }}</small></td>
              <td><button class="danger" @click="deleteEmbed(e)">Xóa mã nhúng</button></td></tr></tbody></table>
        </div>

        <!-- Thư mục người dùng -->
        <div v-else-if="s.page === 'dir'" class="panel">
          <h3>👥 Microsoft Entra ID (mô phỏng)</h3>
          <table class="grid list"><thead><tr><th>Người dùng</th><th>Ai cần thấy gì (ghi chú nghiệp vụ)</th><th>Trạng thái</th></tr></thead>
            <tbody><tr v-for="u in svc.directory.users" :key="u.upn"><td><b>{{ u.name }}</b><br><small>{{ u.upn }}</small>{{ u.internal ? '' : ' · khách ngoài' }}</td><td>{{ u.note }}</td>
              <td><button @click="toggleUser(u)" :class="u.status === 'active' ? '' : 'danger'">{{ u.status === 'active' ? 'Đang hoạt động' : 'Đã khóa' }}</button></td></tr></tbody></table>
          <h4>Nhóm bảo mật</h4>
          <div class="cols2">
            <div v-for="g in svc.directory.groups" :key="g.name" class="box">
              <b>{{ g.name }}</b> <small class="muted">{{ g.note }}</small>
              <div v-if="g.dynamic" class="muted small">Nhóm động – tự gồm mọi tài khoản nội bộ đang hoạt động.</div>
              <template v-else>
                <span v-for="p in g.members" :key="p" class="chip">{{ p }} <button @click="groupRemove(g, p)">✕</button></span>
                <div class="add-row"><select @change="groupAdd(g, $event.target.value); $event.target.value = ''"><option value="">+ thành viên</option><option v-for="p in principals" :key="p" :value="p">{{ p }}</option></select></div>
              </template>
            </div>
          </div>
        </div>

        <!-- Nhật ký -->
        <div v-else-if="s.page === 'audit'" class="panel">
          <h3>📜 Nhật ký hoạt động (Activity log)</h3>
          <table class="grid list"><thead><tr><th>Thời điểm</th><th>Tài khoản</th><th>Hoạt động</th><th>Đối tượng</th><th>Chi tiết</th></tr></thead>
            <tbody><tr v-for="(a, i) in svc.audit.slice().reverse()" :key="i"><td>{{ a.at }}</td><td>{{ a.user }}</td><td>{{ a.action }}</td><td>{{ a.item }}</td><td>{{ a.detail }}</td></tr></tbody></table>
        </div>
      </div>
    </div>
  </section>
  </main>

  <!-- ================= ĐỀ BÀI ================= -->
  <aside v-if="baiOpen" class="bai">
    <h3>{{ baiTitle }}</h3>
    <p>{{ bai.intro }}</p>
    <ol><li v-for="(st, i) in bai.steps" :key="i">{{ st }}</li></ol>
    <template v-if="bai.data">
      <h4>Dữ liệu để dán (Enter data)</h4>
      <div v-for="n in ['DimDonVi', 'DimNgay', 'FactDien']" :key="n" class="datablock">
        <div class="frow"><b>{{ n }}</b><button @click="copyData(n)">Chép</button></div><pre>{{ D.ENTER_DATA[n] }}</pre>
      </div>
    </template>
    <template v-if="checks.length">
      <h4>Tự kiểm tra ({{ checks.filter(c => c[1]).length }}/{{ checks.length }})</h4>
      <ul class="checks"><li v-for="(c, i) in checks" :key="i" :class="{ ok: c[1] }">{{ c[1] ? '✔' : '○' }} {{ c[0] }}</li></ul>
    </template>
    <h4>Nộp bài</h4>
    <p class="small">Tự kiểm tra chỉ xác nhận thao tác. Bài nộp vẫn cần số liệu và giải thích của bạn.</p>
    <button @click="copyResult">Chép kết quả để dán vào bài nộp</button>
    <p class="small muted">Bài làm trên mô phỏng tự lưu trong trình duyệt này. Ở bài nộp, chọn trạng thái “Đã chạy / đã thao tác” và ghi rõ làm trên phòng thí nghiệm mô phỏng.</p>
  </aside>
  </div>

  <!-- ================= MA TRẬN KIỂM THỬ ================= -->
  <section v-if="matrixOpen" class="matrix">
    <div class="frow"><h3>🧪 Ma trận kiểm thử (mẫu C8)</h3><span class="grow"></span>
      <button @click="copyMatrix">Chép (TSV)</button><button @click="downloadMatrix">Tải CSV</button>
      <button class="danger" @click="tests.splice(0)">Xóa hết</button><button @click="matrixOpen = false">✕</button></div>
    <p class="small muted">Mỗi lần View as (Desktop), Test as role hoặc đăng nhập mở báo cáo (service) tự ghi một dòng. Bạn điền cột Kỳ vọng và Đạt.</p>
    <div class="tbl-wrap"><table class="grid">
      <thead><tr><th>#</th><th>Môi trường</th><th>Tài khoản / danh tính</th><th>Vai trò truy cập</th><th>Role RLS</th><th>Đơn vị thấy</th><th>Tổng kWh</th><th>Ghi chú</th><th>Kỳ vọng</th><th>Đạt?</th><th></th></tr></thead>
      <tbody><tr v-for="(t, i) in tests" :key="i" :class="{ bypass: t.bypass, deny: t.denied }">
        <td>{{ i + 1 }}</td><td>{{ t.env }}<br><small class="muted">{{ t.at }}</small></td><td>{{ t.who }}</td><td>{{ t.ws }}</td>
        <td>{{ t.bypass ? 'Không áp RLS' : (t.roles.join(', ') || '(không)') }}</td><td>{{ t.units }}</td><td class="num">{{ fmt(t.kwh) }}</td>
        <td><small>{{ t.note }}{{ t.relOff ? ' · quan hệ DimDonVi–FactDien đang tắt' : '' }}</small></td>
        <td><input v-model="t.expected" placeholder="VD: chỉ DV_A"></td>
        <td><select v-model="t.pass"><option value=""></option><option>Đạt</option><option>Không đạt</option></select></td>
        <td><button class="icon" @click="tests.splice(i, 1)">✕</button></td></tr>
        <tr v-if="!tests.length"><td colspan="11" class="muted">Chưa có lần kiểm thử nào.</td></tr></tbody>
    </table></div>
  </section>

  <!-- ================= HỘP THOẠI ================= -->
  <div v-if="dlg" class="modal-bg" @click.self="dlg = null">
    <div class="modal" :class="'m-' + dlg.kind">
      <template v-if="dlg.kind === 'enter'">
        <h3>Create Table (Enter data)</h3>
        <p class="small muted">Dán dữ liệu có dòng tiêu đề, các cột cách nhau bằng phím Tab (chép từ Excel hoặc từ khối dữ liệu của đề).</p>
        <textarea v-model="dlg.text" rows="8" placeholder="MaDonVi	TenDonVi&#10;DV_A	Dien luc A"></textarea>
        <div v-if="enterPreview()" class="tbl-wrap"><table class="grid"><thead><tr><th v-for="h in enterPreview().head" :key="h">{{ h }}</th></tr></thead>
          <tbody><tr v-for="(r, i) in enterPreview().rows.slice(0, 5)" :key="i"><td v-for="(c, j) in r" :key="j">{{ c }}</td></tr></tbody></table></div>
        <label>Name <input v-model="dlg.name"></label>
        <div v-if="dlg.err" class="ferr">{{ dlg.err }}</div>
        <div class="mbtns"><button class="ok" @click="loadEnter">Load</button><button @click="dlg = null">Cancel</button></div>
      </template>

      <template v-else-if="dlg.kind === 'pq'">
        <h3>Power Query Editor</h3>
        <label>Query <select v-model="dlg.table"><option v-for="t in model.tables" :key="t.name">{{ t.name }}</option></select></label>
        <div class="cols2">
          <div>
            <h4>Cột</h4>
            <div v-for="c in pqCols()" :key="c.name" class="item-row"><span>{{ c.name }} <small class="muted">{{ c.type }}</small></span>
              <span><button @click="pqStep('mask', c.name)" title="Thay giá trị bằng dạng che, ví dụ 090****101">Che giá trị</button>
              <button class="danger" @click="pqStep('remove', c.name)">Remove column</button></span></div>
            <p class="small muted">Che hoặc bỏ cột ở đây xảy ra <b>trước khi nạp</b>: giá trị gốc không vào mô hình, không xuất được (masking tĩnh, giảm dữ liệu – buổi 6).</p>
          </div>
          <div>
            <h4>Applied steps</h4>
            <div class="item-row"><span>Source</span></div>
            <div v-for="(st, i) in pqTable().steps" :key="i" class="item-row"><span>{{ stepLabel(st) }}</span><button class="icon" @click="pqTable().steps.splice(i, 1)">✕</button></div>
          </div>
        </div>
        <div class="tbl-wrap"><table class="grid"><thead><tr><th v-for="c in E.materialize(model).tables[dlg.table].cols" :key="c">{{ c }}</th></tr></thead>
          <tbody><tr v-for="r in pqRows()" :key="r.__id"><td v-for="c in E.materialize(model).tables[dlg.table].cols" :key="c">{{ fmt(r[c]) }}</td></tr></tbody></table></div>
        <div class="mbtns"><button class="ok" @click="dlg = null">Close &amp; Apply</button></div>
      </template>

      <template v-else-if="dlg.kind === 'roles'">
        <h3>Manage security roles</h3>
        <div class="roles-ui">
          <div class="rcol">
            <b>Roles</b>
            <div v-for="r in dlg.roles" :key="r.name" class="pick" :class="{ on: dlg.role === r.name }" @click="dlg.role = r.name; dlg.newName = r.name; dlg.msg = dlg.err = ''">{{ r.name }}</div>
            <button @click="roleCreate">+ Create</button>
            <template v-if="roleSel()">
              <label>Tên role <input v-model="dlg.newName" @change="roleRename"></label>
              <button class="danger" @click="roleDelete">Delete</button>
            </template>
          </div>
          <div class="rcol">
            <b>Tables</b>
            <div v-for="t in model.tables" :key="t.name" class="pick" :class="{ on: dlg.table === t.name, has: roleSel() && (roleSel().filters[t.name] || '').trim() }" @click="dlg.table = t.name; dlg.msg = dlg.err = ''">{{ t.name }}</div>
          </div>
          <div class="rcol grow">
            <template v-if="roleSel()">
              <b>Filter data (DAX) – bảng {{ dlg.table }}</b>
              <textarea v-model="roleSel().filters[dlg.table]" rows="6" spellcheck="false" placeholder='[MaDonVi] = "DV_A"'></textarea>
              <label>Thử với USERPRINCIPALNAME() = <input v-model="dlg.testUpn" :placeholder="owner"></label>
              <button @click="roleCheck">✓ Kiểm tra biểu thức</button>
              <div v-if="dlg.err" class="ferr">{{ dlg.err }}</div><div v-if="dlg.msg" class="okmsg">{{ dlg.msg }}</div>
              <details class="ols"><summary>Bảo mật cấp đối tượng (OLS) cho bảng này</summary>
                <p class="small muted">Trên Power BI thật, OLS thường cấu hình bằng công cụ ngoài (Tabular Editor). Cột đặt “None” sẽ biến mất với role này; hình ảnh dùng cột đó báo lỗi.</p>
                <div v-for="c in olsCols()" :key="c.name" class="item-row"><span>{{ c.name }}</span>
                  <select :value="roleSel().ols[dlg.table + '[' + c.name + ']'] || 'Default'" @change="setOls(dlg.table + '[' + c.name + ']', $event.target.value)">
                    <option>Default</option><option>None</option></select></div>
              </details>
            </template>
            <div v-else class="muted">Tạo một role để bắt đầu.</div>
          </div>
        </div>
        <div class="mbtns"><button class="ok" @click="roleSave">Save</button><button @click="dlg = null">Cancel</button></div>
      </template>

      <template v-else-if="dlg.kind === 'viewas'">
        <h3>View as roles</h3>
        <label><input type="checkbox" v-model="dlg.other"> Other user</label>
        <input v-if="dlg.other" v-model="dlg.upn" list="upns-d" placeholder="email cần thử, VD minh.kehoach@minhan.example">
        <datalist id="upns-d"><option v-for="u in svc.directory.users" :key="u.upn" :value="u.upn"></option></datalist>
        <label v-for="r in model.roles" :key="r.name"><input type="checkbox" :value="r.name" v-model="dlg.roles"> {{ r.name }}</label>
        <p class="small muted">Desktop chỉ lọc theo role bạn đánh dấu. Desktop không biết ai là Member của workspace, ai đã được gán role trên service.</p>
        <div class="mbtns"><button class="ok" @click="applyViewAs">OK</button><button @click="dlg = null">Cancel</button></div>
      </template>

      <template v-else-if="dlg.kind === 'rels'">
        <h3>Manage relationships</h3>
        <div v-for="r in model.relationships" :key="r.id" class="item-row"><span><input type="checkbox" v-model="r.active" title="Active"> {{ relLabel(r) }} · {{ r.cross }}</span><button class="danger" @click="relDelete(r)">Delete</button></div>
        <h4>New relationship</h4>
        <div class="cols2">
          <div><label>Bảng (phía một) <select v-model="dlg.from" @change="dlg.fromCol = ''"><option value=""></option><option v-for="t in model.tables" :key="t.name">{{ t.name }}</option></select></label>
            <label>Cột <select v-model="dlg.fromCol"><option value=""></option><option v-for="c in colsOf(dlg.from)" :key="c">{{ c }}</option></select></label></div>
          <div><label>Bảng (phía nhiều) <select v-model="dlg.to" @change="dlg.toCol = ''"><option value=""></option><option v-for="t in model.tables" :key="t.name">{{ t.name }}</option></select></label>
            <label>Cột <select v-model="dlg.toCol"><option value=""></option><option v-for="c in colsOf(dlg.to)" :key="c">{{ c }}</option></select></label></div>
        </div>
        <div v-if="dlg.err" class="ferr">{{ dlg.err }}</div><div v-if="dlg.msg" class="okmsg">{{ dlg.msg }}</div>
        <div class="mbtns"><button @click="relCheck" :disabled="!dlg.fromCol || !dlg.toCol">Kiểm tra</button><button class="ok" @click="relCreate" :disabled="!dlg.fromCol || !dlg.toCol">Create</button><button @click="dlg = null">Close</button></div>
      </template>

      <template v-else-if="dlg.kind === 'share'">
        <h3>Send link</h3>
        <label><input type="radio" value="org" v-model="dlg.type"> Mọi người trong tổ chức có liên kết</label>
        <label><input type="radio" value="people" v-model="dlg.type"> Người cụ thể</label>
        <template v-if="dlg.type === 'people'">
          <span v-for="(p, i) in dlg.recipients" :key="p" class="chip">{{ p }} <button @click="dlg.recipients.splice(i, 1)">✕</button></span>
          <select @change="addTo(dlg.recipients, $event.target.value); $event.target.value = ''"><option value="">+ người nhận</option><option v-for="p in principals" :key="p" :value="p">{{ userName(p) }}</option></select>
        </template>
        <label><input type="checkbox" v-model="dlg.reshare"> Cho phép người nhận chia sẻ lại</label>
        <label><input type="checkbox" v-model="dlg.build"> Cho phép người nhận tạo nội dung từ dữ liệu (Build)</label>
        <p class="small muted">Người nhận vẫn chịu RLS nếu không phải Admin/Member/Contributor. Người không thuộc role nào sẽ thấy báo cáo trống.</p>
        <div class="mbtns"><button class="ok" @click="createShare">Tạo liên kết</button><button @click="dlg = null">Cancel</button></div>
      </template>

      <template v-else-if="dlg.kind === 'ptw'">
        <h3>Publish to web (public)</h3>
        <p class="deny">Bất kỳ ai trên internet có liên kết hoặc mã nhúng đều xem được báo cáo <b>{{ dlg.name }}</b> và toàn bộ dữ liệu của nó, không cần đăng nhập. Không có RLS, không có nhật ký người xem.</p>
        <div class="mbtns"><button class="danger" @click="confirmPtw">Tạo mã nhúng</button><button @click="dlg = null">Cancel</button></div>
      </template>

      <template v-else-if="dlg.kind === 'export'">
        <h3>Export data</h3>
        <label><input type="radio" value="summarized" v-model="dlg.mode" :disabled="!dlg.can.summarized"> Summarized data (dữ liệu tóm tắt)</label>
        <label><input type="radio" value="underlying" v-model="dlg.mode" :disabled="!dlg.can.underlying"> Underlying data (dữ liệu gốc)
          <small v-if="!dlg.can.underlying" class="muted">– {{ svc.tenant.exportUnderlying ? 'cần quyền Build' : 'quản trị viên đã tắt' }}</small></label>
        <template v-if="exportData().error"><div class="ferr">{{ exportData().error }}</div></template>
        <template v-else>
          <div class="small muted">{{ exportData().note || '' }} Tên tệp: {{ sv.item.name }} [{{ svc.label }}].csv</div>
          <div class="tbl-wrap"><table class="grid"><thead><tr><th v-for="h in exportData().headers" :key="h">{{ h }}</th></tr></thead>
            <tbody><tr v-for="(r, i) in exportData().rows.slice(0, 30)" :key="i"><td v-for="(c, j) in r" :key="j">{{ fmt(c) }}</td></tr></tbody></table></div>
        </template>
        <div class="mbtns"><button class="ok" @click="doExport" :disabled="!dlg.can.summarized && dlg.mode === 'summarized'">Export</button><button @click="dlg = null">Close</button></div>
      </template>

      <template v-else-if="dlg.kind === 'analyze'">
        <h3>Analyze in Excel (PivotTable Fields)</h3>
        <p class="small muted">Excel kết nối thẳng tới semantic model bằng danh tính của bạn: thấy mọi bảng, cả bảng và cột “ẩn khỏi báo cáo”. RLS và OLS vẫn áp dụng.</p>
        <label>Bảng <select v-model="dlg.table"><option v-for="t in sv.item.model.tables" :key="t.name" :value="t.name">{{ t.name }}{{ t.hidden ? ' (ẩn trong báo cáo)' : '' }}</option></select></label>
        <div class="small">{{ analyzeData().total }} dòng<span v-if="analyzeData().hiddenCols.length"> · cột ẩn trong báo cáo: {{ analyzeData().hiddenCols.join(', ') }}</span></div>
        <div class="tbl-wrap"><table class="grid"><thead><tr><th v-for="c in analyzeData().cols" :key="c">{{ c }}</th></tr></thead>
          <tbody><tr v-for="r in analyzeData().rows" :key="r.__id"><td v-for="c in analyzeData().cols" :key="c">{{ fmt(r[c]) }}</td></tr></tbody></table></div>
        <div class="mbtns"><button @click="dlg = null">Close</button></div>
      </template>

      <template v-else-if="dlg.kind === 'label'">
        <h3>Sensitivity label</h3>
        <p class="small muted">Nhãn theo mô hình 4 mức của buổi 1. Nhãn đi theo tệp khi xuất dữ liệu.</p>
        <label v-for="n in NHAN" :key="n"><input type="radio" :value="n" v-model="svc.label" @change="audit('SetSensitivityLabel', reportName, n)"> {{ n }}</label>
        <div class="mbtns"><button class="ok" @click="dlg = null">Close</button></div>
      </template>

      <template v-else-if="dlg.kind === 'msg'">
        <h3>{{ dlg.title }}</h3><p>{{ dlg.text }}</p>
        <div class="mbtns"><button class="ok" @click="dlg = null">OK</button></div>
      </template>
    </div>
  </div>
  <div v-if="toast" class="toast" role="status">{{ toast }}</div>
</div>`
  }).mixin({
    data() { return { dlgPick: { ws: '', wsRole: 'Viewer' } }; },
    computed: { NHAN: () => NHAN, WS_ROLES: () => WS_ROLES, D: () => D, E: () => E },
    methods: { NHAN_INDEX: n => NHAN.indexOf(n) }
  }).mount('#app');
})();
