"""Chạy thực tế lời giải và kiểm tra bộ dữ liệu bài ngắn."""
import ast
import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from beginner_labs import SQL, PYTHON, BI, CUSTOMERS, FACT, DIM_DONVI, DIM_NGAY, connect_sample, build_pack


class BeginnerLabs(unittest.TestCase):
    def test_sql_solutions(self):
        connection = connect_sample()
        try:
            for ex in SQL[:7]:
                with self.subTest(ex['title']):
                    self.assertEqual([list(r) for r in connection.execute(ex['solution']).fetchall()], ex['expected'])
            scope = {'connection': connection}
            with contextlib.redirect_stdout(io.StringIO()):
                exec(SQL[7]['solution'], scope)
            self.assertEqual([list(r) for r in scope['result']], SQL[7]['expected'])
            # Cùng một truy vấn, giá trị không tồn tại được xử lý như dữ liệu.
            self.assertEqual(connection.execute(scope['query'], ('KH002-khong-ton-tai',)).fetchall(), [])
            self.assertEqual(connection.execute(scope['query'], ("KH002' OR '1'='1",)).fetchall(), [])
        finally:
            connection.close()

    def test_python_solutions(self):
        before = os.getcwd()
        with tempfile.TemporaryDirectory() as temp:
            try:
                os.chdir(temp)
                for ex in PYTHON:
                    with self.subTest(ex['title']):
                        output = io.StringIO()
                        scope = {'rows': json.loads(json.dumps(CUSTOMERS)), 'json': json}
                        with contextlib.redirect_stdout(output):
                            exec(ex['solution'], scope)
                        actual = []
                        for line in output.getvalue().splitlines():
                            try:
                                actual.append(ast.literal_eval(line))
                            except (ValueError, SyntaxError):
                                actual.append(line)
                        self.assertEqual(actual, ex['expected'])
                sent = json.loads(Path('ban_giao.json').read_text(encoding='utf-8'))
                self.assertTrue(all(set(r) == {'region', 'kwh'} for r in sent))
            finally:
                os.chdir(before)

    def test_bi_data_and_metrics(self):
        # Đối chiếu số liệu độc lập với mã DAX; chưa thay thế việc chạy Power BI.
        self.assertEqual(len(FACT), 8)
        self.assertEqual(len({r['MaKH'] for r in FACT}), 6)
        self.assertEqual(sum(r['kWh'] for r in FACT), 1770)
        self.assertEqual({u: sum(r['kWh'] for r in FACT if r['MaDonVi'] == u)
                          for u in ('DV_A', 'DV_B', 'DV_C')}, {'DV_A':560, 'DV_B':810, 'DV_C':400})
        self.assertEqual(sum(r['kWh'] for r in FACT if r['MaDonVi'] in ('DV_A','DV_B')), 1370)
        self.assertEqual(sum(r['kWh'] for r in FACT if r['Ngay'] == '2026-09-02'), 370)
        units = {r['MaDonVi'] for r in DIM_DONVI}
        dates = {r['Ngay'] for r in DIM_NGAY}
        self.assertEqual(len(units), len(DIM_DONVI))
        self.assertEqual(len(dates), len(DIM_NGAY))
        self.assertTrue(all(r['MaDonVi'] in units and r['Ngay'] in dates for r in FACT))

    def test_sections_and_solution_gates(self):
        from app.content import ACTIVITIES, MODULES, student_module
        for no, prefix, count in [(6, 'sql',8), (6,'py',8), (7,'bi',10)]:
            for i in range(1,count+1):
                aid = f'm{no:02d}-{prefix}{i:02d}-v1'
                a = ACTIVITIES[aid]
                self.assertEqual(a['scope'], 'student')
                self.assertEqual(len(a['fields']), 4)
                self.assertTrue(a['instructions'])
                self.assertFalse(any(b.get('reveal') for b in a['instructions']))
                for ex in SQL + PYTHON + BI:
                    if ex['title'] == a['title']:
                        self.assertNotIn(ex['answer'], json.dumps(a, ensure_ascii=False))
                hidden = next(s for s in student_module(no,None,set())['sections'] if s.get('activity') == aid)
                self.assertFalse(any(b.get('reveal') for b in hidden['blocks']))
                shown = next(s for s in student_module(no,None,{aid})['sections'] if s.get('activity') == aid)
                self.assertTrue(any(b.get('reveal') == aid for b in shown['blocks']))
        for no in (6,7):
            ids = [s['id'] for s in MODULES[no]['sections']]
            self.assertEqual(len(ids), len(set(ids)))

    def test_student_pack_runs_without_solutions(self):
        files = build_pack()
        self.assertNotIn('solution', '\n'.join(files).lower())
        with tempfile.TemporaryDirectory() as temp:
            for name, text in files.items():
                Path(temp, name).write_text(text, encoding='utf-8')
            for name in ('sql_lab.py', 'python_lab.py'):
                with contextlib.redirect_stdout(io.StringIO()):
                    exec(compile(files[name], name, 'exec'), {'__file__': str(Path(temp,name))})
        path = Path(__file__).resolve().parents[1] / 'app/static/labs/bai_tap_SQL_Python_BI.zip'
        with zipfile.ZipFile(path) as z:
            self.assertEqual(set(z.namelist()), set(files))
            self.assertIsNone(z.testzip())
            self.assertEqual(json.loads(z.read('customers.json')), CUSTOMERS)


if __name__ == '__main__':
    unittest.main()
