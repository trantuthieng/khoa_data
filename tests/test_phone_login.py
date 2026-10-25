"""Kiểm tra tạo tài khoản từ danh sách và đăng nhập bằng số điện thoại."""
import os
import tempfile
import unittest
from pathlib import Path


class PhoneLogin(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # app.db giữ kết nối theo tiến trình: không xóa thư mục để các file test khác dùng tiếp
        os.environ['SQLITE_PATH'] = str(Path(tempfile.mkdtemp()) / 'test.db')
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

    def post(self, url, data, headers=None):
        return self.client.post(url, json=data, headers=headers or self.headers)

    def test_roster_and_phone_login(self):
        room = self.post('/api/t/classes', {'name': 'Lớp điện thoại'}).json()
        cid = room['id']
        roster = ('Người Mẫu A\t0900000001\tKỹ sư\tĐơn vị X\n'
                  'Người Mẫu B, 900000002, Đơn vị Y\n'
                  'Thiếu số điện thoại\n')
        r = self.post(f'/api/t/classes/{cid}/roster', {'text': roster}).json()
        self.assertEqual((r['added'], r['updated'], len(r['errors'])), (2, 0, 1))
        again = self.post(f'/api/t/classes/{cid}/roster', {'text': 'Người Mẫu A2, 0900000001, Đơn vị Z'}).json()
        self.assertEqual((again['added'], again['updated']), (0, 1))

        from app import db
        stored = db.q('SELECT * FROM students WHERE class_id=:c', c=cid)
        self.assertTrue(all('0900000001' not in str(v) for s in stored for v in s.values()))

        a = self.post('/api/join', {'phone': '090 000 0001'}).json()
        self.assertEqual((a['name'], a['cls'], a['rejoin']), ('Người Mẫu A2', room['code'], None))
        st = self.client.get('/api/s/state', headers={'Authorization': 'Bearer ' + a['token']})
        self.assertEqual(st.status_code, 200)
        b = self.post('/api/join', {'phone': '+84900000002'})
        self.assertEqual(b.status_code, 200)

        # đăng nhập trên thiết bị khác làm phiên cũ hết hiệu lực
        self.post('/api/join', {'phone': '0900000001'}).raise_for_status()
        self.assertEqual(self.client.get('/api/s/state', headers={'Authorization': 'Bearer ' + a['token']}).status_code, 401)

        self.assertEqual(self.post('/api/join', {'phone': '0900000999'}).status_code, 404)
        self.assertEqual(self.post('/api/join', {'phone': '123'}).status_code, 400)
        students = self.client.get(f'/api/t/classes/{cid}/state', headers=self.headers).json()['students']
        self.assertTrue(all(s['by_phone'] for s in students))

    def test_tick_changes_only_when_teacher_acts(self):
        room = self.post('/api/t/classes', {'name': 'Lớp nhịp'}).json()
        st = self.post('/api/join', {'code': room['code'], 'name': 'Người Mẫu C'}).json()
        h = {'Authorization': 'Bearer ' + st['token']}
        v1 = self.client.get('/api/s/tick', headers=h).json()['v']
        self.assertEqual(self.client.get('/api/s/tick', headers=h).json()['v'], v1)
        self.post(f"/api/t/classes/{room['id']}/view", {'module': 1, 'current_section': 's5'}).raise_for_status()
        self.assertNotEqual(self.client.get('/api/s/tick', headers=h).json()['v'], v1)
        self.assertEqual(self.client.get('/api/s/tick', headers={'Authorization': 'Bearer sai'}).status_code, 401)


if __name__ == '__main__':
    unittest.main()
