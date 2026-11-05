"""Phòng thí nghiệm AI: phần của từng buổi chỉ mở khi giảng viên bấm, theo từng lớp."""
import os
import tempfile
import unittest
from pathlib import Path


class LabGate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        os.environ['SQLITE_PATH'] = str(Path(cls.temp.name) / 'test.db')
        os.environ['TEACHER_PASSWORD'] = 'test-teacher-only'
        os.environ.pop('DATABASE_URL', None)
        from fastapi.testclient import TestClient
        from app.main import app
        cls.app = app
        cls.TC = TestClient
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

    def post(self, url, data, client=None):
        return (client or self.client).post(url, json=data, headers=self.headers)

    def room(self, name, course='ai-agent'):
        r = self.post('/api/t/classes', {'name': name, 'course': course}).json()
        st = self.post('/api/join', {'code': r['code'], 'name': 'Lan'}).json()
        return r['id'], {'Authorization': 'Bearer ' + st['token']}

    def tabs(self, auth):
        return self.client.get('/api/s/lab', headers=auth).json()['tabs']

    def lab(self, cid, no):
        return self.client.get(f'/api/t/classes/{cid}/state?module={no}').json()['lab']

    def test_open_by_session(self):
        cid, auth = self.room('Lớp A')
        other, other_auth = self.room('Lớp B')

        # mặc định khóa hết
        self.assertEqual(self.tabs(auth), [])
        self.assertEqual(self.lab(cid, 3), {'tab': 'workflow', 'open': False})

        # mở Buổi 3 chỉ mở đúng phần đó, đúng lớp đó, và báo cho học viên qua nhịp đồng bộ
        tick = self.client.get('/api/s/tick', headers=auth).json()['v']
        self.assertEqual(self.post(f'/api/t/classes/{cid}/lab/3', {'open': True}).status_code, 200)
        self.assertNotEqual(self.client.get('/api/s/tick', headers=auth).json()['v'], tick)
        self.assertEqual(self.tabs(auth), ['workflow'])
        self.assertEqual(self.lab(cid, 3)['open'], True)
        self.assertEqual(self.lab(cid, 4)['open'], False)
        self.assertEqual(self.tabs(other_auth), [])

        # mở thêm giữ thứ tự buổi; bấm lặp không lỗi
        self.assertEqual(self.post(f'/api/t/classes/{cid}/lab/2', {'open': True}).status_code, 200)
        self.assertEqual(self.post(f'/api/t/classes/{cid}/lab/2', {'open': True}).status_code, 200)
        self.assertEqual(self.tabs(auth), ['rag', 'workflow'])

        # đóng
        self.assertEqual(self.post(f'/api/t/classes/{cid}/lab/3', {'open': False}).status_code, 200)
        self.assertEqual(self.tabs(auth), ['rag'])

        # mở phần lab không làm lộ file DSL và ngược lại
        self.assertEqual(self.client.get('/api/s/state', headers=auth).json()['files'], [])
        self.assertEqual(self.post(f'/api/t/classes/{cid}/dsl/b4-http', {'shared': True}).status_code, 200)
        self.assertEqual(self.tabs(auth), ['rag'])

    def test_permissions(self):
        cid, auth = self.room('Lớp C')
        anon = self.TC(self.app)
        self.assertEqual(anon.get('/api/s/lab').status_code, 401)
        self.assertEqual(self.post(f'/api/t/classes/{cid}/lab/2', {'open': True}, anon).status_code, 401)
        # học viên không tự mở được
        r = anon.post(f'/api/t/classes/{cid}/lab/2', json={'open': True}, headers={**self.headers, **auth})
        self.assertEqual(r.status_code, 401)
        self.assertEqual(self.tabs(auth), [])

    def test_only_sessions_with_a_lab(self):
        cid, _ = self.room('Lớp D')
        self.assertIsNone(self.lab(cid, 1))
        self.assertEqual(self.post(f'/api/t/classes/{cid}/lab/1', {'open': True}).status_code, 404)
        self.assertEqual(self.post(f'/api/t/classes/{cid}/lab/6', {'open': True}).status_code, 404)
        cid2, auth2 = self.room('Lớp An toàn', 'atdl')
        self.assertEqual(self.post(f'/api/t/classes/{cid2}/lab/2', {'open': True}).status_code, 404)
        self.assertIsNone(self.lab(cid2, 2))
        self.assertEqual(self.tabs(auth2), [])


if __name__ == '__main__':
    unittest.main()
