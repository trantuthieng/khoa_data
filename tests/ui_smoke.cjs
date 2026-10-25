// Chạy với NODE_PATH trỏ tới runtime có playwright. Chỉ dùng server kiểm thử cục bộ.
const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const os = require('node:os');
const path = require('node:path');

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
    const setup = await page.evaluate(async () => {
      const vm = document.querySelector('#app').__vue_app__._container._vnode.component.proxy;
      const cls = await api('POST', '/api/t/classes', { name: 'Lớp kiểm thử giao diện' });
      const student = await api('POST', '/api/join', { code: cls.code, name: 'Học viên thử' });
      await api('POST', `/api/t/classes/${cls.id}/activities/m01-case-v2`, { status: 'open' });
      await api('POST', '/api/s/activity/m01-case-v2', { payload: { fields: { part1: 'Bài cá nhân', part2: 'Cách xử lý', part3: 'Cách kiểm tra' } } }, student.token);
      await vm.enterClass(cls);
      await vm.openResults('m01-case-v2');
      return { cls, student };
    });
    await page.getByText('Theo dõi và chấm bài cá nhân', { exact: true }).waitFor();
    const numbers = page.locator('input[type="number"]');
    await numbers.nth(0).fill('8.5');
    await page.getByPlaceholder('Điểm làm tốt và phần cần sửa').fill('Lý do rõ; bổ sung cách kiểm chứng.');
    await page.getByRole('button', { name: 'Lưu điểm và nhận xét', exact: true }).click();
    await page.getByText('8.5 / 10 điểm', { exact: true }).waitFor();
    // Để qua một lần polling: điểm đã chấm và mẫu nhập phải giữ đúng.
    await page.waitForTimeout(3300);
    assert.equal(await numbers.nth(0).inputValue(), '8.5');
    await page.screenshot({ path: path.join(os.tmpdir(), 'dienluc-teacher-review.png'), fullPage: true });
    await page.evaluate(async () => {
      const vm = document.querySelector('#app').__vue_app__._container._vnode.component.proxy;
      await vm.setStatus('m01-case-v2', 'revealed');
    });
    const learner = await browser.newPage({ viewport: { width: 1280, height: 900 } });
    learner.on('pageerror', e => errors.push(e.message));
    await learner.goto('http://127.0.0.1:8765/');
    await learner.evaluate(session => localStorage.setItem('session', JSON.stringify(session)), setup.student);
    await learner.goto('http://127.0.0.1:8765/learn');
    await learner.waitForFunction(() => document.querySelector('#app').__vue_app__._container._vnode.component.proxy.state !== null);
    await learner.evaluate(() => document.querySelector('#app').__vue_app__._container._vnode.component.proxy.openActivity('m01-case-v2'));
    await learner.getByText('8.5/10', { exact: true }).waitFor();
    await learner.getByText('Nhận xét của giảng viên: Lý do rõ; bổ sung cách kiểm chứng.', { exact: true }).waitFor();
    await learner.screenshot({ path: path.join(os.tmpdir(), 'dienluc-student-review.png'), fullPage: true });
    assert.deepEqual(errors, []);
    console.log('PASS: teacher grades, polling preserves draft, learner sees published score and feedback, no browser errors.');
  } finally { await browser.close(); }
})().catch(e => { console.error(e); process.exitCode = 1; });
