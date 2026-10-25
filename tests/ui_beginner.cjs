// Server kiểm thử cục bộ ở cổng 8765; NODE_PATH trỏ tới runtime có playwright.
const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const path = require('node:path');
const os = require('node:os');

(async () => {
  const browser = await chromium.launch({ headless: true, channel: 'msedge' });
  try {
    const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
    const errors = [];
    page.on('pageerror', e => errors.push(e.message));
    await page.goto('http://127.0.0.1:8765/teacher');
    await page.locator('#pw').fill('test-teacher-only');
    await page.getByRole('button', { name: 'Đăng nhập', exact: true }).click();
    await page.waitForFunction(() => document.querySelector('#app').__vue_app__._container._vnode.component.proxy.authed === true);
    const student = await page.evaluate(async () => {
      const vm = document.querySelector('#app').__vue_app__._container._vnode.component.proxy;
      const cls = await api('POST', '/api/t/classes', { name: 'Lớp bài ngắn SQL Python BI' });
      const st = await api('POST', '/api/join', { code: cls.code, name: 'Học viên bài ngắn' });
      await api('PATCH', `/api/t/classes/${cls.id}`, { active_module: 6 });
      await api('POST', `/api/t/classes/${cls.id}/activities/m06-sql01-v1`, { status: 'open' });
      await vm.enterClass({ ...cls, active_module: 6 });
      await vm.openResults('m06-sql01-v1');
      return st;
    });
    const learner = await browser.newPage({ viewport: { width: 1280, height: 1000 } });
    learner.on('pageerror', e => errors.push(e.message));
    await learner.goto('http://127.0.0.1:8765/');
    await learner.evaluate(s => localStorage.setItem('session', JSON.stringify(s)), student);
    await learner.goto('http://127.0.0.1:8765/learn');
    await learner.waitForFunction(() => document.querySelector('#app').__vue_app__._container._vnode.component.proxy.state !== null);
    await learner.evaluate(() => document.querySelector('#app').__vue_app__._container._vnode.component.proxy.openActivity('m06-sql01-v1'));
    await learner.getByText('SELECT ___, ___ FROM customers ORDER BY id;', { exact: true }).waitFor();
    assert.equal(await learner.getByText('Gợi ý chữa bài', { exact: true }).count(), 0);
    const download = await learner.request.get('http://127.0.0.1:8765/static/labs/bai_tap_SQL_Python_BI.zip');
    assert.equal(download.status(), 200);
    assert.ok((await download.body()).length > 1000);
    await learner.locator('.pfield textarea').nth(0).fill('SELECT region, kwh FROM customers ORDER BY id;');
    await learner.locator('.pfield textarea').nth(1).fill('6 dòng; hai cột region, kwh.');
    await learner.locator('.pfield textarea').nth(2).fill('Chỉ lấy cột cần dùng.');
    await learner.locator('.pfield select').selectOption('Đã chạy / đã thao tác');
    await learner.getByRole('button', { name: 'Nộp bài', exact: true }).click();
    await learner.getByText(/Đã nộp lúc/).waitFor();
    await learner.evaluate(() => window.scrollTo(0, 0));
    await learner.screenshot({ path: path.join(os.tmpdir(), 'dienluc-beginner-sql.png'), fullPage: true });
    await page.evaluate(async () => {
      const vm = document.querySelector('#app').__vue_app__._container._vnode.component.proxy;
      await vm.loadResults('m06-sql01-v1', true);
    });
    await page.getByText('Học viên bài ngắn', { exact: true }).first().waitFor();
    await page.locator('input[type="number"]').nth(0).fill('9');
    await page.getByRole('button', { name: 'Lưu điểm và nhận xét', exact: true }).click();
    await page.getByText('9 / 10 điểm', { exact: true }).waitFor();
    await page.evaluate(async () => {
      const vm = document.querySelector('#app').__vue_app__._container._vnode.component.proxy;
      vm.viewModule = 7;
      await vm.changeViewModule();
      vm.localSection = vm.mod.sections.find(s => s.title.startsWith('Chuẩn bị thực hành Power BI')).id;
      vm.results = null;
      vm.scrollTop();
    });
    await page.getByText('Gán thành viên và kiểm tra vai trò trên Power BI service', { exact: true }).waitFor();
    await page.locator('img[src^="/static/labs/"]').evaluateAll(imgs => imgs.forEach(i => i.loading = 'eager'));
    await page.waitForFunction(() => [...document.querySelectorAll('img[src^="/static/labs/"]')].every(i => i.complete && i.naturalWidth > 0));
    await page.screenshot({ path: path.join(os.tmpdir(), 'dienluc-beginner-bi.png'), fullPage: true });
    assert.deepEqual(errors, []);
    console.log('PASS: beginner SQL instructions, ZIP download, personal submission, teacher grade, BI preparation images, no browser errors.');
  } finally { await browser.close(); }
})().catch(e => { console.error(e); process.exitCode = 1; });
