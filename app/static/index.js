Vue.createApp({
  data() {
    const params = new URLSearchParams(location.search);
    let saved = null;
    try { saved = JSON.parse(store.get('session') || 'null'); } catch (e) { saved = null; }
    return {
      logo: LOGO, mode: 'new', code: (params.get('code') || '').toUpperCase(), name: '', rejoin: '',
      err: '', busy: false, saved,
    };
  },
  computed: { hasSession() { return this.saved && this.saved.token; } },
  methods: {
    async join() {
      this.err = ''; this.busy = true;
      try {
        const body = { code: this.code.trim().toUpperCase() };
        if (this.mode === 'rejoin') body.rejoin = this.rejoin.trim().toUpperCase();
        else { body.name = this.name.trim(); }
        const r = await api('POST', '/api/join', body);
        store.set('session', JSON.stringify({ token: r.token, name: r.name, rejoin: r.rejoin, cls: body.code }));
        location.href = '/learn';
      } catch (e) {
        this.err = e.message;
      } finally { this.busy = false; }
    },
  },
}).mount('#app');
