"""Mỗi lớp học theo một khóa: lớp AI Agent chỉ thấy nội dung và bài tập của khóa AI Agent."""
import os
import tempfile
import unittest
from pathlib import Path


class Courses(unittest.TestCase):
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

    def post(self, url, data):
        return self.client.post(url, json=data, headers=self.headers)

    def test_course_list(self):
        courses = {c['id']: c for c in self.client.get('/api/courses').json()}
        self.assertEqual([m['no'] for m in courses['ai-agent']['modules']], [0, 1, 2, 3, 4, 5])
        self.assertEqual(len(courses['atdl']['modules']), 11)

    def test_default_course_unchanged(self):
        room = self.post('/api/t/classes', {'name': 'Lớp cũ'}).json()
        self.assertEqual(room['course'], 'atdl')

    def test_unknown_course_rejected(self):
        self.assertEqual(self.post('/api/t/classes', {'name': 'Sai khóa', 'course': 'khong-co'}).status_code, 400)

    def test_ai_agent_class(self):
        room = self.post('/api/t/classes', {'name': 'AI Agent – Khóa 01', 'course': 'ai-agent'}).json()
        cid = room['id']
        self.assertEqual(room['course'], 'ai-agent')
        st = self.post('/api/join', {'code': room['code'], 'name': 'Lan'}).json()
        auth = {'Authorization': 'Bearer ' + st['token']}

        state = self.client.get('/api/s/state', headers=auth).json()
        self.assertEqual(state['cls']['course'], 'ai-agent')
        self.assertTrue(state['cls']['course_title'].startswith('AI Agent'))
        self.assertEqual([m['no'] for m in state['modules']], [0, 1])
        self.assertIn('Kiến trúc', state['modules'][1]['short'])

        # buổi 6–10 và bài tập của khóa khác không tồn tại trong lớp này
        self.assertEqual(self.client.patch(f'/api/t/classes/{cid}', json={'active_module': 6}, headers=self.headers).status_code, 400)
        self.assertEqual(self.post(f'/api/t/classes/{cid}/activities/m01-th1', {'status': 'open'}).status_code, 404)
        self.assertEqual(self.post(f'/api/t/classes/{cid}/view', {'module': 7}).status_code, 400)

        # mở và nộp bài thực hành 1; gợi ý chữa bài chỉ hiện khi công bố
        self.post(f'/api/t/classes/{cid}/view', {'module': 1, 'unlocked': 99}).raise_for_status()
        self.post(f'/api/t/classes/{cid}/activities/ai01-th1', {'status': 'open'}).raise_for_status()
        act = self.client.get('/api/s/activity/ai01-th1', headers=auth).json()
        self.assertEqual(act['fields'][1]['type'], 'table')
        self.post('/api/s/activity/ai01-th1', {'payload': {'fields': {'vi_tri': 'Trợ lý Content Marketing'}}})
        r = self.client.post('/api/s/activity/ai01-th1', json={'payload': {'fields': {'vi_tri': 'Trợ lý Content Marketing'}}},
                             headers=auth)
        self.assertEqual(r.status_code, 200)

        def has_hint():
            sections = self.client.get('/api/s/module/1', headers=auth).json()['sections']
            return any(b.get('reveal') for s in sections for b in s['blocks'])
        self.assertFalse(has_hint())
        self.post(f'/api/t/classes/{cid}/activities/ai01-th1', {'status': 'revealed'}).raise_for_status()
        self.assertTrue(has_hint())

        # trắc nghiệm tự chấm
        self.post(f'/api/t/classes/{cid}/activities/ai01-check', {'status': 'open'}).raise_for_status()
        r = self.client.post('/api/s/activity/ai01-check', headers=auth,
                             json={'payload': {'answers': {'q1': 'B', 'q2': 'A', 'q3': 'C', 'q4': 'A'}}}).json()
        self.assertEqual(r['response']['version'], 1)
        res = self.client.get(f'/api/t/classes/{cid}/activities/ai01-check/results').json()
        self.assertEqual((res['responses'][0]['score'], res['responses'][0]['max_score']), (3, 4))

        teacher_mod = self.client.get('/api/t/module/5?course=ai-agent').json()
        self.assertTrue(any(a['id'] == 'ai05-exam' for a in teacher_mod['activities']))
        self.assertEqual(self.client.get('/api/t/module/9?course=ai-agent').status_code, 404)


if __name__ == '__main__':
    unittest.main()
