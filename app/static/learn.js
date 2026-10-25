let session = null;
try { session = JSON.parse(store.get('session') || 'null'); } catch (e) { session = null; }
if (!session || !session.token) location.replace('/');

const sapi = (method, url, body) => api(method, url, body, session && session.token);

const app = Vue.createApp({
  components: { ContentBlocks, ActivityForm },
  data() {
    return {
      logo: LOGO, session, state: null, loadErr: '', statusLabel: STATUS_LABEL, typeLabel: TYPE_LABEL,
      mode: 'lesson', viewModule: null, sectionId: null, modules: {},
      activity: null, payload: null, dirty: false, saving: false, saveErr: '',
      toast: null, showSide: false, showMe: false,
      lastTeacherSection: null, lastActive: null, prevStatus: null,
    };
  },
  computed: {
    moduleData() { const m = this.modules[this.viewModule]; return m ? m.data : null; },
    sections() { return this.moduleData ? this.moduleData.sections : []; },
    section() {
      return this.sections.find(s => s.id === this.sectionId) || this.sections[this.sections.length - 1] || null;
    },
    secIdx() { return this.section ? this.sections.indexOf(this.section) : -1; },
    prevSection() { return this.secIdx > 0 ? this.sections[this.secIdx - 1] : null; },
    nextSection() { return this.secIdx >= 0 && this.secIdx < this.sections.length - 1 ? this.sections[this.secIdx + 1] : null; },
    following() { return this.state ? this.state.view.follow : null; },
    teacherSection() { return this.state ? this.state.view.current_section : null; },
    teacherSectionTitle() {
      const m = this.state && this.modules[this.state.view.module];
      const s = m && m.data.sections.find(x => x.id === this.teacherSection);
      return s ? s.title : '';
    },
    openCount() { return this.state ? this.state.activities.filter(a => a.status === 'open' && !a.submitted).length : 0; },
  },
  methods: {
    fmtTime, themeToggle,
    activityById(id) { return this.state && this.state.activities.find(a => a.id === id); },
    async loadModule(no) {
      const key = this.state.content_keys[no];
      const cached = this.modules[no];
      if (cached && cached.key === key) return;
      const data = await sapi('GET', '/api/s/module/' + no);
      this.modules = { ...this.modules, [no]: { key, data } };
    },
    async poll() {
      let s;
      try {
        s = await sapi('GET', '/api/s/state');
      } catch (e) {
        if (e.status === 401) { store.del('session'); location.replace('/'); return; }
        this.loadErr = 'Kết nối bị gián đoạn. Hệ thống đang kết nối lại…';
        return;
      }
      this.loadErr = '';
      const first = !this.state;
      this.state = s;
      const v = s.view;
      if (first) { this.viewModule = v.module; this.sectionId = v.current_section; }
      if (!first && v.module !== this.lastActive && v.follow) { this.viewModule = v.module; this.sectionId = v.current_section; if (this.mode !== 'activity') this.mode = 'lesson'; }
      if (!s.modules.some(m => m.no === this.viewModule)) this.viewModule = v.module;
      try {
        await this.loadModule(this.viewModule);
        if (v.module !== this.viewModule) await this.loadModule(v.module);
      } catch (e) { /* lần poll sau thử lại */ }
      if (!first && v.follow && v.module === this.viewModule && v.current_section !== this.lastTeacherSection && this.mode === 'lesson') {
        this.goSection(v.current_section);
      }
      this.lastTeacherSection = v.current_section;
      this.lastActive = v.module;

      // thông báo bài tập mới mở / công bố đáp án
      const st = {};
      for (const a of s.activities) st[a.id] = a.status;
      if (this.prevStatus) {
        for (const a of s.activities) {
          const before = this.prevStatus[a.id];
          if (this.mode === 'activity' && this.activity && this.activity.id === a.id) continue;
          if (a.status === 'open' && before !== 'open') this.toast = { text: 'Giảng viên vừa mở: ' + a.title, activity: a.id };
          else if (a.status === 'revealed' && before !== 'revealed') this.toast = { text: 'Đã công bố đáp án: ' + a.title, activity: a.id };
        }
      }
      this.prevStatus = st;

      // làm mới bài đang mở khi trạng thái đổi
      if (this.mode === 'activity' && this.activity) {
        const now = st[this.activity.id];
        if (now && (now !== this.activity.status || now === 'revealed')) await this.openActivity(this.activity.id, true);
      }
    },
    goSection(id, module) {
      if (module !== undefined && module !== this.viewModule) { this.viewModule = module; this.loadModule(module); }
      this.sectionId = id;
      this.mode = 'lesson';
      window.scrollTo({ top: 0 });
    },
    onModuleChange() {
      this.mode = 'lesson';
      this.sectionId = this.viewModule === this.state.view.module ? this.state.view.current_section : 's0';
      this.loadModule(this.viewModule);
    },
    async openActivity(id, keepScroll) {
      if (this.dirty && this.activity && this.activity.id !== id && !confirm('Bài hiện tại có thay đổi chưa nộp. Bạn có muốn chuyển sang bài khác?')) return;
      try {
        const a = await sapi('GET', '/api/s/activity/' + id);
        const wasDirty = this.dirty && this.activity && this.activity.id === id;
        this.activity = a;
        if (!wasDirty || a.status !== 'open') { this.payload = initPayload(a, a.response && a.response.payload); this.dirty = false; }
        if (wasDirty && a.status !== 'open') this.saveErr = 'Bài đã ngừng nhận bài nộp. Thay đổi cuối của bạn chưa được nộp.';
        this.mode = 'activity';
        if (!keepScroll) window.scrollTo({ top: 0 });
      } catch (e) { this.toast = { text: e.message }; }
    },
    async save() {
      this.saving = true; this.saveErr = '';
      try {
        const r = await sapi('POST', '/api/s/activity/' + this.activity.id, { payload: this.payload });
        this.activity.response = r.response;
        this.dirty = false;
        const a = this.activityById(this.activity.id);
        if (a) a.submitted = true;
      } catch (e) {
        this.saveErr = e.message;
      } finally { this.saving = false; }
    },
    logout() {
      const msg = this.session.rejoin
        ? 'Rời lớp trên thiết bị này? Hãy lưu mã vào lại cá nhân trước khi rời lớp: ' + this.session.rejoin
        : 'Rời lớp trên thiết bị này? Bạn có thể vào lại bằng số điện thoại.';
      if (!confirm(msg)) return;
      store.del('session');
      location.replace('/');
    },
  },
  mounted() {
    this.poll();
    const loop = () => setTimeout(async () => { await this.poll(); loop(); }, document.hidden ? 10000 : 3000);
    loop();
    window.addEventListener('beforeunload', e => { if (this.dirty) { e.preventDefault(); e.returnValue = ''; } });
  },
});
app.mount('#app');
