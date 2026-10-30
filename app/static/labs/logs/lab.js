'use strict';
const $ = id => document.getElementById(id);
const text = (tag, value, cls) => { const el = document.createElement(tag); el.textContent = value; if (cls) el.className = cls; return el; };
let events = [], filtered = [], page = 0, selected = null, draftName = '', draft = emptyDraft();
const pageSize = 40;
function emptyDraft() { return {notes: {}, sources: {}, days: {}, pins: {}}; }
function store() {
  if (!draftName) { $('draft-status').textContent = 'Chọn tên và bấm Mở bản nháp để lưu. Có thể tải .txt ngay.'; return; }
  try { localStorage.setItem('loglab-v1:' + draftName, JSON.stringify(draft)); $('draft-status').textContent = 'Đã lưu bản nháp trên máy này · ' + draftName; }
  catch { $('draft-status').textContent = 'Không lưu được trên trình duyệt. Hãy tải bản nháp .txt.'; }
}
function count(field) { const out = {}; for (const e of events) { const k = field === 'day' ? dayOf(e.ts) : e[field]; out[k] = (out[k] || 0) + 1; } return out; }
function dayOf(ts) { return new Date(new Date(ts).getTime() + 7 * 3600000).toISOString().slice(0, 10); }
function localTime(ts) { return new Date(new Date(ts).getTime() + 7 * 3600000).toISOString().replace('T', ' ').replace('.000Z', ' +07:00'); }
function option(parent, value, label) { const o = text('option', label); o.value = value; parent.append(o); }
function reviewRows(target, entries, kind) {
  $(target).replaceChildren();
  for (const [key, n] of entries) {
    const row = text('div', '', 'review-row');
    const b = text('button', key); b.type = 'button'; b.onclick = () => { resetFilters(); $(kind === 'sources' ? 'source' : 'day').value = key; applyFilters(); $('query').focus(); };
    const note = document.createElement('textarea'); note.value = draft[kind][key] || ''; note.setAttribute('aria-label', 'Nhận xét ' + key); note.placeholder = 'Truy vấn, mẫu nền/ngoại lệ, event tham chiếu, việc còn mở…';
    note.oninput = () => { draft[kind][key] = note.value; store(); coverage(); };
    row.append(b, text('span', n + ' dòng'), note); $(target).append(row);
  }
}
function coverage() {
  const meaningful = obj => Object.values(obj).filter(v => v.trim()).length;
  $('coverage').textContent = `Đã ghi nhận xét: ${meaningful(draft.sources)}/${Object.keys(count('source')).length} nguồn · ${meaningful(draft.days)}/${Object.keys(count('day')).length} ngày. Nhận xét cần được giảng viên đối chiếu bằng chứng.`;
}
function restoreUI() {
  document.querySelectorAll('[data-note]').forEach(el => { el.value = draft.notes[el.dataset.note] || ''; });
  reviewRows('source-notes', Object.entries(count('source')).sort((a,b) => b[1]-a[1]), 'sources');
  reviewRows('day-notes', Object.entries(count('day')).sort(), 'days');
  coverage(); renderEvidence(); words();
}
$('load-draft').onclick = () => {
  const name = $('profile').value.trim();
  if (!name) { $('draft-status').textContent = 'Nhập tên bản nháp trước.'; return; }
  let saved;
  try { saved = JSON.parse(localStorage.getItem('loglab-v1:' + name) || 'null'); }
  catch { $('draft-status').textContent = 'Không đọc được bản nháp. Hãy tải bản đang mở trước khi đổi.'; return; }
  const valid = saved && ['notes','sources','days','pins'].every(k => saved[k] && typeof saved[k] === 'object' && !Array.isArray(saved[k]));
  // Tên mới chưa có bản lưu: giữ nội dung đang mở và lưu dưới tên này.
  if (valid && draftName !== name && JSON.stringify(draft) !== JSON.stringify(emptyDraft()) && !confirm('Đổi bản nháp sẽ thay nội dung đang mở. Bạn đã chép hoặc tải bản hiện tại?')) return;
  draftName = name;
  if (valid) draft = saved;
  restoreUI(); store();
};
document.querySelectorAll('[data-tab]').forEach(b => b.onclick = () => {
  document.querySelectorAll('.panel').forEach(p => p.hidden = p.id !== b.dataset.tab);
  document.querySelectorAll('[data-tab]').forEach(t => { t.classList.toggle('active', t === b); t.setAttribute('aria-pressed', String(t === b)); });
});
document.querySelectorAll('[data-note]').forEach(el => el.oninput = () => { draft.notes[el.dataset.note] = el.value; store(); words(); });
function words() { const n = (draft.notes.ban_giao || '').trim().split(/\s+/).filter(Boolean).length; $('word-count').textContent = `${n}/300 từ${n > 300 ? ' · Cần rút gọn trước khi nộp.' : ''}`; }
function resetFilters() { for (const k of ['query','source','day','severity']) $(k).value = ''; }
$('reset').onclick = () => { resetFilters(); applyFilters(); };
function applyFilters() {
  const q = $('query').value.trim().toLowerCase(), src = $('source').value, day = $('day').value, sev = $('severity').value;
  filtered = events.filter(e => (!q || e._search.includes(q)) && (!src || e.source === src) && (!day || dayOf(e.ts) === day) && (!sev || e.severity === sev));
  const field = $('sort').value; filtered.sort((a,b) => new Date(a[field])-new Date(b[field]) || a.event_id.localeCompare(b.event_id)); page = 0; renderRows();
}
function renderRows() {
  $('rows').replaceChildren();
  const pages = Math.max(1, Math.ceil(filtered.length / pageSize));
  for (const e of filtered.slice(page * pageSize, (page + 1) * pageSize)) {
    const row = document.createElement('tr'), cell = document.createElement('td'), b = text('button', e.event_id);
    b.onclick = () => openEvent(e); cell.append(b); row.append(cell);
    for (const value of [e.ts, e.source + ' · ' + e.severity, e.actor_id || '—', e.event_type + ' · ' + (e.resource_id || e.path || '—'), e.result + (e.http_status ? ' · ' + e.http_status : '')]) row.append(text('td', value));
    $('rows').append(row);
  }
  $('result-count').textContent = `${filtered.length.toLocaleString('vi-VN')} / ${events.length.toLocaleString('vi-VN')} bản ghi khớp bộ lọc. Đã đọc vào bộ nhớ toàn bộ file; số này không xác nhận đã điều tra hết.`;
  if (!filtered.length) { const row = document.createElement('tr'), cell = text('td', 'Không có kết quả. Thử bỏ bớt điều kiện hoặc tìm lại toàn file.'); cell.colSpan = 6; row.append(cell); $('rows').append(row); }
  $('page').textContent = `Trang ${page + 1}/${pages}`; $('prev').disabled = page === 0; $('next').disabled = page >= pages - 1;
  const types = {}, results = {};
  for (const e of filtered) { types[e.event_type] = (types[e.event_type] || 0) + 1; results[e.result] = (results[e.result] || 0) + 1; }
  $('distribution').replaceChildren(text('p', 'Thống kê trên toàn bộ kết quả lọc, không chỉ trang đang mở. Chọn loại sự kiện để tìm tiếp; dùng Tìm lại toàn file để mở rộng.'));
  const chips = text('div', '', 'chips');
  for (const [k,n] of Object.entries(types).sort((a,b) => b[1]-a[1])) { const b = text('button', `${k} · ${n}`); b.onclick = () => { $('query').value = '"event_type":"' + k + '"'; applyFilters(); }; chips.append(b); }
  $('distribution').append(chips, text('p', 'Kết quả: ' + Object.entries(results).map(([k,n]) => `${k}: ${n}`).join(' · ')));
}
$('prev').onclick = () => { if (page > 0) { page--; renderRows(); } };
$('next').onclick = () => { if ((page + 1) * pageSize < filtered.length) { page++; renderRows(); } };
for (const k of ['source','day','severity','sort']) $(k).onchange = applyFilters;
let debounce;
$('query').oninput = () => { clearTimeout(debounce); debounce = setTimeout(applyFilters, 150); };
function openEvent(e) {
  selected = e; $('detail-title').textContent = e.event_id + ' · ' + e.source;
  const {_search, ...raw} = e; $('json').textContent = JSON.stringify(raw, null, 2); $('pivots').replaceChildren();
  for (const k of ['actor_id','session_id','trace_id','resource_id','device_id','src_ip']) {
    if (!e[k]) continue;
    const b = text('button', k + ': ' + e[k]); b.onclick = () => { resetFilters(); $('query').value = e[k]; applyFilters(); $('detail').close(); }; $('pivots').append(b);
  }
  $('pin').textContent = draft.pins[e.event_id] ? 'Đã ghim · xem ở Bàn giao' : 'Ghim bằng chứng'; $('detail').showModal();
}
$('close').onclick = () => $('detail').close();
$('pin').onclick = () => { if (!selected) return; draft.pins[selected.event_id] ??= {timeline: '1'}; store(); renderEvidence(); $('pin').textContent = 'Đã ghim · xem ở Bàn giao'; };
function pinned(timeline) { return events.filter(e => draft.pins[e.event_id] && (!timeline || draft.pins[e.event_id].timeline === timeline)).sort((a,b) => new Date(a.ts)-new Date(b.ts)); }
function renderEvidence() {
  $('evidence').replaceChildren();
  if (!pinned().length) { $('evidence').append(text('p', 'Chưa ghim bằng chứng. Mở event trong kho nhật ký rồi bấm Ghim bằng chứng.')); return; }
  for (const group of ['1','2']) {
    const entries = pinned(group), sources = new Set(entries.map(e => e.source)), days = new Set(entries.map(e => dayOf(e.ts)));
    $('evidence').append(text('h3', `Timeline ${group} · ${entries.length} event · ${sources.size} nguồn · ${days.size} ngày`));
    for (const e of entries) {
      const row = text('div', '', 'evidence-row'), b = text('button', e.event_id); b.onclick = () => openEvent(e);
      const select = document.createElement('select'); select.setAttribute('aria-label', 'Timeline ' + e.event_id); option(select, '1', 'Timeline 1'); option(select, '2', 'Timeline 2'); select.value = group;
      select.onchange = () => { draft.pins[e.event_id].timeline = select.value; store(); renderEvidence(); };
      const remove = text('button', 'Bỏ ghim'); remove.onclick = () => { delete draft.pins[e.event_id]; store(); renderEvidence(); };
      row.append(b, select, remove, text('p', `${localTime(e.ts)} · ${e.source} · ${e.event_type}`), text('p', 'Giờ nhận: ' + e.ingested_at)); $('evidence').append(row);
    }
  }
}
function report() {
  const lines = ['BUỔI 9 – CA TRỰC ĐIỀU TRA', 'Bản nháp: ' + (draftName || 'Chưa đặt tên'), 'Chưa nộp cho giảng viên.', $('hash').textContent, '', '1–2. BẢN ĐỒ / PHẠM VI', draft.notes.nhan_ca || '(chưa ghi)', '', 'NGUỒN'];
  for (const [k,n] of Object.entries(count('source')).sort()) lines.push(`${k} (${n}): ${draft.sources[k] || '(chưa rà/ghi nhận)'}`);
  lines.push('', 'NGÀY (ts +07:00)'); for (const [k,n] of Object.entries(count('day')).sort()) lines.push(`${k} (${n}): ${draft.days[k] || '(chưa rà/ghi nhận)'}`);
  lines.push('', 'TRUY VẤN / PHẠM VI', draft.notes.truy_van || '(chưa ghi)', '', '3. HỒ SƠ', draft.notes.ho_so || '(chưa ghi)', '', '4. PHẢN BIỆN', draft.notes.phan_bien || '(chưa ghi)');
  for (const group of ['1','2']) {
    lines.push('', 'TIMELINE ' + group, 'ts gốc | ts +07:00 | ingested_at | event_id | source | hành động | đối tượng | kết quả');
    for (const e of pinned(group)) lines.push([e.ts,localTime(e.ts),e.ingested_at,e.event_id,e.source,e.event_type,e.resource_id || e.path || '',e.result].join(' | '));
  }
  lines.push('', 'LIÊN KẾT / GIỚI HẠN', draft.notes.timeline || '(chưa ghi)', '', 'BÀN GIAO', draft.notes.ban_giao || '(chưa ghi)'); return lines.join('\n');
}
$('copy').onclick = async () => { try { await navigator.clipboard.writeText(report()); $('export-status').textContent = 'Đã chép. Dán vào bài trên lớp học rồi bấm Nộp bài.'; } catch { $('export-status').textContent = 'Không chép được. Dùng Tải bản nháp .txt.'; } };
$('download').onclick = () => { const url = URL.createObjectURL(new Blob([report()], {type: 'text/plain;charset=utf-8'})), a = document.createElement('a'); a.href = url; a.download = 'buoi9-ban-nhap.txt'; a.click(); setTimeout(() => URL.revokeObjectURL(url), 1000); $('export-status').textContent = 'Đã tạo tệp bản nháp; chưa nộp.'; };
async function init() {
  try {
    const response = await fetch('nhat_ky.jsonl.log'); if (!response.ok) throw new Error('HTTP ' + response.status);
    const raw = await response.text(), lines = raw.replace(/^\uFEFF/, '').split(/\r?\n/).filter(s => s.trim());
    events = lines.map((line,i) => { try { const e = JSON.parse(line); if (!e.event_id || !e.source || !Number.isFinite(Date.parse(e.ts)) || !Number.isFinite(Date.parse(e.ingested_at))) throw new Error(); e._search = line.toLowerCase(); return e; } catch { throw new Error('Bản ghi không hợp lệ tại dòng ' + (i+1)); } });
    $('status').textContent = 'Đã đọc ' + events.length.toLocaleString('vi-VN') + ' bản ghi. Bắt đầu từ Nhận ca.';
    const sources = count('source'), days = Object.keys(count('day')).sort();
    for (const [id, values] of [['source',Object.keys(sources).sort()],['day',days],['severity',Object.keys(count('severity')).sort()]]) for (const v of values) option($(id), v, v);
    for (const [value,label] of [[events.length.toLocaleString('vi-VN'),'bản ghi'],[Object.keys(sources).length,'nguồn'],[Object.keys(count('zone')).length,'vùng'],[days.length,'ngày']]) { const box = text('div','','metric'); box.append(text('strong',value),text('span',label)); $('metrics').append(box); }
    for (const [id, field] of [['zones','zone'],['severities','severity']]) for (const [k,n] of Object.entries(count(field)).sort((a,b)=>b[1]-a[1])) { const row = text('div','','stat'); row.append(text('span',k),text('strong',n.toLocaleString('vi-VN'))); $(id).append(row); }
    restoreUI(); applyFilters();
    try { const bytes = new TextEncoder().encode(raw), digest = await crypto.subtle.digest('SHA-256',bytes); $('hash').textContent = 'SHA-256: ' + Array.from(new Uint8Array(digest),b=>b.toString(16).padStart(2,'0')).join(''); }
    catch { $('hash').textContent = 'Trình duyệt chưa hỗ trợ tính băm tại đây. Tải log gốc để kiểm tra bằng công cụ trên máy.'; }
  } catch (error) { $('status').textContent = 'Không mở được nhật ký: ' + error.message + '. Tải lại trang hoặc báo giảng viên.'; }
}
init();
