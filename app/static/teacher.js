const app = Vue.createApp({
  components: { ContentBlocks, ActivityForm },
  data() {
    return {
      logo: LOGO, authed: null, password: '', err: '', toast: '',
      statusLabel: STATUS_LABEL, typeLabel: TYPE_LABEL, statuses: ['hidden', 'open', 'closed', 'revealed'],
      segLabel: { hidden: 'Ẩn', open: 'Mở', closed: 'Đóng', revealed: 'Công bố' },
      index: [], classes: [], newName: '', preview: null, rosterText: '', rosterMsg: '',
      cls: null, room: null, viewModule: 1, modCache: {}, localSection: 's0',
      tab: 'acts', results: null, showKey: false, focusGroup: null, present: false, timer: null, rev: 0, polling: false,
      gradeDrafts: {}, grading: {},
      showOutline: false, showActivities: false,
    };
  },
  computed: {
    mod() { return this.modCache[this.viewModule] || null; },
    localSec() { return this.mod ? (this.mod.sections.find(s => s.id === this.localSection) || this.mod.sections[0]) : null; },
    curIdx() {
      if (!this.mod || !this.room || !this.room.view) return 0;
      return Math.max(0, this.mod.sections.findIndex(s => s.id === this.room.view.current_section));
    },
    onlineCount() { return this.room ? this.room.students.filter(s => s.online).length : 0; },
    revealedIds() { return this.room ? this.room.activities.filter(a => a.status === 'revealed').map(a => a.id) : []; },
    avgScore() {
      const r = this.results.responses;
      if (!r.length) return 0;
      return (r.reduce((s, x) => s + (x.score || 0), 0) / r.length).toFixed(1);
    },
    sortedResponses() { return [...this.results.responses].sort((a, b) => (b.score || 0) - (a.score || 0)); },
  },
  methods: {
    fmtTime, themeToggle,
    flash(msg) { this.toast = msg; setTimeout(() => { if (this.toast === msg) this.toast = ''; }, 4000); },
    async call(method, url, body) {
      try { return await api(method, url, body); }
      catch (e) {
        if (e.status === 401) { this.authed = false; this.stop(); }
        else this.flash(e.message);
        throw e;
      }
    },
    async check() {
      try { await api('GET', '/api/t/me'); this.authed = true; await this.loadClasses(); }
      catch (e) { this.authed = false; }
    },
    async login() {
      this.err = '';
      try { await api('POST', '/api/t/login', { password: this.password }); this.password = ''; this.authed = true; await this.loadClasses(); this.restore(); }
      catch (e) { this.err = e.message; }
    },
    async logout() { await api('POST', '/api/t/logout'); this.authed = false; this.cls = null; this.room = null; this.stop(); },
    async loadClasses() {
      this.index = await this.call('GET', '/api/modules');
      this.classes = await this.call('GET', '/api/t/classes');
    },
    async createClass() {
      const c = await this.call('POST', '/api/t/classes', { name: this.newName.trim() });
      this.newName = '';
      await this.loadClasses();
      this.enterClass(c);
    },
    async archive(c) {
      await this.call('PATCH', '/api/t/classes/' + c.id, { archived: !c.archived });
      await this.loadClasses();
    },
    async removeClass(c) {
      if (prompt('Xóa lớp và toàn bộ bài nộp? Thao tác này không thể hoàn tác. Nhập mã lớp ' + c.code + ' để xác nhận.') !== c.code) return;
      await this.call('DELETE', '/api/t/classes/' + c.id);
      await this.loadClasses();
    },
    async previewModule(no) {
      this.preview = await this.loadMod(no);
    },
    kindTag(s) { return { teacher: 'Chỉ giảng viên', review: 'Thành bài tập', exam: 'Thành bài tập', practice: 'Thực hành' }[s.kind] || ''; },
    async loadMod(no) {
      if (!this.modCache[no]) this.modCache = { ...this.modCache, [no]: await this.call('GET', '/api/t/module/' + no) };
      return this.modCache[no];
    },

    // ---------- phòng học ----------
    async enterClass(c) {
      this.cls = c; this.viewModule = c.active_module; this.results = null;
      store.set('teacher_class', String(c.id));
      await this.loadMod(this.viewModule);
      await this.refresh(true);
      this.start();
    },
    leaveClass() { this.cls = null; this.room = null; this.stop(); store.del('teacher_class'); this.loadClasses(); },
    async restore() {
      const id = Number(store.get('teacher_class'));
      const c = this.classes.find(x => x.id === id);
      if (c) this.enterClass(c);
    },
    start() { this.stop(); this.timer = setInterval(() => this.refresh(false), 3000); },
    stop() { if (this.timer) clearInterval(this.timer); this.timer = null; },
    async refresh(jump) {
      if (!this.cls) return;
      // không chồng request khi mạng chậm; bỏ kết quả cũ nếu vừa có thao tác mới
      if (!jump && this.polling) return;
      const rev = this.rev, mod = this.viewModule;
      let r;
      this.polling = true;
      try { r = await this.call('GET', `/api/t/classes/${this.cls.id}/state?module=${mod}`); } catch (e) { return; } finally { this.polling = false; }
      if (!jump && (rev !== this.rev || mod !== this.viewModule)) return;
      this.room = r; this.cls = r.cls;
      if (jump && r.view) this.localSection = r.view.current_section;
      if (this.results) await this.loadResults(this.results.activity.id, true);
    },
    async changeViewModule() {
      this.results = null;
      await this.loadMod(this.viewModule);
      await this.refresh(true);
      if (!this.room.view) this.localSection = 's0';
    },
    async setActive(no) {
      await this.call('PATCH', '/api/t/classes/' + this.cls.id, { active_module: no });
      await this.refresh(true);
      this.flash('Lớp đã chuyển sang buổi ' + no);
    },
    async setView(patch) {
      // hiện ngay trên giao diện, server xác nhận sau
      this.rev++;
      if (this.room.view) this.room.view = { ...this.room.view, ...patch };
      try {
        const v = await this.call('POST', `/api/t/classes/${this.cls.id}/view`, { module: this.viewModule, ...patch });
        this.rev++;
        this.room.view = v;
        return v;
      } catch (e) { this.rev++; this.refresh(true); throw e; }
    },
    async presentSection(id) {
      await this.setView({ current_section: id });
      this.localSection = id;
      this.scrollTop();
    },
    presentIdx(i) {
      if (!this.mod || i < 0 || i >= this.mod.sections.length) return;
      this.presentSection(this.mod.sections[i].id);
    },
    studentHidden(s) { return !['content', 'practice'].includes(s.kind); },
    isLocked(s, i) { return this.viewModule !== 0 && this.room.view && i > this.room.view.unlocked; },
    secIcon(s, i) {
      if (this.room.view && s.id === this.room.view.current_section && this.viewModule === this.cls.active_module) return '▶';
      if (this.studentHidden(s)) return '👁';
      if (this.viewModule === 0) return '✓';
      return this.isLocked(s, i) ? '🔒' : '✓';
    },
    scrollTop() { window.scrollTo({ top: 0 }); },
    actStatus(id) { const a = this.room.activities.find(x => x.id === id); return a ? a.status : 'hidden'; },
    async setStatus(id, status) {
      const a = this.room.activities.find(x => x.id === id);
      const before = a && a.status;
      this.rev++;
      if (a) a.status = status;
      try {
        await this.call('POST', `/api/t/classes/${this.cls.id}/activities/${id}`, { status });
      } catch (e) { if (a) a.status = before; throw e; } finally { this.rev++; }
      if (this.results && this.results.activity.id === id) this.results.status = status;
    },
    async openResults(id) { this.focusGroup = null; this.showKey = false; this.showActivities = false; await this.loadResults(id, false); this.scrollTop(); },
    async loadResults(id, silent) {
      try {
        const data = await this.call('GET', `/api/t/classes/${this.cls.id}/activities/${id}/results`);
        if (silent && (!this.results || this.results.activity.id !== id)) return;
        this.results = data;
      }
      catch (e) { if (!silent) throw e; }
    },
    gradeDraft(r) {
      if (!this.gradeDrafts[r.id]) this.gradeDrafts[r.id] = {
        version: r.version, score: r.score ?? '', max_score: r.max_score ?? 10, feedback: r.feedback || '',
      };
      return this.gradeDrafts[r.id];
    },
    async saveGrade(r) {
      const draft = this.gradeDraft(r);
      if (draft.score === '' || draft.score === null || draft.max_score === '' || draft.max_score === null) {
        this.flash('Vui lòng nhập điểm và điểm tối đa trước khi lưu.'); return;
      }
      this.grading[r.id] = true;
      try {
        await this.call('POST', `/api/t/classes/${this.cls.id}/responses/${r.id}/grade`, {
          ...draft, score: Number(draft.score), max_score: Number(draft.max_score),
        });
        await this.loadResults(this.results.activity.id, true);
        delete this.gradeDrafts[r.id];
        this.flash(this.results.status === 'revealed' ? 'Đã cập nhật điểm và nhận xét cho bài đã công bố.' : 'Đã lưu điểm và nhận xét. Học viên sẽ xem được khi bạn chọn Công bố.');
      } catch (e) { /* call đã hiển thị lỗi; giữ bản chấm đang nhập */ }
      finally { this.grading[r.id] = false; }
    },
    reloadGrade(r) { delete this.gradeDrafts[r.id]; },
    goSectionOf(a) { this.localSection = a.section; this.results = null; this.scrollTop(); },
    practicePayload(r) { return initPayload(this.results.activity, r.payload); },
    isCorrect(q, o) { return Array.isArray(q.correct) ? q.correct.includes(o.key) : q.correct === o.key; },
    qStat(q) { return this.results.stats && this.results.stats.questions[q.id]; },
    optCount(q, o) { const s = this.qStat(q); return s ? s.counts[o.key] : 0; },
    optPct(q, o) { const s = this.qStat(q); return s && s.n ? Math.round(100 * s.counts[o.key] / s.n) : 0; },
    pctCorrect(q) { const s = this.qStat(q); return s && s.n ? Math.round(100 * s.correct / s.n) : 0; },
    async delResponse(r) {
      if (!confirm('Xóa bài nộp này? Điểm và nhận xét cũng sẽ bị xóa. Học viên chỉ có thể nộp lại khi bài được mở.')) return;
      await this.call('DELETE', `/api/t/classes/${this.cls.id}/responses/${r.id}`);
      await this.loadResults(this.results.activity.id, true);
    },
    async importRoster() {
      const r = await this.call('POST', `/api/t/classes/${this.cls.id}/roster`, { text: this.rosterText });
      this.rosterMsg = `Đã tạo ${r.added} tài khoản, cập nhật ${r.updated}.` + (r.errors.length ? '\n' + r.errors.join('\n') : '');
      if (!r.errors.length) this.rosterText = '';
      this.refresh(false);
    },
    async kick(s) {
      if (!confirm('Xóa học viên ' + s.name + ' khỏi lớp? Toàn bộ bài nộp, điểm và nhận xét của học viên này cũng sẽ bị xóa.')) return;
      await this.call('DELETE', `/api/t/classes/${this.cls.id}/students/${s.id}`);
      this.refresh(false);
    },
    togglePresent() {
      this.present = !this.present;
      const el = document.documentElement;
      if (this.present && el.requestFullscreen) el.requestFullscreen().catch(() => { /* không cho toàn màn hình: vẫn trình chiếu trong cửa sổ */ });
      else if (!this.present && document.fullscreenElement) document.exitFullscreen().catch(() => {});
    },
    onKey(e) {
      if (!this.cls || !this.room || ['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement.tagName)) return;
      if (this.viewModule !== this.cls.active_module || this.results) return;
      if (['ArrowRight', 'PageDown'].includes(e.key)) { e.preventDefault(); this.presentIdx(this.curIdx + 1); }
      if (['ArrowLeft', 'PageUp'].includes(e.key)) { e.preventDefault(); this.presentIdx(this.curIdx - 1); }
      if (e.key === 'Escape' && this.present) this.present = false;
    },
  },
  watch: {
    present(v) { document.body.classList.toggle('present', v); },
  },
  async mounted() {
    await this.check();
    if (this.authed) this.restore();
    window.addEventListener('keydown', this.onKey);
    document.addEventListener('fullscreenchange', () => { if (!document.fullscreenElement && this.present) this.present = false; });
  },
});
app.mount('#app');
