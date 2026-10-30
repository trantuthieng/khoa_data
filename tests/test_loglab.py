"""Bài mới phải nộp/chấm qua luồng thật và không lộ đáp án qua static/API học viên."""
import hashlib
import json
import os
import tempfile
import unittest
from pathlib import Path


class LogLab(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        os.environ['SQLITE_PATH'] = str(Path(cls.temp.name) / 'loglab.db')
        os.environ['TEACHER_PASSWORD'] = 'loglab-test'
        os.environ.pop('DATABASE_URL', None)
        from fastapi.testclient import TestClient
        from app.main import app
        cls.client = TestClient(app)
        cls.client.__enter__()
        cls.headers = {'X-Requested-With': 'fetch'}

    @classmethod
    def tearDownClass(cls):
        cls.client.__exit__(None, None, None)
        from app import db
        db.engine.dispose()
        cls.temp.cleanup()

    def test_data_and_build_survive_regeneration(self):
        import sys
        sys.path.insert(0, str(Path('tools').resolve()))
        from log_investigation import add_log_investigation
        doc = json.loads(Path('app/content/m09.json').read_text(encoding='utf-8'))
        before = json.dumps(doc)
        self.assertEqual(json.dumps(add_log_investigation(doc)), before)
        self.assertEqual(sum(a['id'] == 'm09-loglab-v1' for a in doc['activities']), 1)
        self.assertTrue(any(a['id'] == 'm09-th10' for a in doc['activities']))
        data = Path('app/static/labs/logs/nhat_ky.jsonl.log').read_bytes()
        rows = [json.loads(x) for x in data.decode('utf-8-sig').splitlines()]
        self.assertEqual(len(rows), 10000)
        self.assertEqual(len({e['source'] for e in rows}), 29)
        original = Path('../nhat_ky_website_10000_dong.jsonl.log')
        if original.exists():
            self.assertEqual(hashlib.sha256(data).digest(), hashlib.sha256(original.read_bytes()).digest())

    def test_student_submission_and_private_answer(self):
        c = self.client
        from fastapi.testclient import TestClient
        from app.main import app
        self.assertEqual(TestClient(app).get('/api/t/answers/m09-loglab-v1').status_code, 401)
        c.post('/api/t/login', json={'password': 'loglab-test'}, headers=self.headers).raise_for_status()
        room = c.post('/api/t/classes', json={'name': 'Log lab'}, headers=self.headers).json()
        st = c.post('/api/join', json={'code': room['code'], 'name': 'Log student'}, headers=self.headers).json()
        auth = {**self.headers, 'Authorization': 'Bearer ' + st['token']}
        base = f'/api/t/classes/{room["id"]}'
        c.post(base + '/view', json={'module': 9, 'unlocked': 999}, headers=self.headers).raise_for_status()
        c.post(base + '/activities/m09-loglab-v1', json={'status': 'open'}, headers=self.headers).raise_for_status()
        public = c.get('/api/s/activity/m09-loglab-v1', headers=auth)
        public.raise_for_status()
        self.assertEqual(len(public.json()['fields']), 5)
        self.assertNotIn('S34', public.text)
        self.assertNotIn('EVT009369', public.text)
        module = c.get('/api/s/module/9', headers=auth)
        self.assertNotIn('thẻ thử thách, lưu ý S43', module.text)
        c.post('/api/s/activity/m09-loglab-v1', json={'payload': {'fields': {'ho_so': 'EVT000315: cần xác minh chính sách MFA'}}}, headers=auth).raise_for_status()
        results = c.get(base + '/activities/m09-loglab-v1/results').json()
        self.assertEqual(len(results['responses']), 1)
        response = results['responses'][0]
        c.post(base + '/activities/m09-loglab-v1', json={'status': 'closed'}, headers=self.headers).raise_for_status()
        c.post(base + f'/responses/{response["id"]}/grade', json={
            'version': response['version'], 'score': 8, 'max_score': 10,
            'feedback': 'Có chuỗi bằng chứng, cần thêm đối chứng.',
        }, headers=self.headers).raise_for_status()
        self.assertIsNone(c.get('/api/s/activity/m09-loglab-v1', headers=auth).json()['response']['score'])
        c.post(base + '/activities/m09-loglab-v1', json={'status': 'revealed'}, headers=self.headers).raise_for_status()
        self.assertEqual(c.get('/api/s/activity/m09-loglab-v1', headers=auth).json()['response']['score'], 8)
        answer = c.get('/api/t/answers/m09-loglab-v1')
        answer.raise_for_status()
        self.assertIn('S60', answer.text)
        self.assertIn('clock skew', answer.text)
        self.assertEqual(c.get('/static/labs/logs/dap_an.md').status_code, 404)
        self.assertEqual(c.get('/static/answer_keys/log_investigation/dap_an.md').status_code, 404)
        self.assertEqual(c.get('/static/labs/logs/index.html').status_code, 200)


if __name__ == '__main__':
    unittest.main()
