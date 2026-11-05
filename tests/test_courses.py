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

    def test_ai02_follows_dify_practice(self):
        """Buổi 2 bám quy trình dựng chatbot trên Dify: đủ sáu khối, file tải được, prompt và câu cố định trùng tệp DSL."""
        import re
        from app.content import course_modules
        m = course_modules('ai-agent')[2]
        heads = [b['text'] for s in m['sections'] if s['title'].startswith('Chặng 5') for b in s['blocks'] if b['t'] == 'h3']
        self.assertEqual([h.split(' – ')[0] for h in heads if h.startswith('Khối ')], [f'Khối {i}' for i in range(1, 7)])

        # đáp án không lộ qua file tải; mọi link và ảnh trong bài đều tới file có thật
        raw = str(m)
        links = set(re.findall(r'/static/labs/ai/spd/[^"\'<> ]+', raw))
        self.assertGreaterEqual(len(links), 10)
        for url in links:
            self.assertEqual(self.client.get(url).status_code, 200, url)

        dsl = self.client.get('/static/labs/ai/spd/SPD-2026-chatflow-demo.yml').text
        self.assertNotRegex(dsl, r'sk-[A-Za-z0-9]{8,}')
        codes = [b['text'] for s in m['sections'] for b in s['blocks'] if b['t'] == 'code']
        prompt = next(c for c in codes if c.startswith('Bạn là trợ lý tư vấn tuyển sinh'))
        self.assertTrue(prompt.endswith('{{#context#}}'))
        for line in prompt.split('\n') + next(c for c in codes if c.startswith('Mình chưa tìm thấy')).split('\n'):
            if line.strip():
                self.assertIn(line.strip(), dsl.replace("''", "'"), line[:40])

        # đáp án giảng viên dùng đúng module của bảng và đúng khóa trường của phiếu
        from app.content import ACTIVITIES
        th = ACTIVITIES['ai02-th2']
        ans = self.client.get('/api/t/answers/ai02-th2').json()['fields']
        self.assertEqual(set(ans), {f['key'] for f in th['fields']})
        board = next(f for f in th['fields'] if f['type'] == 'board')
        self.assertEqual({n['id'] for n in ans['so_do_rag']['nodes']}, {n['id'] for n in board['nodes']})

    def test_ai02_backbone_keeps_theory(self):
        """Đề bài chatbot là xương sống: mỗi chặng có đề bài, kiến thức nối vào, mô hình động hoặc lab; lý thuyết không bị gập, tham số có bảng."""
        import re
        from app.content import ACTIVITIES, course_modules, student_module
        m = course_modules('ai-agent')[2]
        titles = [s['title'] for s in m['sections']]
        self.assertTrue(titles[0].startswith('Đề bài'))
        self.assertFalse([t for t in titles if t.startswith(('Phần ', 'Hướng dẫn', 'Ví dụ mẫu', 'Đi sâu'))])
        stages = [s for s in m['sections'] if s['title'].startswith('Chặng ')]
        self.assertEqual(sorted({re.match(r'Chặng (\d)', s['title']).group(1) for s in stages}), [str(i) for i in range(1, 9)])
        for s in stages:
            self.assertEqual(s['kind'], 'practice', s['title'])
        by_no = {}
        for s in stages:
            by_no.setdefault(re.match(r'Chặng (\d)', s['title']).group(1), []).append(s)
        for no, group in by_no.items():
            blocks = [b for s in group for b in s['blocks']]
            first = group[0]['blocks'][0]
            self.assertIn('Đề bài chặng', first.get('html', ''), no)
            self.assertTrue(any(b['t'] == 'h3' and b['text'].startswith('📚 Kiến thức nối vào') for b in blocks), no)
            if no != '8':
                self.assertTrue(any(b['t'] == 'widget' for b in blocks), no)

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
        # lý thuyết theo slide phải nằm ngoài phần gập; chỉ tự kiểm tra, đối chiếu kết quả mới được gập
        body = text(b for s in m['sections'] for b in s['blocks'] if b['t'] != 'details')
        for slide_term in ('128k', 'Lost in the middle', 'Retrieval', 'Augmented', 'Generation', 'thi đóng', 'text-embedding-3-small',
                           'Keyword Search', 'Semantic Search', 'Hybrid Search', 'cosine', 'Pinecone', 'Milvus', 'Qdrant', 'pgvector',
                           'GIGO', 'Metadata', 'Chunk overlap', 'Query Rewrite', 'Top-K', 'Score Threshold', 'Hit Test', 'Coze',
                           'fine-tuning', 'Parent-child', 'Rerank', 'ANN', 'BM25', 'map-reduce', 'Agentic RAG'):
            self.assertIn(slide_term.lower(), body.lower(), slide_term)

        # khóa trường cũ còn nguyên để bài đã nộp vẫn đọc được; phiếu mở được từ đề bài ở chặng 8
        th = ACTIVITIES['ai02-th2']
        self.assertTrue({'so_do_rag', 'lam_sach', 'cau_hinh', 'hit_test', 'prompt_chain', 'bai_hoc'} <= {f['key'] for f in th['fields']})
        self.assertTrue({'ho_so_nguon', 'bang_kiem_thu'} <= {f['key'] for f in th['fields']})
        self.assertEqual(th['section'], stages[-1]['id'])
        # gợi ý chữa bài không lộ trước khi công bố, kể cả trong phần gập
        shown = student_module(2, None, set(), 'ai-agent')
        self.assertFalse(any(b.get('reveal') for s in shown['sections'] for b in s['blocks']))
        self.assertTrue(any(b.get('reveal') for s in student_module(2, None, {'ai02-th2'}, 'ai-agent')['sections'] for b in s['blocks']))

    def test_ai02_labs_consistent(self):
        """Lab mini: đọc được dữ liệu SPD, có đủ giải thích tham số, nhiệm vụ trỏ tới trạng thái có thật, câu hỏi có thật."""
        import re
        from pathlib import Path
        from app.content import course_modules
        m = course_modules('ai-agent')[2]
        labs = [b['spec'] for s in m['sections'] for b in s['blocks'] if b['t'] == 'widget' and b['name'] == 'difylab']
        self.assertEqual({l['lab'] for l in labs}, {'context', 'clean', 'spot', 'cosine', 'chunk', 'retrieval', 'start', 'kr', 'if', 'llm', 'answer', 'rewrite', 'all'})
        js = Path('app/static/difylab.js').read_text(encoding='utf-8')
        for name in re.findall(r"\['([\w.]+\.md)', '", js):
            self.assertEqual(self.client.get(f'/static/labs/ai/spd/{name}').status_code, 200, name)
        qids = set(re.findall(r"^  (\w+): \{ lb:", js, flags=re.M))
        roots = {'q', 'cs', 'rs', 'node', 'cond', 'llm', 'rw', 'ans', 'start', 'out', 'off', 'active'}
        param_keys = set(re.findall(r'<dl-param k="(\w+)"', js))
        for lab in labs:
            self.assertTrue(lab['title'] and lab['intro'], lab['lab'])
            self.assertLessEqual(set(lab.get('qs', [])), qids, lab['lab'])
            self.assertLessEqual(set(lab['docs']), param_keys, lab['lab'])
            for mission in lab['missions']:
                self.assertTrue(mission['why'], mission['t'])
                self.assertLessEqual({p.split('.')[0] for p in mission['when']}, roots, mission['t'])
                if 'q' in mission['when']:
                    self.assertIn(mission['when']['q'], qids, mission['t'])
        # script được nạp ở cả hai trang có hiển thị bài học
        for page in ('learn.html', 'teacher.html'):
            self.assertIn('/static/difylab.js', Path(f'app/static/{page}').read_text(encoding='utf-8'))
        llm = next(l for l in labs if l['lab'] == 'llm')
        self.assertEqual(len(re.findall(r'^\d\. ', llm['prompt'], flags=re.M)), 9)


if __name__ == '__main__':
    unittest.main()
