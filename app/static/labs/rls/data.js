/* Dữ liệu giả lập và các kịch bản của phòng thí nghiệm RLS (buổi 7).
   Số liệu khớp tools/beginner_labs.py (bài BI 01–10) và script Thực hành 8 (random.seed(8)). */
(function (global) {
  'use strict';

  // ---------- Bộ nhỏ theo ngày (BI 01–10) ----------
  const BI_DIMDONVI = [['DV_A', 'Dien luc A'], ['DV_B', 'Dien luc B'], ['DV_C', 'Dien luc C']];
  const BI_DIMNGAY = [['2026-09-01', '2026-09'], ['2026-09-02', '2026-09']];
  const BI_FACT = [
    ['KH001', 'DV_A', '2026-09-01', 100], ['KH002', 'DV_A', '2026-09-01', 150], ['KH003', 'DV_A', '2026-09-01', 200],
    ['KH004', 'DV_B', '2026-09-01', 250], ['KH005', 'DV_B', '2026-09-01', 300], ['KH006', 'DV_C', '2026-09-01', 400],
    ['KH001', 'DV_A', '2026-09-02', 110], ['KH004', 'DV_B', '2026-09-02', 260]];

  // ---------- Bộ Thực hành 8 theo tháng ----------
  const TH8_FACT = [
    ['DV_A', '2026-07', 'An Phú', 174, 64880], ['DV_A', '2026-08', 'An Phú', 174, 64155], ['DV_A', '2026-09', 'An Phú', 174, 64263],
    ['DV_A', '2026-07', 'Bình Minh', 148, 51014], ['DV_A', '2026-08', 'Bình Minh', 148, 50685], ['DV_A', '2026-09', 'Bình Minh', 148, 50969],
    ['DV_A', '2026-07', 'Đông Hòa', 130, 48196], ['DV_A', '2026-08', 'Đông Hòa', 130, 48635], ['DV_A', '2026-09', 'Đông Hòa', 130, 49228],
    ['DV_A', '2026-07', 'Phú Thượng', 121, 48921], ['DV_A', '2026-08', 'Phú Thượng', 121, 49329], ['DV_A', '2026-09', 'Phú Thượng', 121, 50321],
    ['DV_A', '2026-07', 'Tân Lập', 163, 61459], ['DV_A', '2026-08', 'Tân Lập', 163, 62147], ['DV_A', '2026-09', 'Tân Lập', 163, 62234],
    ['DV_B', '2026-07', 'Hòa Bình', 210, 71680], ['DV_B', '2026-08', 'Hòa Bình', 210, 79404], ['DV_B', '2026-09', 'Hòa Bình', 210, 70626],
    ['DV_B', '2026-07', 'Long Thạnh', 185, 67570], ['DV_B', '2026-08', 'Long Thạnh', 185, 61838], ['DV_B', '2026-09', 'Long Thạnh', 185, 63339],
    ['DV_B', '2026-07', 'Mỹ Lợi', 140, 53194], ['DV_B', '2026-08', 'Mỹ Lợi', 140, 47666], ['DV_B', '2026-09', 'Mỹ Lợi', 140, 50693],
    ['DV_B', '2026-07', 'Tân Phong', 166, 58591], ['DV_B', '2026-08', 'Tân Phong', 166, 58541], ['DV_B', '2026-09', 'Tân Phong', 166, 58888]];
  const TH8_PHANQUYEN = [
    ['tuan.truongphong@dlx.example', 'DV_A'], ['truongphong@dly.example', 'DV_B'],
    ['minh.kehoach@minhan.example', 'DV_A'], ['minh.kehoach@minhan.example', 'DV_B'],
    ['ha.kehoach@dly.example', 'DV_A'], ['ha.kehoach@dly.example', 'DV_B']];

  // Bảng khách hàng chi tiết chỉ có trong kịch bản rà soát (bị nạp "cho tiện tra cứu").
  const KH_CHI_TIET = [
    ['KH-A01', 'Khách mẫu A01', '0900000101', '000000000101', 'DV_A', 'An Phú', 1210],
    ['KH-A02', 'Khách mẫu A02', '0900000102', '000000000102', 'DV_A', 'An Phú', 980],
    ['KH-A03', 'Khách mẫu A03', '0900000103', '000000000103', 'DV_A', 'Bình Minh', 1475],
    ['KH-A04', 'Khách mẫu A04', '0900000104', '000000000104', 'DV_A', 'Đông Hòa', 860],
    ['KH-A05', 'Khách mẫu A05', '0900000105', '000000000105', 'DV_A', 'Phú Thượng', 1320],
    ['KH-A06', 'Khách mẫu A06', '0900000106', '000000000106', 'DV_A', 'Tân Lập', 1105],
    ['KH-B01', 'Khách mẫu B01', '0900000201', '000000000201', 'DV_B', 'Hòa Bình', 1540],
    ['KH-B02', 'Khách mẫu B02', '0900000202', '000000000202', 'DV_B', 'Hòa Bình', 1190],
    ['KH-B03', 'Khách mẫu B03', '0900000203', '000000000203', 'DV_B', 'Long Thạnh', 1015],
    ['KH-B04', 'Khách mẫu B04', '0900000204', '000000000204', 'DV_B', 'Mỹ Lợi', 1260],
    ['KH-B05', 'Khách mẫu B05', '0900000205', '000000000205', 'DV_B', 'Tân Phong', 935],
    ['KH-B06', 'Khách mẫu B06', '0900000206', '000000000206', 'DV_B', 'Tân Phong', 1380]];

  function table(name, cols, rows, extra) {
    return Object.assign({
      name, hidden: false,
      columns: cols.map(([n, type]) => ({ name: n, type, hidden: false })),
      source: rows.map(r => Object.fromEntries(cols.map(([n], i) => [n, r[i]]))),
      steps: []
    }, extra || {});
  }

  function rel(from, fromCol, to, toCol, extra) {
    return Object.assign({ id: `${from}.${fromCol}-${to}.${toCol}`, from, fromCol, to, toCol, active: true, cross: 'Single', secBoth: false }, extra || {});
  }

  // Dạng văn bản để dán vào Enter data (tab giữa các cột).
  function tsv(cols, rows) {
    return [cols.join('\t')].concat(rows.map(r => r.join('\t'))).join('\n');
  }

  const BI_TABLES = () => [
    table('DimDonVi', [['MaDonVi', 'Text'], ['TenDonVi', 'Text']], BI_DIMDONVI),
    table('DimNgay', [['Ngay', 'Date'], ['Thang', 'Text']], BI_DIMNGAY),
    table('FactDien', [['MaKH', 'Text'], ['MaDonVi', 'Text'], ['Ngay', 'Date'], ['kWh', 'Whole number']], BI_FACT)];

  const TH8_TABLES = () => [
    table('DimDonVi', [['MaDonVi', 'Text'], ['TenDonVi', 'Text']], [['DV_A', 'Điện lực X'], ['DV_B', 'Điện lực Y']]),
    table('DimThang', [['Thang', 'Text'], ['ThangSo', 'Whole number']], [['2026-07', 7], ['2026-08', 8], ['2026-09', 9]]),
    table('FactDien', [['MaDonVi', 'Text'], ['Thang', 'Text'], ['Phuong', 'Text'], ['SoKH', 'Whole number'], ['kWh', 'Whole number']], TH8_FACT),
    table('PhanQuyen', [['Email', 'Text'], ['MaDonVi', 'Text']], TH8_PHANQUYEN)];

  const ENTER_DATA = {
    DimDonVi: tsv(['MaDonVi', 'TenDonVi'], BI_DIMDONVI),
    DimNgay: tsv(['Ngay', 'Thang'], BI_DIMNGAY),
    FactDien: tsv(['MaKH', 'MaDonVi', 'Ngay', 'kWh'], BI_FACT)
  };

  const M_TONG = { name: 'Tong kWh', table: 'FactDien', expr: 'SUM(FactDien[kWh])' };
  const M_SOKH = { name: 'So KH', table: 'FactDien', expr: 'DISTINCTCOUNT(FactDien[MaKH])' };
  const M_SODONG = { name: 'So dong', table: 'FactDien', expr: 'COUNTROWS(FactDien)' };
  const M_SOKH_TH8 = { name: 'So KH binh quan thang', table: 'FactDien',
    expr: 'AVERAGEX ( VALUES ( DimThang[Thang] ), CALCULATE ( SUM ( FactDien[SoKH] ) ) )' };

  const ROLE_A = { name: 'DonVi_A', filters: { DimDonVi: '[MaDonVi] = "DV_A"' }, ols: {} };
  const ROLE_B = { name: 'DonVi_B', filters: { DimDonVi: '[MaDonVi] = "DV_B"' }, ols: {} };
  const DYN_RULE = '[MaDonVi] IN CALCULATETABLE (\n    VALUES ( PhanQuyen[MaDonVi] ),\n    PhanQuyen[Email] = USERPRINCIPALNAME ()\n)';

  let vid = 0;
  const V = (type, props, w) => Object.assign({ id: 'v' + (++vid), type, w: w || 4, fields: [], measures: [] }, props);
  const page = (name, visuals, filters) => ({ name, visuals: visuals || [], filters: filters || [] });

  function user(upn, name, note, extra) {
    return Object.assign({ upn, name, note: note || '', status: 'active', internal: true }, extra || {});
  }

  // Thư mục người dùng (mô phỏng Microsoft Entra ID) cho bộ BI nhỏ.
  function biDirectory() {
    return {
      users: [
        user('ban.hocvien@lab.example', 'Bạn (người làm báo cáo)', 'Chủ workspace thực hành – Admin.'),
        user('nguoixem.a@lab.example', 'Người xem A', 'Chỉ được xem Điện lực A.'),
        user('nguoixem.b@lab.example', 'Người xem B', 'Chỉ được xem Điện lực B.'),
        user('khong.gan@lab.example', 'Người chưa được cấp role', 'Có quyền mở báo cáo nhưng chưa gán role nào.'),
        user('thanhvien@lab.example', 'Đồng nghiệp làm báo cáo', 'Theo nghiệp vụ chỉ cần xem Điện lực A.')],
      groups: [{ name: 'Toan_Cong_Ty', dynamic: 'internal', members: [], note: 'Nhóm động: mọi tài khoản nội bộ.' }]
    };
  }

  function th8Directory() {
    return {
      users: [
        user('ban.lambaocao@minhan.example', 'Bạn – nhóm dữ liệu Công ty', 'Người làm báo cáo, Admin workspace.'),
        user('tuan.truongphong@dlx.example', 'Anh Tuấn', 'Trưởng phòng Kinh doanh Điện lực X. Chỉ xem Điện lực X.'),
        user('truongphong@dly.example', 'Trưởng phòng KD Điện lực Y', 'Chỉ xem Điện lực Y.'),
        user('minh.kehoach@minhan.example', 'Anh Minh', 'Phòng Kế hoạch Công ty. Xem cả hai điện lực.'),
        user('ha.kehoach@dly.example', 'Chị Hà', 'Đã chuyển từ Điện lực X sang Điện lực Y từ 01/09/2026. Chỉ xem Điện lực Y.'),
        user('moi.vao@dlx.example', 'Nhân viên mới', 'Mới vào, chưa được cấp quyền dữ liệu.'),
        user('khong.gan@dlx.example', 'Người chưa gán role', 'Được mở báo cáo nhưng chưa gán role RLS nào.'),
        user('bientap.a@dlx.example', 'Biên tập viên Điện lực X', 'Được nhờ chỉnh giao diện báo cáo.')],
      groups: [{ name: 'Toan_Cong_Ty', dynamic: 'internal', members: [], note: 'Nhóm động: mọi tài khoản nội bộ.' }]
    };
  }

  function emptyService(directory, owner) {
    return {
      model: null, report: null, publishedAt: null,
      directory, owner, signedIn: owner,
      workspace: { name: 'KinhDoanh – Báo cáo (thực hành)', access: [{ principal: owner, role: 'Admin' }] },
      security: {}, shares: [], app: { published: false, audience: [], allowBuild: false, allowReshare: false },
      embeds: [], extra: [],
      tenant: { exportSummarized: true, exportUnderlying: false, publishToWeb: true },
      label: 'Nội bộ', audit: []
    };
  }

  function desktop(tables, rels, measures, roles, pages) {
    return {
      model: { tables, relationships: rels || [], measures: measures || [], roles: roles || [] },
      report: { pages: pages || [page('Page 1')] }
    };
  }

  // ---------- Các kịch bản ----------
  function biBase(level) {
    vid = 0;
    const tables = level >= 2 ? BI_TABLES() : [];
    const rels = level >= 3 ? [rel('DimDonVi', 'MaDonVi', 'FactDien', 'MaDonVi'), rel('DimNgay', 'Ngay', 'FactDien', 'Ngay')] : [];
    const measures = [];
    const visuals = [];
    if (level >= 4) { measures.push({ ...M_TONG }); visuals.push(V('card', { title: 'Tong kWh', measure: 'Tong kWh' }, 3)); visuals.push(V('table', { fields: ['DimDonVi[MaDonVi]'], measures: ['Tong kWh'] }, 5)); }
    if (level >= 5) { measures.push({ ...M_SOKH }, { ...M_SODONG }); visuals.push(V('card', { measure: 'So KH' }, 2), V('card', { measure: 'So dong' }, 2)); }
    if (level >= 6) visuals.unshift(V('slicer', { field: 'DimDonVi[MaDonVi]' }, 3));
    const roles = level >= 7 ? [JSON.parse(JSON.stringify(ROLE_A)), JSON.parse(JSON.stringify(ROLE_B))] : [];
    return desktop(tables, rels, measures, roles, [page('Page 1', visuals)]);
  }

  function biScenario(level) {
    return { desktop: biBase(level), service: emptyService(biDirectory(), 'ban.hocvien@lab.example'), dataset: 'bi' };
  }

  function th8Scenario() {
    vid = 0;
    const d = desktop(TH8_TABLES(), [
      rel('DimDonVi', 'MaDonVi', 'FactDien', 'MaDonVi'),
      rel('DimThang', 'Thang', 'FactDien', 'Thang'),
      // Power BI tự phát hiện quan hệ khi nạp: đề yêu cầu không nối PhanQuyen.
      rel('DimDonVi', 'MaDonVi', 'PhanQuyen', 'MaDonVi', { auto: true })], [], [], [page('Page 1')]);
    return { desktop: d, service: emptyService(th8Directory(), 'ban.lambaocao@minhan.example'), dataset: 'th8' };
  }

  // Kịch bản "báo cáo đang vận hành": dựng sẵn, đã publish, cài sẵn nhiều lỗi phân quyền để rà soát.
  function auditScenario() {
    vid = 0;
    const tables = TH8_TABLES();
    tables.find(t => t.name === 'PhanQuyen').source.push(
      { Email: 'baocao.chung@dlx.example', MaDonVi: 'DV_A' }, { Email: 'baocao.chung@dlx.example', MaDonVi: 'DV_B' },
      { Email: 'an.nghiviec@dlx.example', MaDonVi: 'DV_A' }, { Email: 'lan.ketoan@dlx.example', MaDonVi: 'DV_A' });
    const kh = table('DSKhachHang', [['MaKH', 'Text'], ['HoTen', 'Text'], ['SoDienThoai', 'Text'], ['CCCD', 'Text'],
      ['MaDonVi', 'Text'], ['Phuong', 'Text'], ['kWh_Q3', 'Whole number']], KH_CHI_TIET);
    kh.columns.find(c => c.name === 'CCCD').hidden = true;
    kh.columns.push({ name: 'SDT_hien_thi', type: 'Text', hidden: false,
      calc: 'LEFT ( [SoDienThoai], 3 ) & "****" & RIGHT ( [SoDienThoai], 3 )' });
    tables.push(kh);
    const roles = [
      { name: 'NguoiXem', filters: { DimDonVi: DYN_RULE }, ols: {} },
      { name: 'DonVi_A', filters: { DimDonVi: '[MaDonVi] = "DV_A"' }, ols: {} },
      { name: 'DonVi_B', filters: { DimDonVi: '[MaDonVi] = "DV_B"' }, ols: {} },
      { name: 'TatCa_TamThoi', filters: { DimDonVi: 'TRUE ()' }, ols: {} }];
    const p1 = page('Sản lượng', [
      V('slicer', { field: 'DimDonVi[TenDonVi]' }, 3),
      V('card', { measure: 'Tong kWh' }, 3),
      V('card', { measure: 'So KH binh quan thang' }, 3),
      V('bar', { fields: ['DimDonVi[TenDonVi]'], measures: ['Tong kWh'] }, 3),
      V('table', { fields: ['FactDien[Phuong]', 'FactDien[Thang]'], measures: ['Tong kWh'] }, 12)]);
    const p2 = page('Tra cứu khách hàng', [
      V('table', { title: 'Khách hàng (số điện thoại đã che)', fields: ['DSKhachHang[MaKH]', 'DSKhachHang[HoTen]', 'DSKhachHang[SDT_hien_thi]', 'DSKhachHang[Phuong]', 'DSKhachHang[kWh_Q3]'] }, 12)]);
    const d = desktop(tables, [rel('DimDonVi', 'MaDonVi', 'FactDien', 'MaDonVi'), rel('DimThang', 'Thang', 'FactDien', 'Thang')],
      [{ ...M_TONG }, { ...M_SOKH_TH8 }], roles, [p1, p2]);

    const dir = th8Directory();
    dir.users = dir.users.filter(u => !['khong.gan@dlx.example', 'bientap.a@dlx.example'].includes(u.upn));
    dir.users.push(
      user('nhanvien.baocao@dlx.example', 'Nhân viên phòng KD Điện lực X', 'Chỉ cần xem số Điện lực X. Được thêm vào workspace “để sửa giúp tiêu đề”.'),
      user('lan.ketoan@dlx.example', 'Chị Lan (kế toán)', 'Kế toán tổng hợp Điện lực X. Chỉ cần số Điện lực X.'),
      user('baocao.chung@dlx.example', 'Tài khoản báo cáo chung', 'Tài khoản dùng chung của phòng KD, 5 người biết mật khẩu, không bật MFA.'),
      user('an.nghiviec@dlx.example', 'Anh An (đã nghỉ việc)', 'Nghỉ việc từ 15/09/2026. Tài khoản đã bị khóa.', { status: 'disabled' }),
      user('nv.kythuat@dlx.example', 'Nhân viên kỹ thuật', 'Không làm công việc kinh doanh, không cần số liệu.'),
      user('doitac@doitac.example', 'Đối tác bên ngoài', 'Khách (guest) của công ty phần mềm.', { internal: false }));
    dir.groups.push(
      { name: 'NguoiXem_BaoCao', members: ['tuan.truongphong@dlx.example', 'truongphong@dly.example', 'minh.kehoach@minhan.example',
        'ha.kehoach@dly.example', 'moi.vao@dlx.example', 'baocao.chung@dlx.example', 'an.nghiviec@dlx.example'], note: 'Người xem báo cáo sản lượng.' },
      { name: 'KT_TongHop', members: ['lan.ketoan@dlx.example'], note: 'Kế toán tổng hợp.' });
    const s = emptyService(dir, 'ban.lambaocao@minhan.example');
    s.workspace.access.push(
      { principal: 'tuan.truongphong@dlx.example', role: 'Member' },
      { principal: 'nhanvien.baocao@dlx.example', role: 'Contributor' },
      { principal: 'NguoiXem_BaoCao', role: 'Viewer' },
      { principal: 'an.nghiviec@dlx.example', role: 'Viewer' });
    s.security = { NguoiXem: ['NguoiXem_BaoCao'], DonVi_A: ['KT_TongHop'], DonVi_B: ['KT_TongHop'], TatCa_TamThoi: ['Toan_Cong_Ty'] };
    s.shares = [{ id: 'sh1', type: 'org', recipients: [], reshare: true, build: true, by: 'tuan.truongphong@dlx.example', at: '2026-08-20 09:12' }];
    s.app = { published: true, audience: ['NguoiXem_BaoCao'], allowBuild: false, allowReshare: false };
    s.tenant = { exportSummarized: true, exportUnderlying: true, publishToWeb: true };
    s.label = 'Công khai';
    s.audit = [
      { at: '2026-08-12 14:03', user: 'ban.lambaocao@minhan.example', action: 'CreateRole', item: 'TatCa_TamThoi', detail: 'Tạo role tạm để demo cho lãnh đạo, thêm nhóm Toan_Cong_Ty.' },
      { at: '2026-08-20 09:12', user: 'tuan.truongphong@dlx.example', action: 'ShareReport', item: 'SanLuong_Q3', detail: 'Liên kết: Mọi người trong tổ chức (chia sẻ lại, Build).' },
      { at: '2026-09-03 16:40', user: 'nhanvien.baocao@dlx.example', action: 'PublishToWebReport', item: 'SanLuong_BanNhap', detail: 'Tạo mã nhúng công khai.' },
      { at: '2026-09-18 21:15', user: 'baocao.chung@dlx.example', action: 'ExportReport', item: 'SanLuong_Q3', detail: 'Xuất dữ liệu gốc trang Tra cứu khách hàng (.xlsx).' }];
    // Bản nháp: mô hình riêng không có role, có bảng khách hàng, đã Publish to web.
    const draftModel = JSON.parse(JSON.stringify(d.model));
    draftModel.roles = [];
    s.extra = [{ id: 'draft', name: 'SanLuong_BanNhap', model: draftModel,
      report: JSON.parse(JSON.stringify(d.report)), note: 'Bản sao lưu “để thử giao diện”, tạo 03/09/2026.' }];
    s.embeds = [{ id: 'e1', report: 'draft', by: 'nhanvien.baocao@dlx.example', at: '2026-09-03 16:40', url: 'https://app.powerbi.example/view?r=eyJrIjoiMDNhZ...' }];
    s.model = JSON.parse(JSON.stringify(d.model));
    s.report = JSON.parse(JSON.stringify(d.report));
    s.publishedAt = '2026-08-12 14:00';
    return { desktop: d, service: s, dataset: 'th8' };
  }

  const SCENARIOS = {
    bi01: { title: 'BI 01 – Nhập ba bảng nhỏ', group: 'Bài BI ngắn', build: () => biScenario(1) },
    bi02: { title: 'BI 02 – Nối bảng đơn vị và ngày', group: 'Bài BI ngắn', build: () => biScenario(2) },
    bi03: { title: 'BI 03 – Tạo một thẻ tổng sản lượng', group: 'Bài BI ngắn', build: () => biScenario(3) },
    bi04: { title: 'BI 04 – Đếm khách khác với đếm dòng', group: 'Bài BI ngắn', build: () => biScenario(4) },
    bi05: { title: 'BI 05 – Thử slicer và hiểu giới hạn', group: 'Bài BI ngắn', build: () => biScenario(5) },
    bi06: { title: 'BI 06 – Thử RLS cho từng đơn vị', group: 'Bài BI ngắn', build: () => biScenario(6) },
    bi07: { title: 'BI 07 – Tìm lỗi quan hệ bị tắt', group: 'Bài BI ngắn', build: () => biScenario(7) },
    bi08: { title: 'BI 08 – Một người có hai role', group: 'Bài BI ngắn', build: () => biScenario(7) },
    bi09: { title: 'BI 09 – Lọc theo ngày', group: 'Bài BI ngắn', build: () => biScenario(7) },
    bi10: { title: 'BI 10 – Kiểm thử người xem trên service', group: 'Bài BI ngắn', build: () => biScenario(7) },
    th8: { title: 'Thực hành 8 – Báo cáo quản trị có RLS', group: 'Thực hành 8', build: th8Scenario },
    rasoat: { title: 'Rà soát báo cáo đang vận hành (tìm lỗi phân quyền)', group: 'Rà soát', build: auditScenario }
  };

  global.RLSData = { SCENARIOS, ENTER_DATA, DYN_RULE };
})(window);
