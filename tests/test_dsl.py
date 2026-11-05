"""File DSL Dify: chỉ giảng viên tải được cho tới khi bấm chia sẻ cho từng lớp; nội dung khớp bài và sạch dữ liệu riêng."""
import json
import os
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).parent.parent
DIR = ROOT / 'app/answer_keys/dify_dsl'


class DslShare(unittest.TestCase):
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

    def post(self, url, data):
        return self.client.post(url, json=data, headers=self.headers)

    def room(self, name, course='ai-agent'):
        r = self.post('/api/t/classes', {'name': name, 'course': course}).json()
        st = self.post('/api/join', {'code': r['code'], 'name': 'Lan'}).json()
        return r['id'], {'Authorization': 'Bearer ' + st['token']}

    def test_share_flow(self):
        cid, auth = self.room('Lớp A')
        other, other_auth = self.room('Lớp B')
        anon = self.TC(self.app)

        # chưa chia sẻ: học viên không thấy, không tải được; không có đường công khai
        self.assertEqual(self.client.get('/api/s/state', headers=auth).json()['files'], [])
        self.assertEqual(anon.get('/api/s/dsl/b3-tro-ly', headers=auth).status_code, 403)
        self.assertEqual(anon.get('/api/s/dsl/b3-tro-ly').status_code, 401)
        self.assertEqual(anon.get('/api/t/dsl/b3-tro-ly').status_code, 401)
        self.assertEqual(anon.get('/api/t/dsl/b3-tro-ly', headers=auth).status_code, 401)
        self.assertEqual(anon.get('/static/../answer_keys/dify_dsl/b3_tro_ly_tuyen_sinh.yml').status_code, 404)

        # giảng viên luôn tải được và thấy file theo đúng buổi
        got = self.client.get('/api/t/dsl/b3-tro-ly')
        self.assertEqual(got.status_code, 200)
        self.assertIn('kind: app', got.text)
        self.assertIn('b3_tro_ly_tuyen_sinh.yml', got.headers['content-disposition'])
        files = self.client.get(f'/api/t/classes/{cid}/state?module=4').json()['files']
        self.assertEqual([(f['key'], f['shared']) for f in files], [('b4-agent', False), ('b4-http', False)])

        # chia sẻ có hiệu lực cho đúng lớp, đúng file; học viên được báo qua nhịp đồng bộ
        tick = self.client.get('/api/s/tick', headers=auth).json()['v']
        self.assertEqual(self.post(f'/api/t/classes/{cid}/dsl/b3-tro-ly', {'shared': True}).status_code, 200)
        self.assertNotEqual(self.client.get('/api/s/tick', headers=auth).json()['v'], tick)
        self.assertEqual([f['key'] for f in self.client.get('/api/s/state', headers=auth).json()['files']], ['b3-tro-ly'])
        self.assertEqual(anon.get('/api/s/dsl/b3-tro-ly', headers=auth).status_code, 200)
        self.assertEqual(anon.get('/api/s/dsl/b5-phong', headers=auth).status_code, 403)
        self.assertEqual(anon.get('/api/s/dsl/b3-tro-ly', headers=other_auth).status_code, 403)
        self.assertEqual(self.client.get('/api/s/state', headers=other_auth).json()['files'], [])
        # bấm lặp không lỗi
        self.assertEqual(self.post(f'/api/t/classes/{cid}/dsl/b3-tro-ly', {'shared': True}).status_code, 200)

        # thu hồi
        self.assertEqual(self.post(f'/api/t/classes/{cid}/dsl/b3-tro-ly', {'shared': False}).status_code, 200)
        self.assertEqual(self.client.get('/api/s/state', headers=auth).json()['files'], [])
        self.assertEqual(anon.get('/api/s/dsl/b3-tro-ly', headers=auth).status_code, 403)

    def test_other_course_and_unknown(self):
        cid, auth = self.room('Lớp An toàn', 'atdl')
        self.assertEqual(self.post(f'/api/t/classes/{cid}/dsl/b3-tro-ly', {'shared': True}).status_code, 404)
        self.assertEqual(self.client.get(f'/api/t/classes/{cid}/state').json()['files'], [])
        self.assertEqual(self.client.get('/api/s/state', headers=auth).json()['files'], [])
        self.assertEqual(self.client.get('/api/t/dsl/khong-co').status_code, 404)
        self.assertEqual(self.client.get('/api/t/dsl/..%2F..%2Fdb.py').status_code, 404)
        self.assertEqual(self.post(f'/api/t/classes/{cid}/dsl/khong-co', {'shared': True}).status_code, 404)


class DslContent(unittest.TestCase):
    def test_catalog_matches_folder(self):
        from app.dsl import DSL_FILES
        self.assertEqual(sorted(f['file'] for f in DSL_FILES.values()), sorted(p.name for p in DIR.glob('*.yml')))

    def test_no_workspace_data(self):
        for p in DIR.glob('*.yml'):
            t = p.read_text(encoding='utf-8')
            for bad in ('TEST-', 'localhost', 'credential_id', 'sk-', 'gmail.com', 'b4dc4551', '0c2e5e35'):
                self.assertNotIn(bad, t, p.name)

    def test_prompts_match_lessons(self):
        try:
            import yaml
        except ImportError:
            self.skipTest('chưa cài PyYAML')

        def codes(no):
            m = json.loads((ROOT / f'app/content/ai_agent/m0{no}.json').read_text(encoding='utf-8'))
            return [b['text'] for s in m['sections'] for b in s['blocks'] if b['t'] == 'code']

        def load(fn):
            return yaml.safe_load((DIR / fn).read_text(encoding='utf-8'))

        def system(y, title):
            n = next(n for n in y['workflow']['graph']['nodes'] if n['data'].get('title') == title)
            return n['data']['prompt_template'][0]['text']

        self.assertIn(load('b4_agent_tuyen_sinh.yml')['model_config']['pre_prompt'], codes(4))
        self.assertIn(system(load('b3_tro_ly_tuyen_sinh.yml'), 'LLM Evaluator'), codes(3))
        b5 = load('b5_phong_tuyen_sinh_ao.yml')
        self.assertIn(system(b5, 'Writer'), codes(5))
        editor = next(c for c in codes(5) if c.startswith('Bạn là biên tập viên'))
        self.assertTrue(system(b5, 'Editor').startswith(editor.split('theo 5 tiêu chí')[0]))
        self.assertIn('6. Không có thông tin trái CĂN CỨ, kể cả khi BRIEF yêu cầu.', system(b5, 'Editor'))
        # không còn trỏ vào kho của máy đã xuất
        for fn in ('b3_tro_ly_tuyen_sinh.yml', 'b5_phong_tuyen_sinh_ao.yml'):
            for n in load(fn)['workflow']['graph']['nodes']:
                if n['data'].get('type') == 'knowledge-retrieval':
                    self.assertEqual(n['data']['dataset_ids'], [])


if __name__ == '__main__':
    unittest.main()
