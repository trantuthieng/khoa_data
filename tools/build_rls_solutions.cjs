// Dựng bài mẫu hoàn chỉnh cho phòng thí nghiệm RLS: chạy chính mô phỏng, làm từng bài bằng các thao tác của giao diện,
// rồi lưu trạng thái (mô hình, báo cáo, service, ma trận kiểm thử) vào app/answer_keys/rls_solutions/<bài>.json.
// Giảng viên mở bằng ?dapan=1; tệp chỉ phát qua /api/t/labs/rls/<bài>.
//
// Chạy: NODE_PATH=<thư mục node_modules có playwright> node tools/build_rls_solutions.cjs
// Cần Python (để phục vụ tệp tĩnh) và Microsoft Edge.
const { chromium } = require('playwright');
const { spawn } = require('node:child_process');
const fs = require('node:fs');
const path = require('node:path');

const ROOT = path.resolve(__dirname, '..');
const OUT = path.join(ROOT, 'app', 'answer_keys', 'rls_solutions');
const PORT = 8823;
const VM = "document.querySelector('#app').__vue_app__._container._vnode.component.proxy";
const wait = ms => new Promise(r => setTimeout(r, ms));

const DYN = 'NguoiXem';
const PQ_RULE = '[Email] = USERPRINCIPALNAME ()';

