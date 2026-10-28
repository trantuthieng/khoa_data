"""Kiểm tra luồng nộp cá nhân, chấm điểm và bảo vệ đáp án."""
import importlib
import json
import os
import tempfile
import unittest
from pathlib import Path


class TeachingFlow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        os.environ['SQLITE_PATH'] = str(Path(cls.temp.name) / 'test.db')
        os.environ['TEACHER_PASSWORD'] = 'test-teacher-only'
        os.environ.pop('DATABASE_URL', None)
        from fastapi.testclient import TestClient
        from app.main import app
        cls.client = TestClient(app)
        cls.client.__enter__()
        cls.headers = {'X-Requested-With': 'fetch'}
        cls.client.post('/api/t/login', json={'password': 'test-teacher-only'}, headers=cls.headers).raise_for_status()

    @classmethod
    def tearDownClass(cls):
        cls.client.__exit__(None, None, None)
        from app import db
        db.engine.dispose()
        cls.temp.cleanup()

    def post(self, url, data, headers=None):
        return self.client.post(url, json=data, headers=headers or self.headers)

    def test_open_all_includes_sections_added_later(self):
        room = self.post('/api/t/classes', {'name': 'Open all'}).json()
        st = self.post('/api/join', {'code': room['code'], 'name': 'Chi'}).json()
        n = len(json.loads(Path('app/content/m07.json').read_text(encoding='utf-8'))['sections'])
        view = self.post(f'/api/t/classes/{room["id"]}/view', {'module': 7, 'unlocked': n - 1}).json()
        self.assertGreater(view['unlocked'], n)
        sections = self.client.get('/api/s/module/7', headers={'Authorization': 'Bearer ' + st['token']}).json()['sections']
        self.assertTrue(any(s.get('activity') == 'm07-rlslab-v1' for s in sections))

    def test_individual_grading_and_revision(self):
        room = self.post('/api/t/classes', {'name': 'Test individual'}).json()
        cid = room['id']
        alice = self.post('/api/join', {'code': room['code'], 'name': 'Alice'}).json()
        bob = self.post('/api/join', {'code': room['code'], 'name': 'Bob'}).json()
        ah = {'Authorization': 'Bearer ' + alice['token']}
        bh = {'Authorization': 'Bearer ' + bob['token']}
        aid = 'm01-case-v2'
        base = f'/api/t/classes/{cid}'
        self.post(base + f'/activities/{aid}', {'status': 'open'}).raise_for_status()
        self.assertEqual(self.post('/api/s/activity/' + aid, {'payload': {'fields': {'part1': '  '}}}, ah).status_code, 400)
        self.post('/api/s/activity/' + aid, {'payload': {'fields': {'part1': 'Alice response'}}}, ah).raise_for_status()
        result = self.client.get(base + f'/activities/{aid}/results').json()
        self.assertEqual(len(result['responses']), 1)
        self.assertEqual([s['name'] for s in result['not_submitted']], ['Bob'])
        self.assertIsNone(self.client.get('/api/s/activity/' + aid, headers=bh).json()['response'])
        r = result['responses'][0]
        grade = base + f'/responses/{r["id"]}/grade'
        payload = {'version': r['version'], 'score': 8.5, 'max_score': 10, 'feedback': 'Good reasoning'}
        self.assertEqual(self.post(grade, dict(payload, score=11)).status_code, 400)
        self.post(grade, payload).raise_for_status()
        hidden = self.client.get('/api/s/activity/' + aid, headers=ah).json()['response']
        self.assertIsNone(hidden['score'])
        self.assertEqual(hidden['feedback'], '')
        self.post(base + f'/activities/{aid}', {'status': 'revealed'}).raise_for_status()
        self.assertEqual(self.post('/api/s/activity/' + aid, {'payload': {'fields': {'part1': 'Late'}}}, ah).status_code, 409)
        shown = self.client.get('/api/s/activity/' + aid, headers=ah).json()['response']
        self.assertEqual(shown['score'], 8.5)
        self.assertEqual(shown['feedback'], 'Good reasoning')
        export = self.client.get(base + '/export.csv').text
        self.assertIn('8.5', export)
        self.assertIn('Good reasoning', export)
        self.post(base + f'/activities/{aid}', {'status': 'open'})
        self.post('/api/s/activity/' + aid, {'payload': {'fields': {'part1': 'Revised'}}}, ah).raise_for_status()
        self.assertEqual(self.post(grade, payload).status_code, 409)
        revised = self.client.get(base + f'/activities/{aid}/results').json()['responses'][0]
        self.assertIsNone(revised['score'])
        other = self.post('/api/t/classes', {'name': 'Other class'}).json()
        self.assertEqual(self.post(f'/api/t/classes/{other["id"]}/responses/{r["id"]}/grade', payload).status_code, 404)
        self.post('/api/t/logout', {})
        self.assertEqual(self.post(grade, payload).status_code, 401)
        self.post('/api/t/login', {'password': 'test-teacher-only'}).raise_for_status()

    def test_board_submission(self):
        room = self.post('/api/t/classes', {'name': 'Test board'}).json()
        alice = self.post('/api/join', {'code': room['code'], 'name': 'Alice'}).json()
        ah = {'Authorization': 'Bearer ' + alice['token']}
        aid = 'm03-th3'
        self.post(f'/api/t/classes/{room["id"]}/activities/{aid}', {'status': 'open'}).raise_for_status()
        act = self.client.get('/api/s/activity/' + aid, headers=ah).json()
        self.assertEqual(act['fields'][0]['type'], 'board')
        # chỉ kéo module, nối dây mà chưa ghi chữ: chưa tính là bài làm
        moved = {'nodes': [{'id': 'r_nv', 'kind': 'role', 'x': 60, 'y': 90, 'text': ''}],
                 'links': [{'id': 'l1', 'from': 'r_nv', 'to': 'p_xem'}]}
        self.assertEqual(self.post('/api/s/activity/' + aid, {'payload': {'fields': {'ma_tran_bang': moved}}}, ah).status_code, 400)
        moved['links'][0]['pham_vi'] = 'KH đơn vị mình'
        self.post('/api/s/activity/' + aid, {'payload': {'fields': {'ma_tran_bang': moved}}}, ah).raise_for_status()
        saved = self.client.get('/api/s/activity/' + aid, headers=ah).json()['response']['payload']
        self.assertEqual(saved['fields']['ma_tran_bang']['links'][0]['pham_vi'], 'KH đơn vị mình')

    def test_teacher_answer_keys(self):
        from app.answer_keys import ANSWER_KEYS
        from app.content import ACTIVITIES
        for aid, key in ANSWER_KEYS.items():
            fields = {f['key']: f for f in ACTIVITIES[aid]['fields']}
            self.assertEqual(set(key['fields']), set(fields), aid)
            for fk, v in key['fields'].items():
                f = fields[fk]
                if f['type'] != 'board':
                    continue
                # bài mẫu chỉ dùng module có trong bảng, đủ module dựng sẵn, dây nối tới module có thật
                kinds = {k['kind']: k for k in f['kinds']}
                ids = {n['id'] for n in v['nodes']}
                self.assertTrue({n['id'] for n in f['nodes']} <= ids, aid)
                for n in v['nodes']:
                    self.assertIn(n['kind'], kinds, n['id'])
                    if 'tag' in n:
                        self.assertIn(n['tag'], kinds[n['kind']]['options'], n['id'])
                    w, h = f['size']
                    self.assertTrue(0 <= n['x'] <= w - 236 and 0 <= n['y'] < h, n['id'])
                for l in v['links']:
                    self.assertTrue(l['from'] in ids and l['to'] in ids, l['id'])
        aid = next(iter(ANSWER_KEYS))
        self.assertEqual(self.client.get('/api/t/answers').json()[0]['id'], aid)
        self.assertIn('fields', self.client.get('/api/t/answers/' + aid).json())
        self.assertEqual(self.client.get('/api/t/answers/m01-nope').status_code, 404)
        # học viên không nhận được đáp án giảng viên
        room = self.post('/api/t/classes', {'name': 'Test answer key'}).json()
        alice = self.post('/api/join', {'code': room['code'], 'name': 'Alice'}).json()
        self.post(f'/api/t/classes/{room["id"]}/activities/{aid}', {'status': 'revealed'}).raise_for_status()
        act = self.client.get('/api/s/activity/' + aid, headers={'Authorization': 'Bearer ' + alice['token']}).text
        self.assertNotIn(ANSWER_KEYS[aid]['summary'][:40], act)
        self.client.cookies.clear()
        self.assertEqual(self.client.get('/api/t/answers/' + aid).status_code, 401)
        self.post('/api/t/login', {'password': 'test-teacher-only'}).raise_for_status()

    def test_supplemental_content_and_answer_gates(self):
        from app.content import MODULES, ACTIVITIES, public_activity, student_module, score
        exam = {q['text'] for q in ACTIVITIES['m10-exam']['questions']}
        self.assertEqual(len(exam), 20)
        for no in range(1, 11):
            aid = f'm{no:02d}-case-v2'
            a = ACTIVITIES[aid]
            if no == 3:
                # buổi 3 làm trên không gian bảng
                self.assertEqual(a['fields'][0]['type'], 'board')
            else:
                self.assertEqual(len(a['fields']), 3)
            for status in ('open', 'closed'):
                m = student_module(no, None, set())
                section = next(s for s in m['sections'] if s.get('activity') == aid)
                self.assertFalse(any(b.get('reveal') for b in section['blocks']))
            shown = student_module(no, None, {aid})
            self.assertTrue(any(b.get('reveal') == aid for s in shown['sections'] for b in s['blocks']))
            if no < 10:
                quiz = ACTIVITIES[f'm{no:02d}-check-v2']
                self.assertEqual(len(quiz['questions']), 2)
                self.assertFalse(exam.intersection(q['text'] for q in quiz['questions']))
                self.assertTrue(all('correct' not in q and 'explain' not in q for q in public_activity(quiz, 'open')['questions']))
                answers = {q['id']: q['correct'] for q in quiz['questions']}
                self.assertEqual(score(quiz, {'answers': answers}), (2, 2))
        for no, aid in ((1, 'm01-cia'), (9, 'm09-th10')):
            tagged = [b for s in MODULES[no]['sections'] for b in s['blocks'] if b.get('reveal') == aid]
            self.assertTrue(tagged)


if __name__ == '__main__':
    unittest.main()
