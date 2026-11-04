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
        self.assertEqual(act['fields'][2]['type'], 'board')
        self.post('/api/s/activity/ai01-th1', {'payload': {'fields': {'problem': 'Giao dịch viên mất 5 phút mỗi cuộc gọi'}}})
        r = self.client.post('/api/s/activity/ai01-th1', json={'payload': {'fields': {'problem': 'Giao dịch viên mất 5 phút mỗi cuộc gọi'}}},
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
        exam = next(a for a in teacher_mod['activities'] if a['id'] == 'ai05-exam')
        self.assertEqual(len(exam['questions']), 20)
        for no in range(1, 6):
            self.assertEqual(sum(1 for q in exam['questions'] if q.get('module') == no), 4)
        self.assertEqual(self.client.get('/api/t/module/9?course=ai-agent').status_code, 404)

    def test_ai_agent_boards_answers_and_lab(self):
        from app.content import ACTIVITIES
        for no in range(1, 6):
            aid = f'ai0{no}-th{no}'
            self.assertTrue(any(f['type'] == 'board' for f in ACTIVITIES[aid]['fields']), aid)
            ans = self.client.get(f'/api/t/answers/{aid}')
            self.assertEqual(ans.status_code, 200, aid)
            self.assertIn('fields', ans.json())
        lab = self.client.get('/static/labs/ai/index.html')
        self.assertEqual(lab.status_code, 200)
        self.assertIn('Phòng thí nghiệm AI Agent', lab.text)

    def test_ai02_is_hands_on(self):
        """Buổi 2 thuần thực hành: mỗi chặng làm trước, kiến thức xen sau, nội dung slide không mất."""
        from app.content import ACTIVITIES, course_modules, student_module
        m = course_modules('ai-agent')[2]
        titles = [s['title'] for s in m['sections']]
        self.assertFalse([t for t in titles if t.startswith(('Phần ', 'Hướng dẫn', 'Ví dụ mẫu', 'Đi sâu'))])
        stages = [s for s in m['sections'] if s['title'].startswith('Chặng ')]
        self.assertEqual([s['title'].split(' – ')[0] for s in stages], [f'Chặng {i}' for i in range(1, 9)])
        for s in stages:
            self.assertEqual(s['kind'], 'practice', s['title'])
            heads = [b['text'] for b in s['blocks'] if b['t'] == 'h3']
            xen = [i for i, h in enumerate(heads) if h.startswith('Xen kẽ')]
            if s['title'].startswith('Chặng 8'):
                self.assertEqual(xen, [])
                continue
            # có đúng một lần xen kẽ, và khối đầu tiên của chặng là việc phải làm
            self.assertEqual(len(xen), 1, s['title'])
            self.assertTrue(s['blocks'][0]['text'].startswith('Làm ngay'), s['title'])

        def text(blocks):
            out = []
            for b in blocks:
                out.append(b.get('plain', '') + b.get('text', ''))
                for it in b.get('items', []):
                    out.append(it.get('plain', ''))
                for r in b.get('rows', []):
                    out.extend(c.get('plain', '') for c in r)
                out.append(text(b.get('blocks', [])))
            return '\n'.join(out)
        body = text(b for s in m['sections'] for b in s['blocks'])
        for slide_term in ('128k', 'Lost in the middle', 'Retrieval', 'Augmented', 'Generation', 'thi đóng', 'text-embedding-3-small',
                           'Keyword Search', 'Semantic Search', 'Hybrid Search', 'cosine', 'Pinecone', 'Milvus', 'Qdrant', 'pgvector',
                           'GIGO', 'OCR', 'Metadata', 'Chunk overlap', 'Query Rewrite', 'Top-K', 'Score Threshold', 'Hit Test', 'Coze'):
            self.assertIn(slide_term.lower(), body.lower(), slide_term)

        # khóa trường cũ còn nguyên để bài đã nộp vẫn đọc được; phiếu mở được từ đề bài ở chặng 8
        th = ACTIVITIES['ai02-th2']
        self.assertTrue({'so_do_rag', 'lam_sach', 'cau_hinh', 'hit_test', 'prompt_chain', 'bai_hoc'} <= {f['key'] for f in th['fields']})
        self.assertEqual(th['section'], stages[-1]['id'])
        # gợi ý chữa bài không lộ trước khi công bố, kể cả trong phần gập
        shown = student_module(2, None, set(), 'ai-agent')
        self.assertFalse(any(b.get('reveal') for s in shown['sections'] for b in s['blocks']))
        self.assertTrue(any(b.get('reveal') for s in student_module(2, None, {'ai02-th2'}, 'ai-agent')['sections'] for b in s['blocks']))


if __name__ == '__main__':
    unittest.main()
