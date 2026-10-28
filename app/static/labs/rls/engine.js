/* Bộ máy mô phỏng: DAX rút gọn, lan truyền bộ lọc qua quan hệ, RLS/OLS và quyền trên service.
   Mô phỏng hành vi để học, không phải Power BI thật. */
(function (global) {
  'use strict';

  class DaxError extends Error {}
  const fail = msg => { throw new DaxError(msg); };

  // ---------- Tách từ ----------
  function tokenize(src) {
    const out = [];
    let i = 0;
    while (i < src.length) {
      const c = src[i];
      if (/\s/.test(c)) { i++; continue; }
      if (src.startsWith('--', i) || src.startsWith('//', i)) { while (i < src.length && src[i] !== '\n') i++; continue; }
      if (src.startsWith('/*', i)) { const e = src.indexOf('*/', i + 2); i = e < 0 ? src.length : e + 2; continue; }
      if ('“”„‟'.includes(c)) fail(`Cú pháp của '${c}' không đúng. Dấu ngoặc kép cong thường xuất hiện khi chép từ Word; hãy gõ lại bằng ngoặc kép thẳng ".`);
      if ('‘’'.includes(c)) fail(`Cú pháp của '${c}' không đúng. Hãy gõ lại bằng dấu nháy thẳng '.`);
      if (c === '"') {
        let s = ''; i++;
        for (;;) {
          if (i >= src.length) fail('Chuỗi văn bản chưa được đóng bằng dấu ".');
          if (src[i] === '"') { if (src[i + 1] === '"') { s += '"'; i += 2; continue; } i++; break; }
          s += src[i++];
        }
        out.push({ t: 'str', v: s }); continue;
      }
      if (/[0-9]/.test(c) || (c === '.' && /[0-9]/.test(src[i + 1] || ''))) {
        const m = /^[0-9]*\.?[0-9]+/.exec(src.slice(i));
        out.push({ t: 'num', v: Number(m[0]) }); i += m[0].length; continue;
      }
      if (c === '[') {
        const e = src.indexOf(']', i);
        if (e < 0) fail('Thiếu dấu ] đóng tên cột.');
        out.push({ t: 'br', v: src.slice(i + 1, e) }); i = e + 1; continue;
      }
      if (c === "'") {
        const e = src.indexOf("'", i + 1);
        if (e < 0) fail("Thiếu dấu ' đóng tên bảng.");
        out.push({ t: 'id', v: src.slice(i + 1, e), quoted: true }); i = e + 1; continue;
      }
      if (/[\p{L}_]/u.test(c)) {
        const m = /^[\p{L}\p{N}_.]+/u.exec(src.slice(i));
        out.push({ t: 'id', v: m[0] }); i += m[0].length; continue;
      }
      const two = src.substr(i, 2);
      if (['&&', '||', '<>', '<=', '>=', '=='].includes(two)) { out.push({ t: 'op', v: two }); i += 2; continue; }
      if ('=<>+-*/&(),{}'.includes(c)) { out.push({ t: 'op', v: c }); i++; continue; }
      fail(`Ký tự không hợp lệ: ${c}`);
    }
    return out;
  }

  // ---------- Phân tích cú pháp ----------
  function parse(src) {
    if (!String(src || '').trim()) fail('Biểu thức trống.');
    const tk = tokenize(src);
    let p = 0;
    const peek = (o = 0) => tk[p + o];
    const isOp = v => peek() && peek().t === 'op' && peek().v === v;
    const isKw = v => peek() && peek().t === 'id' && !peek().quoted && peek().v.toUpperCase() === v;
    const expect = v => { if (!isOp(v)) fail(`Cần “${v}” ${peek() ? 'trước “' + (peek().v) + '”' : 'ở cuối biểu thức'}.`); p++; };

    function expr() { return or(); }
    function or() { let l = and(); while (isOp('||')) { p++; l = { k: 'bin', op: '||', l, r: and() }; } return l; }
    function and() { let l = cmp(); while (isOp('&&')) { p++; l = { k: 'bin', op: '&&', l, r: cmp() }; } return l; }
    function cmp() {
      const l = cat();
      if (peek() && peek().t === 'op' && ['=', '==', '<>', '<', '>', '<=', '>='].includes(peek().v)) { const op = tk[p++].v; return { k: 'bin', op: op === '==' ? '=' : op, l, r: cat() }; }
      if (isKw('IN')) { p++; return { k: 'in', l, r: cat() }; }
      if (isKw('NOT') && peek(1) && peek(1).t === 'id' && peek(1).v.toUpperCase() === 'IN') { p += 2; return { k: 'un', op: 'NOT', e: { k: 'in', l, r: cat() } }; }
      return l;
    }
    function cat() { let l = add(); while (isOp('&')) { p++; l = { k: 'bin', op: '&', l, r: add() }; } return l; }
    function add() { let l = mul(); while (isOp('+') || isOp('-')) { const op = tk[p++].v; l = { k: 'bin', op, l, r: mul() }; } return l; }
    function mul() { let l = un(); while (isOp('*') || isOp('/')) { const op = tk[p++].v; l = { k: 'bin', op, l, r: un() }; } return l; }
    function un() {
      if (isOp('-')) { p++; return { k: 'un', op: '-', e: un() }; }
      if (isKw('NOT') && !(peek(1) && peek(1).t === 'op' && peek(1).v === '(')) { p++; return { k: 'un', op: 'NOT', e: un() }; }
      return prim();
    }
    function prim() {
      const t = peek();
      if (!t) fail('Biểu thức kết thúc đột ngột.');
      if (t.t === 'num') { p++; return { k: 'lit', v: t.v }; }
      if (t.t === 'str') { p++; return { k: 'lit', v: t.v }; }
      if (t.t === 'br') { p++; return { k: 'col', table: null, col: t.v }; }
      if (isOp('(')) { p++; const e = expr(); expect(')'); return e; }
      if (isOp('{')) {
        p++; const items = [];
        if (!isOp('}')) { items.push(expr()); while (isOp(',')) { p++; items.push(expr()); } }
        expect('}'); return { k: 'list', items };
      }
      if (t.t === 'id') {
        p++;
        if (peek() && peek().t === 'br') { const c = tk[p++].v; return { k: 'col', table: t.v, col: c }; }
        if (!t.quoted && isOp('(')) {
          p++; const args = [];
          if (!isOp(')')) { args.push(expr()); while (isOp(',')) { p++; args.push(expr()); } }
          expect(')');
          return { k: 'call', fn: t.v.toUpperCase(), args };
        }
        const u = t.v.toUpperCase();
        if (!t.quoted && (u === 'TRUE' || u === 'FALSE')) return { k: 'lit', v: u === 'TRUE' };
        return { k: 'tbl', name: t.v };
      }
      fail(`Không hiểu “${t.v}” ở vị trí này.`);
    }
    const tree = expr();
    if (p < tk.length) fail(`Thừa “${tk[p].v}” sau biểu thức.`);
    return tree;
  }

  // ---------- Dữ liệu mô hình ----------
  const TYPES = ['Text', 'Whole number', 'Decimal number', 'Date', 'True/false'];

  function convert(v, type) {
    if (v === null || v === undefined || v === '') return null;
    if (type === 'Text') return String(v);
    if (type === 'Whole number' || type === 'Decimal number') {
      const n = Number(String(v).replace(',', '.'));
      if (!Number.isFinite(n)) return { err: String(v) };
      return type === 'Whole number' ? Math.round(n) : n;
    }
    if (type === 'Date') {
      const s = String(v).trim();
      let m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(s);
      if (m) return s;
      m = /^(\d{1,2})\/(\d{1,2})\/(\d{4})$/.exec(s);
      if (m) return `${m[3]}-${m[2].padStart(2, '0')}-${m[1].padStart(2, '0')}`;
      return { err: s };
    }
    if (type === 'True/false') return /^(true|1|đúng)$/i.test(String(v));
    return v;
  }

  function maskValue(v) {
    const s = v === null || v === undefined ? '' : String(v);
    return s.length < 6 ? '****' : s.slice(0, 3) + '****' + s.slice(-3);
  }

  // Áp các bước Power Query, kiểu dữ liệu và cột tính toán. Kết quả lưu tạm theo đối tượng mô hình.
  const matCache = new WeakMap();
  function materialize(model) {
    const key = JSON.stringify(model);
    const hit = matCache.get(model);
    if (hit && hit.key === key) return hit.M;
    const M = { tables: {}, model };
    for (const t of model.tables) {
      let rows = t.source.map(r => ({ ...r }));
      let cols = t.columns.filter(c => !c.calc).map(c => c.name);
      for (const s of t.steps || []) {
        if (s.op === 'remove') { cols = cols.filter(c => c !== s.col); rows.forEach(r => delete r[s.col]); }
        if (s.op === 'mask') rows.forEach(r => { r[s.col] = maskValue(r[s.col]); });
        if (s.op === 'filter') rows = rows.filter(r => String(r[s.col]) !== String(s.value));
      }
      const defs = t.columns.filter(c => !c.calc && cols.includes(c.name));
      const typed = rows.map((r, i) => {
        const o = { __id: i };
        for (const c of defs) o[c.name] = convert(r[c.name], c.type);
        return o;
      });
      M.tables[t.name] = { name: t.name, rows: typed, def: t, cols: defs.map(c => c.name) };
    }
    // Cột tính toán: tính một lần khi nạp, không chịu RLS (giống Power BI).
    M.calcErrors = {};
    for (const t of model.tables) {
      for (const c of t.columns.filter(c => c.calc)) {
        const T = M.tables[t.name];
        const key = `${t.name}[${c.name}]`;
        let tree = null;
        try { tree = parse(c.calc); } catch (e) { M.calcErrors[key] = e.message; }
        for (const r of T.rows) {
          try {
            r[c.name] = tree ? scalar(evaluate(tree, mkEnv(M, { rowCtx: [{ table: t.name, row: r }] }))) : null;
          } catch (e) { r[c.name] = { err: '#ERROR' }; M.calcErrors[key] = e.message; }
        }
        T.cols.push(c.name);
      }
    }
    matCache.set(model, { key, M });
    return M;
  }

  function colDef(M, table, col) {
    const T = M.tables[table];
    if (!T) fail(`Không tìm thấy bảng '${table}'.`);
    const def = T.def.columns.find(c => c.name === col);
    if (!def || !T.cols.includes(col)) fail(`Không tìm thấy cột '${col}' trong bảng '${table}'.`);
    return def;
  }

  // ---------- Ngữ cảnh lọc ----------
  // ctx = { cols: { "T|C": [giá trị] }, rows: { T: [__id] } }
  const emptyCtx = () => ({ cols: {}, rows: {} });
  const cloneCtx = c => ({ cols: { ...c.cols }, rows: { ...c.rows } });

  function mkEnv(M, o) {
    return Object.assign({ M, upn: '', ctx: emptyCtx(), rowCtx: [], base: null, cache: new Map(), depth: 0, sec: false }, o);
  }

  function baseRows(env, table) {
    const T = env.M.tables[table];
    if (!T) fail(`Không tìm thấy bảng '${table}'.`);
    return env.base && env.base[table] ? env.base[table] : T.rows;
  }

  // Lọc từng bảng theo ngữ cảnh rồi lan truyền qua các quan hệ đang hoạt động.
  function filteredAll(env, ctx, secMode) {
    const key = JSON.stringify([ctx, !!secMode]);
    if (env.cache.has(key)) return env.cache.get(key);
    const sets = {}, filtered = {};
    for (const name of Object.keys(env.M.tables)) {
      let rows = baseRows(env, name);
      let f = false;
      for (const [k, vals] of Object.entries(ctx.cols)) {
        const [t, c] = k.split('|');
        if (t !== name) continue;
        const set = new Set(vals.map(v => JSON.stringify(v)));
        rows = rows.filter(r => set.has(JSON.stringify(r[c] === undefined ? null : r[c])));
        f = true;
      }
      if (ctx.rows[name]) { const ids = new Set(ctx.rows[name]); rows = rows.filter(r => ids.has(r.__id)); f = true; }
      sets[name] = rows; filtered[name] = f;
    }
    const rels = env.M.model.relationships.filter(r => r.active && sets[r.from] && sets[r.to]);
    for (let loop = 0, changed = true; changed && loop < 12; loop++) {
      changed = false;
      for (const r of rels) {
        if (filtered[r.from]) {
          const keys = new Set(sets[r.from].map(x => x[r.fromCol]));
          const next = sets[r.to].filter(x => keys.has(x[r.toCol]));
          if (next.length !== sets[r.to].length) { sets[r.to] = next; filtered[r.to] = true; changed = true; }
        }
        const both = r.cross === 'Both' && (!secMode || r.secBoth);
        if (both && filtered[r.to]) {
          const keys = new Set(sets[r.to].map(x => x[r.toCol]));
          const next = sets[r.from].filter(x => keys.has(x[r.fromCol]));
          if (next.length !== sets[r.from].length) { sets[r.from] = next; filtered[r.from] = true; changed = true; }
        }
      }
    }
    const res = { sets, filtered };
    env.cache.set(key, res);
    return res;
  }

  const rowsIn = (env, table, ctx) => filteredAll(env, ctx || env.ctx).sets[table];

  // ---------- Đánh giá ----------
  const isBlank = v => v === null || v === undefined;
  const isTable = v => v && typeof v === 'object' && v.__table;
  const isErr = v => v && typeof v === 'object' && 'err' in v;

  function scalar(v) {
    if (isTable(v)) {
      if (v.rows.length === 0) return null;
      if (v.rows.length === 1 && v.cols.length === 1) return v.rows[0][v.cols[0]];
      fail('Một bảng có nhiều giá trị được dùng ở chỗ cần một giá trị duy nhất.');
    }
    if (isErr(v)) fail(`Giá trị '${v.err}' không chuyển được sang kiểu của cột.`);
    return v;
  }

  function typeName(v) { return typeof v === 'number' ? 'Integer/Number' : typeof v === 'boolean' ? 'True/False' : 'Text'; }

  function compare(op, a, b) {
    a = scalar(a); b = scalar(b);
    if (!isBlank(a) && !isBlank(b) && typeof a !== typeof b && !(typeof a === 'boolean' || typeof b === 'boolean'))
      fail(`Phép so sánh DAX không hỗ trợ so sánh giá trị kiểu ${typeName(a)} với giá trị kiểu ${typeName(b)}. Hãy dùng VALUE hoặc FORMAT để chuyển kiểu.`);
    if (isBlank(a)) a = typeof b === 'number' ? 0 : typeof b === 'boolean' ? false : '';
    if (isBlank(b)) b = typeof a === 'number' ? 0 : typeof a === 'boolean' ? false : '';
    if (typeof a === 'string') { a = a.toLowerCase(); b = String(b).toLowerCase(); }
    switch (op) {
      case '=': return a === b;
      case '<>': return a !== b;
      case '<': return a < b;
      case '>': return a > b;
      case '<=': return a <= b;
      case '>=': return a >= b;
    }
  }

  function num(v) {
    v = scalar(v);
    if (isBlank(v)) return null;
    if (typeof v === 'boolean') return v ? 1 : 0;
    if (typeof v !== 'number') fail(`Không thể chuyển giá trị '${v}' kiểu Text sang kiểu Number.`);
    return v;
  }

  // Tên cột trong một nút, để biết bộ lọc CALCULATE áp lên cột nào.
  function colsIn(node, out = []) {
    if (!node || typeof node !== 'object') return out;
    if (node.k === 'col' && node.table) out.push(node);
    for (const k of ['l', 'r', 'e']) colsIn(node[k], out);
    (node.args || []).forEach(a => colsIn(a, out));
    (node.items || []).forEach(a => colsIn(a, out));
    return out;
  }

  // Chuyển ngữ cảnh dòng thành ngữ cảnh lọc (context transition).
  function transition(env, ctx) {
    const c = cloneCtx(ctx);
    for (const rc of env.rowCtx) {
      if (rc.origin && rc.origin.length) rc.origin.forEach(o => { c.cols[o.table + '|' + o.col] = [rc.row[o.alias || o.col]]; });
      else if (rc.row && rc.row.__id !== undefined) c.rows[rc.table] = [rc.row.__id];
    }
    return c;
  }

  // Áp các đối số lọc của CALCULATE / CALCULATETABLE.
  function applyFilters(env, ctx, args) {
    const c = cloneCtx(ctx);
    for (const a of args) {
      if (a.k === 'call' && (a.fn === 'ALL' || a.fn === 'REMOVEFILTERS')) {
        if (!a.args.length) { c.cols = {}; c.rows = {}; continue; }
        for (const x of a.args) {
          if (x.k === 'tbl') { for (const k of Object.keys(c.cols)) if (k.startsWith(x.name + '|')) delete c.cols[k]; delete c.rows[x.name]; }
          else if (x.k === 'col') delete c.cols[x.table + '|' + x.col];
        }
        continue;
      }
      const refs = colsIn(a);
      const tables = [...new Set(refs.map(r => r.table))];
      const isPred = a.k === 'bin' || a.k === 'in' || a.k === 'un';
      if (isPred && tables.length === 1 && refs.length) {
        const t = tables[0];
        const cols = [...new Set(refs.map(r => r.col))];
        cols.forEach(col => colDef(env.M, t, col));
        if (cols.length === 1) {
          const vals = [...new Set(baseRows(env, t).map(r => JSON.stringify(r[cols[0]] === undefined ? null : r[cols[0]])))].map(s => JSON.parse(s));
          const keep = vals.filter(v => truthy(evaluate(a, { ...env, rowCtx: env.rowCtx.concat([{ table: t, row: { [cols[0]]: v } }]) })));
          c.cols[t + '|' + cols[0]] = keep;
        } else {
          const keep = baseRows(env, t).filter(r => truthy(evaluate(a, { ...env, rowCtx: env.rowCtx.concat([{ table: t, row: r }]) })));
          cols.forEach(col => delete c.cols[t + '|' + col]);
          c.rows[t] = keep.map(r => r.__id);
        }
        continue;
      }
      if (isPred) fail('Bộ lọc trong CALCULATE chỉ được tham chiếu cột của một bảng. Hãy dùng FILTER.');
      const tv = evalTable(a, env);
      if (tv.origin && tv.origin.length) {
        tv.origin.forEach(o => { c.cols[o.table + '|' + o.col] = [...new Set(tv.rows.map(r => r[o.alias || o.col]))]; });
      } else if (tv.table) {
        c.rows[tv.table] = tv.rows.map(r => r.__id);
      }
    }
    return c;
  }

  function truthy(v) {
    v = scalar(v);
    if (typeof v === 'boolean') return v;
    if (isBlank(v)) return false;
    if (typeof v === 'number') return v !== 0;
    fail(`Biểu thức trả về văn bản '${v}', không phải TRUE/FALSE.`);
  }

  // Trả về bảng: { __table, table, rows, cols, origin }
  function evalTable(node, env) {
    if (node.k === 'tbl') {
      const rows = rowsIn(env, node.name, env.ctx);
      if (!env.M.tables[node.name]) fail(`Không tìm thấy bảng '${node.name}'.`);
      return { __table: true, table: node.name, rows, cols: env.M.tables[node.name].cols, origin: null };
    }
    if (node.k === 'list') {
      const rows = node.items.map(i => ({ Value: scalar(evaluate(i, env)) }));
      return { __table: true, table: null, rows, cols: ['Value'], origin: null };
    }
    if (node.k === 'call') {
      const A = node.args;
      switch (node.fn) {
        case 'VALUES': case 'DISTINCT': {
          if (A.length !== 1) fail(`${node.fn} cần đúng một đối số.`);
          if (A[0].k === 'tbl') return evalTable(A[0], env);
          if (A[0].k !== 'col' || !A[0].table) fail(`${node.fn} cần một cột có tên bảng, ví dụ VALUES(Bang[Cot]).`);
          const { table, col } = A[0];
          colDef(env.M, table, col);
          const vals = [...new Set(rowsIn(env, table, env.ctx).map(r => JSON.stringify(r[col] === undefined ? null : r[col])))].map(s => JSON.parse(s));
          return { __table: true, table, rows: vals.map(v => ({ [col]: v })), cols: [col], origin: [{ table, col }] };
        }
        case 'ALL': case 'REMOVEFILTERS': {
          const x = A[0];
          if (!x) fail('ALL cần một bảng hoặc cột.');
          if (x.k === 'tbl') return { __table: true, table: x.name, rows: baseRows(env, x.name), cols: env.M.tables[x.name].cols, origin: null };
          colDef(env.M, x.table, x.col);
          const vals = [...new Set(baseRows(env, x.table).map(r => JSON.stringify(r[x.col] ?? null)))].map(s => JSON.parse(s));
          return { __table: true, table: x.table, rows: vals.map(v => ({ [x.col]: v })), cols: [x.col], origin: [{ table: x.table, col: x.col }] };
        }
        case 'FILTER': {
          const t = evalTable(A[0], env);
          const rows = t.rows.filter(r => truthy(evaluate(A[1], { ...env, rowCtx: env.rowCtx.concat([{ table: t.table, row: r, origin: t.origin }]) })));
          return { ...t, rows };
        }
        case 'CALCULATETABLE': {
          const ctx = applyFilters(env, env.rowCtx.length ? transition(env, env.ctx) : env.ctx, A.slice(1));
          return evalTable(A[0], { ...env, ctx, rowCtx: [] });
        }
        case 'SELECTCOLUMNS': case 'SUMMARIZE': fail(`Mô phỏng chưa hỗ trợ hàm ${node.fn}. Dùng VALUES hoặc CALCULATETABLE.`);
      }
    }
    const v = evaluate(node, env);
    if (isTable(v)) return v;
    fail('Cần một biểu thức bảng ở vị trí này.');
  }

  function aggregate(fn, node, env) {
    const A = node.args;
    if (fn === 'COUNTROWS') {
      const t = A.length ? evalTable(A[0], env) : fail('COUNTROWS cần một bảng.');
      return t.rows.length || null;
    }
    const c = A[0];
    if (!c || c.k !== 'col') fail(`${fn} cần một cột, ví dụ ${fn}(Bang[Cot]).`);
    if (!c.table) fail(`Hãy ghi tên bảng trước cột: ${fn}(Bang[${c.col}]).`);
    const def = colDef(env.M, c.table, c.col);
    const rows = rowsIn(env, c.table, env.ctx);
    const vals = rows.map(r => r[c.col]);
    if (vals.some(isErr)) fail(`Cột ${c.table}[${c.col}] có giá trị lỗi do sai kiểu dữ liệu.`);
    if (fn === 'DISTINCTCOUNT') return new Set(vals.map(v => JSON.stringify(v))).size || null;
    if (fn === 'COUNT') return vals.filter(v => !isBlank(v)).length || null;
    if (def.type === 'Text' || def.type === 'Date') fail(`Hàm ${fn} không làm việc được với giá trị kiểu ${def.type === 'Text' ? 'String' : 'Date'} (cột ${c.table}[${c.col}] đang là ${def.type}). Đổi kiểu dữ liệu của cột sang số.`);
    const ns = vals.filter(v => !isBlank(v));
    if (!ns.length) return null;
    switch (fn) {
      case 'SUM': return ns.reduce((a, b) => a + b, 0);
      case 'AVERAGE': return ns.reduce((a, b) => a + b, 0) / ns.length;
      case 'MIN': return Math.min(...ns);
      case 'MAX': return Math.max(...ns);
    }
  }

  function iterate(fn, node, env) {
    const t = evalTable(node.args[0], env);
    if (!node.args[1]) fail(`${fn} cần hai đối số: bảng và biểu thức.`);
    const vals = t.rows.map(r => scalar(evaluate(node.args[1], { ...env, rowCtx: env.rowCtx.concat([{ table: t.table, row: r, origin: t.origin }]) })));
    const ns = vals.filter(v => !isBlank(v)).map(num);
    if (!ns.length) return null;
    switch (fn) {
      case 'SUMX': return ns.reduce((a, b) => a + b, 0);
      case 'AVERAGEX': return ns.reduce((a, b) => a + b, 0) / ns.length;
      case 'MINX': return Math.min(...ns);
      case 'MAXX': return Math.max(...ns);
      case 'COUNTX': return ns.length;
    }
  }

  function measureByName(M, name) {
    return M.model.measures.find(m => m.name.toLowerCase() === String(name).toLowerCase());
  }

  function evalMeasure(m, env) {
    if (env.depth > 20) fail(`Thước đo [${m.name}] tham chiếu vòng tròn.`);
    const tree = parse(m.expr);
    const ctx = env.rowCtx.length ? transition(env, env.ctx) : env.ctx;
    return evaluate(tree, { ...env, ctx, rowCtx: [], depth: env.depth + 1 });
  }

  function findColumnInRowCtx(env, table, col) {
    for (let i = env.rowCtx.length - 1; i >= 0; i--) {
      const rc = env.rowCtx[i];
      if (table && rc.table !== table) continue;
      if (rc.row && col in rc.row) return { found: true, v: rc.row[col] };
      if (rc.origin) {
        const o = rc.origin.find(o => o.col === col && (!table || o.table === table));
        if (o) return { found: true, v: rc.row[o.alias || o.col] };
      }
    }
    return { found: false };
  }

  function evaluate(node, env) {
    switch (node.k) {
      case 'lit': return node.v;
      case 'list': return evalTable(node, env);
      case 'tbl': return evalTable(node, env);
      case 'col': {
        const r = findColumnInRowCtx(env, node.table, node.col);
        if (r.found) return r.v;
        if (!node.table) {
          const m = measureByName(env.M, node.col);
          if (m) return evalMeasure(m, env);
          if (env.rowCtx.length) fail(`Không tìm thấy cột [${node.col}] trong bảng ${env.rowCtx[env.rowCtx.length - 1].table}.`);
          fail(`Không tìm thấy thước đo hoặc cột [${node.col}].`);
        }
        colDef(env.M, node.table, node.col);
        fail(`Không xác định được một giá trị duy nhất cho cột '${node.col}' trong bảng '${node.table}'. Hãy dùng một hàm tổng hợp như SUM, MIN, MAX.`);
      }
      case 'un': {
        if (node.op === '-') { const v = num(evaluate(node.e, env)); return isBlank(v) ? null : -v; }
        return !truthy(evaluate(node.e, env));
      }
      case 'in': {
        const v = scalar(evaluate(node.l, env));
        const t = evalTable(node.r, env);
        const c = t.cols[0];
        return t.rows.some(r => { try { return compare('=', v, r[t.origin ? (t.origin[0].alias || t.origin[0].col) : c]); } catch (e) { throw e; } });
      }
      case 'bin': {
        const { op } = node;
        if (op === '&&') return truthy(evaluate(node.l, env)) && truthy(evaluate(node.r, env));
        if (op === '||') return truthy(evaluate(node.l, env)) || truthy(evaluate(node.r, env));
        const a = evaluate(node.l, env), b = evaluate(node.r, env);
        if (['=', '<>', '<', '>', '<=', '>='].includes(op)) return compare(op, a, b);
        if (op === '&') { const x = scalar(a), y = scalar(b); return (isBlank(x) ? '' : String(x)) + (isBlank(y) ? '' : String(y)); }
        const x = num(a), y = num(b);
        if (op === '+') return isBlank(x) && isBlank(y) ? null : (x || 0) + (y || 0);
        if (op === '-') return isBlank(x) && isBlank(y) ? null : (x || 0) - (y || 0);
        if (op === '*') return isBlank(x) || isBlank(y) ? null : x * y;
        if (op === '/') { if (isBlank(y) || y === 0) fail('Phép chia cho 0. Hãy dùng DIVIDE.'); return isBlank(x) ? null : x / y; }
        break;
      }
      case 'call': return call(node, env);
    }
    fail('Biểu thức không hợp lệ.');
  }

  function call(node, env) {
    const A = node.args, fn = node.fn;
    const arg = i => scalar(evaluate(A[i], env));
    switch (fn) {
      case 'USERPRINCIPALNAME': case 'USERNAME': return env.upn || '';
      case 'TRUE': return true;
      case 'FALSE': return false;
      case 'BLANK': return null;
      case 'ISBLANK': return isBlank(arg(0));
      case 'NOT': return !truthy(evaluate(A[0], env));
      case 'AND': return truthy(evaluate(A[0], env)) && truthy(evaluate(A[1], env));
      case 'OR': return truthy(evaluate(A[0], env)) || truthy(evaluate(A[1], env));
      case 'IF': return truthy(evaluate(A[0], env)) ? evaluate(A[1], env) : (A[2] ? evaluate(A[2], env) : null);
      case 'LEFT': { const s = arg(0); return isBlank(s) ? '' : String(s).slice(0, A[1] ? num(evaluate(A[1], env)) : 1); }
      case 'RIGHT': { const s = arg(0), n = A[1] ? num(evaluate(A[1], env)) : 1; return isBlank(s) ? '' : String(s).slice(-n); }
      case 'MID': { const s = arg(0); return isBlank(s) ? '' : String(s).substr(num(evaluate(A[1], env)) - 1, num(evaluate(A[2], env))); }
      case 'LEN': { const s = arg(0); return isBlank(s) ? 0 : String(s).length; }
      case 'UPPER': return String(arg(0) ?? '').toUpperCase();
      case 'LOWER': return String(arg(0) ?? '').toLowerCase();
      case 'CONCATENATE': return String(arg(0) ?? '') + String(arg(1) ?? '');
      case 'REPT': return String(arg(0) ?? '').repeat(num(evaluate(A[1], env)) || 0);
      case 'DIVIDE': { const a = num(evaluate(A[0], env)), b = num(evaluate(A[1], env)); if (isBlank(b) || b === 0) return A[2] ? arg(2) : null; return isBlank(a) ? null : a / b; }
      case 'SUM': case 'AVERAGE': case 'MIN': case 'MAX': case 'COUNT': case 'DISTINCTCOUNT': case 'COUNTROWS':
        return aggregate(fn, node, env);
      case 'SUMX': case 'AVERAGEX': case 'MINX': case 'MAXX': case 'COUNTX':
        return iterate(fn, node, env);
      case 'CALCULATE': {
        if (!A.length) fail('CALCULATE cần ít nhất một đối số.');
        const ctx = applyFilters(env, env.rowCtx.length ? transition(env, env.ctx) : env.ctx, A.slice(1));
        return evaluate(A[0], { ...env, ctx, rowCtx: [] });
      }
      case 'SELECTEDVALUE': {
        const t = evalTable({ k: 'call', fn: 'VALUES', args: [A[0]] }, env);
        return t.rows.length === 1 ? t.rows[0][t.cols[0]] : (A[1] ? arg(1) : null);
      }
      case 'HASONEVALUE': return evalTable({ k: 'call', fn: 'VALUES', args: [A[0]] }, env).rows.length === 1;
      case 'RELATED': {
        const c = A[0];
        if (!c || c.k !== 'col' || !c.table) fail('RELATED cần một cột có tên bảng.');
        const rc = env.rowCtx[env.rowCtx.length - 1];
        if (!rc) fail('RELATED chỉ dùng trong ngữ cảnh dòng (cột tính toán, FILTER, SUMX…).');
        const r = env.M.model.relationships.find(r => r.active && r.to === rc.table && r.from === c.table);
        if (!r) fail(`Cột '${c.col}' của bảng '${c.table}' không tồn tại hoặc không có quan hệ tới bảng '${rc.table}'.`);
        const hit = env.M.tables[c.table].rows.find(x => compare('=', x[r.fromCol], rc.row[r.toCol]));
        return hit ? hit[c.col] : null;
      }
      case 'LOOKUPVALUE': {
        const res = A[0];
        if (!res || res.k !== 'col' || !res.table) fail('LOOKUPVALUE cần cột kết quả có tên bảng.');
        const T = env.M.tables[res.table];
        const pairs = [];
        for (let i = 1; i + 1 < A.length; i += 2) {
          if (A[i].k !== 'col') fail('LOOKUPVALUE: đối số tìm kiếm phải là cột.');
          pairs.push([A[i].col, scalar(evaluate(A[i + 1], env))]);
        }
        const hits = T.rows.filter(r => pairs.every(([c, v]) => compare('=', r[c], v)));
        const vals = [...new Set(hits.map(r => JSON.stringify(r[res.col])))];
        if (vals.length > 1) fail('Một bảng có nhiều giá trị được cung cấp ở chỗ cần một giá trị duy nhất (LOOKUPVALUE tìm thấy nhiều dòng).');
        return vals.length ? JSON.parse(vals[0]) : (A.length % 2 === 0 ? arg(A.length - 1) : null);
      }
      case 'VALUES': case 'DISTINCT': case 'ALL': case 'FILTER': case 'CALCULATETABLE': case 'REMOVEFILTERS':
        return evalTable(node, env);
      case 'CONTAINS': case 'PATHCONTAINS': case 'USEROBJECTID': case 'CUSTOMDATA':
        fail(`Mô phỏng chưa hỗ trợ hàm ${fn}.`);
    }
    fail(`Không nhận ra hàm ${fn}. Mô phỏng hỗ trợ: SUM, DISTINCTCOUNT, COUNTROWS, AVERAGEX, CALCULATE, CALCULATETABLE, VALUES, FILTER, ALL, DIVIDE, IF, LOOKUPVALUE, RELATED, USERPRINCIPALNAME, LEFT, RIGHT…`);
  }

  // ---------- Bảo mật cấp dòng ----------
  /* opts: { roles: [tên role], upn, bypass, noRoleMeans: 'all' | 'none' }
     Trả về { base: {bảng: [dòng]}, olsHidden: Set("T[C]"), error, denied } */
  function security(model, opts) {
    const M = materialize(model);
    const all = Object.fromEntries(Object.entries(M.tables).map(([k, t]) => [k, t.rows]));
    const res = { base: all, olsHidden: new Set(), error: null, denied: false, roles: [] };
    if (opts.bypass) return res;
    const roles = (opts.roles || []).map(n => model.roles.find(r => r.name === n)).filter(Boolean);
    res.roles = roles.map(r => r.name);
    if (!roles.length) {
      if (opts.noRoleMeans === 'none' && model.roles.length) {
        res.denied = true;
        res.base = Object.fromEntries(Object.keys(all).map(k => [k, []]));
      }
      return res;
    }
    const union = {};
    for (const role of roles) {
      const env = mkEnv(M, { upn: opts.upn || '' });
      const ctx = emptyCtx();
      for (const [table, expr] of Object.entries(role.filters || {})) {
        if (!String(expr || '').trim()) continue;
        if (!M.tables[table]) continue;
        let tree;
        try { tree = parse(expr); } catch (e) { res.error = `Role ${role.name}, bảng ${table}: ${e.message}`; continue; }
        try {
          ctx.rows[table] = M.tables[table].rows.filter(r => truthy(evaluate(tree, { ...env, rowCtx: [{ table, row: r }] }))).map(r => r.__id);
        } catch (e) {
          res.error = `Role ${role.name}, bảng ${table}: ${e.message}`;
          ctx.rows[table] = [];
        }
      }
      const { sets } = filteredAll(env, ctx, true);
      for (const [t, rows] of Object.entries(sets)) {
        union[t] = union[t] || new Set();
        rows.forEach(r => union[t].add(r.__id));
      }
    }
    res.base = Object.fromEntries(Object.entries(M.tables).map(([k, t]) => [k, t.rows.filter(r => union[k].has(r.__id))]));
    // OLS: cột bị ẩn khi mọi role đang áp đều đặt None cho cột đó.
    const keys = new Set(roles.flatMap(r => Object.keys(r.ols || {})));
    for (const k of keys) if (roles.every(r => (r.ols || {})[k] === 'None')) res.olsHidden.add(k);
    return res;
  }

  // ---------- Hình ảnh trên báo cáo ----------
  const parseField = f => { const m = /^(.+)\[(.+)\]$/.exec(f); return m ? { table: m[1], col: m[2] } : null; };

  function ctxFromFilters(filters) {
    const ctx = emptyCtx();
    for (const f of filters || []) {
      if (!f || !f.values || !f.values.length) continue;
      const p = parseField(f.field);
      if (p) ctx.cols[p.table + '|' + p.col] = f.values.slice();
    }
    return ctx;
  }

  function relatedLookup(M, fromTable, row, target, col) {
    if (fromTable === target) return row[col];
    const r = M.model.relationships.find(r => r.active && r.to === fromTable && r.from === target);
    if (!r) return undefined;
    const hit = M.tables[target].rows.find(x => x[r.fromCol] === row[r.toCol]);
    return hit ? hit[col] : null;
  }

  function visualData(model, sec, visual, filters) {
    const M = materialize(model);
    const env = mkEnv(M, { base: sec.base, upn: sec.upn || '' });
    const ctx = ctxFromFilters(filters);
    env.ctx = ctx;
    if (sec.denied) return { error: 'denied' };
    const fields = (visual.type === 'slicer' ? [visual.field] : visual.fields || []).filter(Boolean);
    const measures = (visual.type === 'card' ? [visual.measure] : visual.measures || []).filter(Boolean);
    for (const f of fields) {
      if (sec.olsHidden.has(f)) return { error: `Không tìm thấy trường ${f}. Trường này có thể đã bị xóa hoặc bạn không có quyền xem (bảo mật cấp đối tượng).` };
      const p = parseField(f);
      try { colDef(M, p.table, p.col); } catch (e) { return { error: e.message }; }
    }
    for (const m of measures) {
      const def = measureByName(M, m);
      if (!def) return { error: `Không tìm thấy thước đo [${m}].` };
      const used = colsIn(safeParse(def.expr) || {}).map(c => `${c.table}[${c.col}]`);
      const hid = used.find(u => sec.olsHidden.has(u));
      if (hid) return { error: `Thước đo [${m}] dùng trường ${hid} mà bạn không có quyền xem.` };
    }
    try {
      if (visual.type === 'card') {
        if (!measures.length) return { empty: true };
        return { value: evalMeasure(measureByName(M, measures[0]), env) };
      }
      if (visual.type === 'slicer') {
        if (!fields.length) return { empty: true };
        const p = parseField(fields[0]);
        const c2 = cloneCtx(ctx); delete c2.cols[p.table + '|' + p.col];
        const vals = [...new Set(rowsIn(env, p.table, c2).map(r => JSON.stringify(r[p.col] ?? null)))].map(s => JSON.parse(s));
        vals.sort((a, b) => String(a).localeCompare(String(b), 'vi'));
        return { values: vals };
      }
      // Bảng và biểu đồ cột
      if (!fields.length && !measures.length) return { empty: true };
      const ps = fields.map(parseField);
      let tuples = [[]];
      if (ps.length) {
        const tables = [...new Set(ps.map(p => p.table))];
        let anchor = tables.length === 1 ? tables[0] : tables.find(a => tables.every(t => t === a ||
          M.model.relationships.some(r => r.active && r.to === a && r.from === t)));
        if (!anchor) {
          anchor = Object.keys(M.tables).find(a => tables.every(t => t === a || M.model.relationships.some(r => r.active && r.to === a && r.from === t)));
        }
        if (!anchor) return { error: 'Không thể xác định mối quan hệ giữa các trường. Hãy kiểm tra quan hệ trong Model view.' };
        const seen = new Map();
        for (const row of rowsIn(env, anchor, ctx)) {
          const t = ps.map(p => relatedLookup(M, anchor, row, p.table, p.col));
          if (t.some(v => v === undefined)) return { error: 'Không thể xác định mối quan hệ giữa các trường. Hãy kiểm tra quan hệ trong Model view.' };
          seen.set(JSON.stringify(t), t);
        }
        tuples = [...seen.values()];
        tuples.sort((a, b) => { for (let i = 0; i < a.length; i++) { const c = String(a[i]).localeCompare(String(b[i]), 'vi', { numeric: true }); if (c) return c; } return 0; });
      }
      const rows = [];
      for (const t of tuples) {
        const c2 = cloneCtx(ctx);
        ps.forEach((p, i) => { c2.cols[p.table + '|' + p.col] = [t[i]]; });
        const vals = measures.map(m => evalMeasure(measureByName(M, m), { ...env, ctx: c2 }));
        if (measures.length && vals.every(isBlank)) continue;
        rows.push(t.concat(vals));
      }
      const total = measures.length && ps.length ? measures.map(m => evalMeasure(measureByName(M, m), env)) : null;
      return { headers: fields.map(f => parseField(f).col).concat(measures), rows, total, nFields: ps.length };
    } catch (e) {
      if (e instanceof DaxError) return { error: e.message };
      throw e;
    }
  }

  function safeParse(s) { try { return parse(s); } catch (e) { return null; } }

  // Kiểm tra nhanh một biểu thức (thanh công thức, Manage roles).
  function checkMeasure(model, expr) {
    try {
      const M = materialize(model);
      const v = evaluate(parse(expr), mkEnv(M, {}));
      if (isTable(v)) return { error: 'Biểu thức trả về một bảng; thước đo phải trả về một giá trị.' };
      return { value: v };
    } catch (e) { if (e instanceof DaxError) return { error: e.message }; throw e; }
  }

  function checkRule(model, table, expr, upn) {
    try {
      const M = materialize(model);
      if (!M.tables[table]) return { error: `Không tìm thấy bảng ${table}.` };
      const tree = parse(expr);
      const env = mkEnv(M, { upn: upn || 'ban@lab.example' });
      const keep = M.tables[table].rows.filter(r => truthy(evaluate(tree, { ...env, rowCtx: [{ table, row: r }] })));
      return { count: keep.length, total: M.tables[table].rows.length };
    } catch (e) { if (e instanceof DaxError) return { error: e.message }; throw e; }
  }

  function checkCalcColumn(model, table, expr) {
    try {
      const M = materialize(model);
      const tree = parse(expr);
      const r = M.tables[table].rows[0];
      return { sample: r ? scalar(evaluate(tree, mkEnv(M, { rowCtx: [{ table, row: r }] }))) : null };
    } catch (e) { if (e instanceof DaxError) return { error: e.message }; throw e; }
  }

  // Kiểm tra trước khi tạo quan hệ: kiểu dữ liệu, khóa duy nhất ở phía một.
  function checkRelationship(model, from, fromCol, to, toCol) {
    const M = materialize(model);
    const A = M.tables[from], B = M.tables[to];
    if (!A || !B) return { error: 'Chọn đủ hai bảng.' };
    if (from === to) return { error: 'Không thể tạo quan hệ của một bảng với chính nó trong mô phỏng.' };
    const da = A.def.columns.find(c => c.name === fromCol), db = B.def.columns.find(c => c.name === toCol);
    if (!da || !db) return { error: 'Chọn đủ hai cột.' };
    if (da.type !== db.type) return { error: `Không thể tạo quan hệ giữa hai cột khác kiểu dữ liệu (${from}[${fromCol}] là ${da.type}, ${to}[${toCol}] là ${db.type}). Đổi kiểu trong Table view trước.` };
    const va = A.rows.map(r => r[fromCol]), vb = B.rows.map(r => r[toCol]);
    if (va.some(isErr) || vb.some(isErr)) return { error: 'Một trong hai cột có giá trị lỗi do sai kiểu dữ liệu.' };
    const uniqA = new Set(va.map(String)).size === va.length && !va.some(isBlank);
    const uniqB = new Set(vb.map(String)).size === vb.length && !vb.some(isBlank);
    const overlap = va.filter(v => vb.includes(v)).length;
    if (!uniqA && !uniqB) return { warn: 'Cả hai cột đều có giá trị trùng lặp: đây sẽ là quan hệ nhiều–nhiều (Many to many). Bảng danh mục cần một mã duy nhất ở phía một.', cardinality: '*:*' };
    if (!uniqA && uniqB) return { swap: true, cardinality: '1:*', info: `Phía một là ${to}[${toCol}] (giá trị duy nhất). Mô phỏng sẽ đảo chiều cho đúng.` };
    return { cardinality: uniqB ? '1:1' : '1:*', info: overlap ? '' : 'Cảnh báo: hai cột không có giá trị nào trùng nhau.' };
  }

  // ---------- Quyền trên Power BI service ----------
  const WS_RANK = { Admin: 4, Member: 3, Contributor: 2, Viewer: 1 };

  function principalsOf(dir, upn) {
    const u = dir.users.find(x => x.upn === upn);
    const out = new Set([upn]);
    let grew = true;
    while (grew) {
      grew = false;
      for (const g of dir.groups) {
        if (out.has(g.name)) continue;
        const inDyn = g.dynamic === 'internal' && u && u.internal && u.status === 'active';
        if (inDyn || g.members.some(m => out.has(m))) { out.add(g.name); grew = true; }
      }
    }
    return out;
  }

  /* Ai mở được báo cáo, theo đường nào, có bị RLS giới hạn không. */
  function access(svc, upn) {
    const dir = svc.directory;
    const u = dir.users.find(x => x.upn === upn);
    if (!u) return { signIn: false, reason: 'Không tìm thấy tài khoản trong thư mục.' };
    if (u.status !== 'active') return { signIn: false, reason: 'Tài khoản đã bị vô hiệu hóa. Không đăng nhập được.' };
    const P = principalsOf(dir, upn);
    let ws = null, via = null;
    for (const a of svc.workspace.access) if (P.has(a.principal) && (!ws || WS_RANK[a.role] > WS_RANK[ws])) { ws = a.role; via = a.principal; }
    const paths = [];
    if (ws) paths.push(`Workspace: ${ws}${via !== upn ? ' (qua nhóm ' + via + ')' : ''}`);
    let build = ws && ws !== 'Viewer', reshare = ws && ws !== 'Viewer';
    if (svc.app.published && svc.app.audience.some(a => P.has(a))) { paths.push('App'); build = build || svc.app.allowBuild; reshare = reshare || svc.app.allowReshare; }
    for (const s of svc.shares) {
      if ((s.type === 'org' && u.internal) || (s.type === 'people' && s.recipients.some(r => P.has(r)))) {
        paths.push(s.type === 'org' ? 'Liên kết “Mọi người trong tổ chức”' : 'Chia sẻ trực tiếp');
        build = build || s.build; reshare = reshare || s.reshare;
      }
    }
    if (!paths.length) return { signIn: true, open: false, principals: [...P], reason: 'Bạn cần quyền truy cập. Báo cáo chưa được chia sẻ với tài khoản này.' };
    const bypass = !!ws && ws !== 'Viewer';
    const roles = Object.entries(svc.security).filter(([, mem]) => mem.some(m => P.has(m))).map(([r]) => r)
      .filter(r => svc.model && svc.model.roles.some(x => x.name === r));
    return { signIn: true, open: true, ws, paths, bypass, roles, build: !!build, reshare: !!reshare, principals: [...P] };
  }

  global.RLSEngine = {
    DaxError, TYPES, parse, materialize, security, visualData, checkMeasure, checkRule, checkCalcColumn,
    checkRelationship, access, principalsOf, parseField, maskValue, WS_RANK,
    evalMeasureByName(model, sec, name, filters) {
      const M = materialize(model);
      const m = measureByName(M, name);
      if (!m) return null;
      try { return evalMeasure(m, mkEnv(M, { base: sec.base, ctx: ctxFromFilters(filters) })); } catch (e) { return { err: e.message }; }
    },
    rowsOf(model, sec, table) { materialize(model); return (sec.base[table] || []); }
  };
})(window);