(async () => {
  const srv = spawn('python', ['-m', 'http.server', String(PORT)], { cwd: path.join(ROOT, 'app'), stdio: 'ignore' });
  await wait(1500);
  const browser = await chromium.launch({ headless: true, channel: 'msedge' });
  const pg = await browser.newPage({ viewport: { width: 1500, height: 950 } });
  const errors = [];
  pg.on('pageerror', e => errors.push(e.message));
  pg.on('dialog', d => d.accept());
  const ev = js => pg.evaluate(js);
  const run = async js => { await ev(`(() => { const v = ${VM}, m = v.model, s = v.svc; ${js} })()`); await wait(120); };

  async function open(bai) {
    await pg.goto(`http://127.0.0.1:${PORT}/static/labs/rls/index.html?bai=${bai}`);
    await ev('localStorage.clear()');
    await pg.reload();
    await wait(400);
  }
  async function viewAs(roles, upn) {
    await run(`v.mode = 'desktop'; v.openViewAs(); v.dlg.roles = ${JSON.stringify(roles)}; v.dlg.other = ${!!upn}; v.dlg.upn = ${JSON.stringify(upn || '')}; v.applyViewAs();`);
    await run('v.stopViewAs();');
  }
  async function signIn(upn, report) {
    await run(`v.mode = 'service'; s.signedIn = ${JSON.stringify(upn)};`);
    await run(`v.openReport(${JSON.stringify(report || 'main')}${upn === '__public__' ? ", '__public__'" : ''});`);
  }
  async function publish() { await run('v.mode = "desktop"; v.publish(); v.dlg = null;'); }
  const visual = (type, props) => `v.addVisual('${type}'); Object.assign(v.dPage.visuals[v.dPage.visuals.length - 1], ${JSON.stringify(props)}); v.d.sel = null;`;
  const measure = (name, expr) => `m.measures.push({ name: '${name}', table: 'FactDien', expr: '${expr}' });`;
  async function slicer(field, values) {
    for (const x of values) await run(`const sl = v.dPage.visuals.find(z => z.type === 'slicer' && z.field === '${field}'); v.toggleSlicer(v.d.slicers, sl, '${x}');`);
  }

  const SOLVE = {
    async bi01() {
      for (const t of ['DimDonVi', 'DimNgay', 'FactDien'])
        await run(`v.openEnter(); v.dlg.name = '${t}'; v.dlg.text = RLSData.ENTER_DATA.${t}; v.loadEnter();`);
      await run(`for (const [t, c] of [['DimNgay', 'Ngay'], ['FactDien', 'Ngay']]) m.tables.find(x => x.name === t).columns.find(x => x.name === c).type = 'Date';
                 for (const c of ['MaKH', 'MaDonVi']) m.tables.find(x => x.name === 'FactDien').columns.find(x => x.name === c).type = 'Text';
                 m.tables.find(x => x.name === 'FactDien').columns.find(x => x.name === 'kWh').type = 'Whole number';`);
    },
    async bi02() {
      for (const [a, ac, b, bc] of [['DimDonVi', 'MaDonVi', 'FactDien', 'MaDonVi'], ['DimNgay', 'Ngay', 'FactDien', 'Ngay']])
        await run(`v.openRels(); Object.assign(v.dlg, { from: '${a}', fromCol: '${ac}', to: '${b}', toCol: '${bc}' }); v.relCreate(); v.dlg = null;`);
    },
    async bi03() {
      await run(measure('Tong kWh', 'SUM(FactDien[kWh])') + visual('card', { measure: 'Tong kWh' }) +
        visual('table', { fields: ['DimDonVi[MaDonVi]'], measures: ['Tong kWh'] }));
    },
    async bi04() {
      await run(measure('So KH', 'DISTINCTCOUNT(FactDien[MaKH])') + measure('So dong', 'COUNTROWS(FactDien)') +
        visual('card', { measure: 'So KH' }) + visual('card', { measure: 'So dong' }));
    },
    async bi05() {
      await run(visual('slicer', { field: 'DimDonVi[MaDonVi]' }));
      await slicer('DimDonVi[MaDonVi]', ['DV_A', 'DV_A']);
    },
    async bi06() {
      await run(`m.roles.push({ name: 'DonVi_A', filters: { DimDonVi: '[MaDonVi] = "DV_A"' }, ols: {} }, { name: 'DonVi_B', filters: { DimDonVi: '[MaDonVi] = "DV_B"' }, ols: {} });`);
      await viewAs(['DonVi_A']);
      await viewAs(['DonVi_B']);
    },
    async bi07() {
      const rel = `m.relationships.find(r => r.from === 'DimDonVi' && r.to === 'FactDien')`;
      await run(`${rel}.active = false;`);
      await viewAs(['DonVi_A']);
      await run(`${rel}.active = true;`);
      await viewAs(['DonVi_A']);
    },
    async bi08() { await viewAs(['DonVi_A', 'DonVi_B']); },
    async bi09() {
      await run(visual('slicer', { field: 'DimNgay[Ngay]' }));
      await slicer('DimNgay[Ngay]', ['2026-09-01', '2026-09-01', '2026-09-02', '2026-09-02']);
    },
    async bi10() {
      await publish();
      await run(`s.security.DonVi_A.push('nguoixem.a@lab.example'); s.security.DonVi_B.push('nguoixem.b@lab.example');
                 for (const p of ['nguoixem.a@lab.example', 'nguoixem.b@lab.example', 'khong.gan@lab.example']) s.workspace.access.push({ principal: p, role: 'Viewer' });
                 s.workspace.access.push({ principal: 'thanhvien@lab.example', role: 'Member' });`);
      for (const u of ['nguoixem.a@lab.example', 'nguoixem.b@lab.example', 'khong.gan@lab.example', 'thanhvien@lab.example']) await signIn(u);
    },
    async th8() {
      await run(`m.relationships = m.relationships.filter(r => r.from !== 'PhanQuyen' && r.to !== 'PhanQuyen');` +
        measure('Tong kWh', 'SUM ( FactDien[kWh] )') +
        measure('So KH binh quan thang', 'AVERAGEX ( VALUES ( DimThang[Thang] ), CALCULATE ( SUM ( FactDien[SoKH] ) ) )') +
        visual('slicer', { field: 'DimDonVi[TenDonVi]' }) + visual('card', { measure: 'Tong kWh' }) +
        visual('card', { measure: 'So KH binh quan thang' }) +
        visual('bar', { fields: ['DimDonVi[TenDonVi]'], measures: ['Tong kWh'] }) +
        visual('table', { fields: ['FactDien[Phuong]', 'FactDien[Thang]'], measures: ['Tong kWh'], w: 12 }) +
        `m.roles.push({ name: 'DonVi_A', filters: { DimDonVi: '[MaDonVi] = "DV_A"' }, ols: {} },
                      { name: 'DonVi_B', filters: { DimDonVi: '[MaDonVi] = "DV_B"' }, ols: {} },
                      { name: '${DYN}', filters: { DimDonVi: RLSData.DYN_RULE, PhanQuyen: '${PQ_RULE}' }, ols: {} });
         m.tables.find(t => t.name === 'PhanQuyen').hidden = true;`);
      await viewAs(['DonVi_A']);
      await viewAs(['DonVi_B']);
      for (const u of ['minh.kehoach@minhan.example', 'ha.kehoach@dly.example', 'moi.vao@dlx.example']) await viewAs([DYN], u);
      await publish();
      const viewers = ['tuan.truongphong@dlx.example', 'truongphong@dly.example', 'minh.kehoach@minhan.example', 'ha.kehoach@dly.example'];
      await run(`for (const p of ${JSON.stringify(viewers)}) s.security.${DYN}.push(p);
                 for (const p of ${JSON.stringify(viewers.concat(['khong.gan@dlx.example']))}) s.workspace.access.push({ principal: p, role: 'Viewer' });
                 s.workspace.access.push({ principal: 'bientap.a@dlx.example', role: 'Member' });`);
      for (const u of viewers.concat(['khong.gan@dlx.example', 'bientap.a@dlx.example'])) await signIn(u);
      // Lỗi chị Hà: xóa dòng quyền cũ, publish lại, thử lại. Gỡ bientap.a khỏi Member sau khi đã tái hiện lỗi.
      await run(`s.signedIn = s.owner; const pq = m.tables.find(t => t.name === 'PhanQuyen');
                 pq.source = pq.source.filter(r => !(r.Email === 'ha.kehoach@dly.example' && r.MaDonVi === 'DV_A'));`);
      await publish();
      await signIn('ha.kehoach@dly.example');
      await run(`s.signedIn = s.owner; s.workspace.access = s.workspace.access.filter(a => a.principal !== 'bientap.a@dlx.example');`);
    },
    async rasoat() {
      const users = ['tuan.truongphong@dlx.example', 'truongphong@dly.example', 'minh.kehoach@minhan.example', 'ha.kehoach@dly.example',
        'moi.vao@dlx.example', 'nhanvien.baocao@dlx.example', 'lan.ketoan@dlx.example', 'baocao.chung@dlx.example',
        'an.nghiviec@dlx.example', 'nv.kythuat@dlx.example', 'doitac@doitac.example'];
      const sweep = async () => {
        for (const u of users) await signIn(u);
        for (const e of await ev(`${VM}.svc.embeds.map(e => e.report)`)) await signIn('__public__', e);
        await run('s.signedIn = s.owner;');
      };
      await sweep();
      await run(`
        m.roles = m.roles.filter(r => !['TatCa_TamThoi', 'DonVi_A', 'DonVi_B'].includes(r.name));
        m.roles.find(r => r.name === '${DYN}').filters.PhanQuyen = '${PQ_RULE}';
        const pq = m.tables.find(t => t.name === 'PhanQuyen');
        pq.hidden = true;
        pq.source = pq.source.filter(r => !(r.Email === 'ha.kehoach@dly.example' && r.MaDonVi === 'DV_A') &&
          !['baocao.chung@dlx.example', 'an.nghiviec@dlx.example'].includes(r.Email));
        pq.source.push({ Email: 'nhanvien.baocao@dlx.example', MaDonVi: 'DV_A' });
        v.report.pages.splice(1, 1);
        m.tables = m.tables.filter(t => t.name !== 'DSKhachHang');
        v.d.page = 0;`);
      await publish();
      await run(`
        s.shares.splice(0);
        s.workspace.access = s.workspace.access.filter(a => !['tuan.truongphong@dlx.example', 'an.nghiviec@dlx.example'].includes(a.principal));
        s.workspace.access.find(a => a.principal === 'nhanvien.baocao@dlx.example').role = 'Viewer';
        const g = s.directory.groups.find(g => g.name === 'NguoiXem_BaoCao');
        g.members = g.members.filter(x => !['baocao.chung@dlx.example', 'an.nghiviec@dlx.example'].includes(x));
        g.members.push('lan.ketoan@dlx.example', 'nhanvien.baocao@dlx.example');
        s.directory.users.find(u => u.upn === 'baocao.chung@dlx.example').status = 'disabled';
        s.embeds.splice(0); s.extra.splice(0);
        s.tenant.publishToWeb = false; s.tenant.exportUnderlying = false; s.label = 'Mật';`);
      await sweep();
    }
  };

  // Ai cần thấy gì theo nghiệp vụ: [mô tả, tổng kWh mong đợi; null = không thấy dữ liệu]
  const X = ['Chỉ Điện lực X', 826436], Y = ['Chỉ Điện lực Y', 742030], XY = ['Điện lực X và Y', 1568466], NONE = ['Không thấy dữ liệu', null];
  const NEED = {
    th8: { DonVi_A: X, DonVi_B: Y, 'tuan.truongphong@dlx.example': X, 'truongphong@dly.example': Y, 'minh.kehoach@minhan.example': XY,
      'ha.kehoach@dly.example': Y, 'moi.vao@dlx.example': NONE, 'khong.gan@dlx.example': NONE, 'bientap.a@dlx.example': X },
    bi: { DonVi_A: ['Chỉ DV_A', 560], DonVi_B: ['Chỉ DV_B', 810], 'DonVi_A+DonVi_B': ['DV_A và DV_B (hợp quyền)', 1370],
      'nguoixem.a@lab.example': ['Chỉ DV_A', 560], 'nguoixem.b@lab.example': ['Chỉ DV_B', 810], 'khong.gan@lab.example': ['Không thấy dữ liệu', null],
      'thanhvien@lab.example': ['Chỉ DV_A (theo nghiệp vụ)', 560] }
  };
  NEED.rasoat = Object.assign({}, NEED.th8, { 'nhanvien.baocao@dlx.example': X, 'lan.ketoan@dlx.example': X, 'baocao.chung@dlx.example': NONE,
    'an.nghiviec@dlx.example': NONE, 'nv.kythuat@dlx.example': NONE, 'doitac@doitac.example': NONE, 'Người ngoài internet': NONE });
  const fmtN = n => n.toLocaleString('vi-VN');
  function grade(bai, t) {
    const need = NEED[bai.startsWith('bi') ? 'bi' : bai];
    const key = t.upn && need[t.upn] ? t.upn : need[t.who] ? t.who : t.roles.join('+');
    const n = need[key];
    if (!n) return ['', '', ''];
    const ok = n[1] === null ? t.kwh === null : t.kwh === n[1];
    const why = ok || t.bypass ? '' : t.relOff ? 'quan hệ đang tắt' : 'thấy nhiều hơn quyền nghiệp vụ';
    return [n[0] + (n[1] === null ? '' : ': ' + fmtN(n[1])), ok ? 'Đạt' : 'Không đạt', why];
  }

  fs.mkdirSync(OUT, { recursive: true });
  let failed = 0;
  for (const [bai, solve] of Object.entries(SOLVE)) {
    await open(bai);
    await solve();
    const tests = await ev(`JSON.parse(JSON.stringify(${VM}.tests))`);
    const graded = tests.map(t => grade(bai, t));
    await run(`${JSON.stringify(graded)}.forEach(([e, p, w], i) => { const x = v.tests[i]; x.expected = e; x.pass = p; if (w) x.note = x.note ? x.note + ' · ' + w : w; });`);
    await run(`v.mode = '${bai === 'rasoat' ? 'service' : 'desktop'}'; s.signedIn = s.owner; v.d.viewAs = null; v.dlg = null; v.persist();`);
    const checks = await ev(`${VM}.checks.map(c => [c[0], !!c[1]])`);
    const bad = checks.filter(c => !c[1]);
    failed += bad.length;
    const state = await ev(`localStorage.getItem('rlslab:${bai}')`);
    fs.writeFileSync(path.join(OUT, `${bai}.json`), state + '\n');
    const n = await ev(`${VM}.tests.length`);
    console.log(`${bai}: ${checks.length - bad.length}/${checks.length} mục tự kiểm tra, ${n} dòng kiểm thử${bad.length ? ' – CHƯA ĐẠT: ' + bad.map(c => c[0]).join('; ') : ''}`);
  }
  await browser.close();
  srv.kill();
  if (errors.length) console.log('Lỗi trang:', errors);
  process.exit(failed || errors.length ? 1 : 0);
})();
