import csv
import hashlib
import hmac
import io
import json
import os
import re
import secrets
import time
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Literal, Optional

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from starlette.middleware.sessions import SessionMiddleware

from . import db
from .answer_keys import ANSWER_KEYS
from .content import ACTIVITIES, INDEX, MODULES, public_activity, score, section_index, student_module

BASE = Path(__file__).parent
TEACHER_PASSWORD = os.environ.get("TEACHER_PASSWORD", "")
SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_urlsafe(32)
PROD = bool(os.environ.get("RENDER") or os.environ.get("PRODUCTION"))
ONLINE_SECONDS = 20
MAX_PAYLOAD = 100_000
OPEN_ALL = 9999  # giá trị unlocked khi giảng viên mở toàn bộ buổi
VN_TZ = timezone(timedelta(hours=7))

app = FastAPI(title="Lớp học An toàn dữ liệu", docs_url=None, redoc_url=None, openapi_url=None)
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY, session_cookie="gv_session",
                   max_age=12 * 3600, same_site="strict", https_only=PROD)
app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")


@app.on_event("startup")
def _startup():
    db.init_db()
    # Buổi 7 có thêm phần Phòng thí nghiệm RLS ở cuối: lớp đã mở đến phần cuối cũ (28) thì mở luôn phần mới
    db.x("UPDATE class_modules SET unlocked=:a WHERE module_no=7 AND unlocked=28", a=OPEN_ALL)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    # API giảng viên dùng cookie: bắt buộc header tùy biến để chặn CSRF từ trang khác
    if request.url.path.startswith("/api/t/") and request.method not in ("GET", "HEAD") \
            and request.headers.get("x-requested-with") != "fetch":
        return JSONResponse({"detail": "Yêu cầu chưa hợp lệ. Vui lòng tải lại trang rồi thử lại."}, status_code=403)
    resp = await call_next(request)
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["X-Frame-Options"] = "DENY"
    resp.headers["Referrer-Policy"] = "same-origin"
    # 'unsafe-eval' cần cho Vue biên dịch template ngay trong trang
    resp.headers["Content-Security-Policy"] = (
        "default-src 'self'; script-src 'self' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'")
    if request.url.path.startswith("/api/"):
        resp.headers["Cache-Control"] = "no-store"
    else:
        # trang và file tĩnh: luôn hỏi lại server (304 nếu chưa đổi) để bản deploy mới có hiệu lực ngay
        resp.headers.setdefault("Cache-Control", "no-cache")
    return resp


def now():
    return time.time()


def sha(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


# ---------------------------------------------------------------- trang

def asset_url(m):
    # gắn mã nội dung vào đường dẫn JS/CSS: bản deploy mới đổi URL, trình duyệt không dùng lại bản cũ trong bộ nhớ đệm
    f = BASE / "static" / m.group(2)
    v = hashlib.md5(f.read_bytes()).hexdigest()[:10] if f.is_file() else "0"
    return f'{m.group(1)}"/static/{m.group(2)}?v={v}"'


def page(name):
    html = (BASE / "static" / name).read_text(encoding="utf-8")
    return HTMLResponse(re.sub(r'((?:src|href)=)"/static/([\w./-]+\.(?:js|css))"', asset_url, html))


@app.get("/")
def page_home():
    return page("index.html")


@app.get("/learn")
def page_learn():
    return page("learn.html")


@app.get("/teacher")
def page_teacher():
    return page("teacher.html")


@app.get("/healthz")
def health():
    db.q("SELECT 1 AS ok")
    # RENDER_GIT_COMMIT do Render đặt: biết bản deploy nào đang chạy
    return {"ok": True, "rev": os.environ.get("RENDER_GIT_COMMIT", "")[:7]}


@app.get("/api/modules")
def modules_index():
    return INDEX


# ---------------------------------------------------------------- chung

def view_row(class_id, module_no, create=False):
    row = db.q1("SELECT * FROM class_modules WHERE class_id=:c AND module_no=:m", c=class_id, m=module_no)
    if row is None and create:
        db.x("""INSERT INTO class_modules (class_id, module_no, current_section, unlocked, follow, stage, updated_at)
                VALUES (:c, :m, 's0', 0, 1, 1, :t) ON CONFLICT DO NOTHING""", c=class_id, m=module_no, t=now())
        row = db.q1("SELECT * FROM class_modules WHERE class_id=:c AND module_no=:m", c=class_id, m=module_no)
    return row


def activity_states(class_id):
    return {r["activity_id"]: r["status"] for r in
            db.q("SELECT activity_id, status FROM activity_states WHERE class_id=:c", c=class_id)}


def owner_key(a, student):
    return f"s:{student['id']}"


def get_activity(aid):
    a = ACTIVITIES.get(aid)
    if not a:
        raise HTTPException(404, "Không tìm thấy bài tập này")
    return a


# ---------------------------------------------------------------- học viên

class JoinIn(BaseModel):
    code: Optional[str] = Field(default=None, max_length=12)
    phone: Optional[str] = Field(default=None, max_length=20)
    name: Optional[str] = Field(default=None, max_length=60)
    rejoin: Optional[str] = Field(default=None, max_length=12)


_join_fail = defaultdict(list)


def _throttle(key, bucket, limit=10, window=300):
    t = now()
    bucket[key] = [x for x in bucket[key] if t - x < window]
    if len(bucket[key]) >= limit:
        raise HTTPException(429, "Bạn đã thử nhiều lần liên tiếp. Vui lòng chờ vài phút rồi thử lại.")


def norm_phone(raw):
    d = "".join(ch for ch in raw or "" if ch.isdigit())
    if d.startswith("84") and len(d) == 11:
        d = "0" + d[2:]
    if len(d) == 9 and not d.startswith("0"):
        d = "0" + d  # Excel thường làm mất số 0 đầu
    return d if len(d) == 10 and d.startswith("0") else None


def phone_hash(phone):
    # chỉ lưu giá trị băm để tra cứu, không lưu số điện thoại dạng rõ
    return sha("phone:" + phone)


@app.post("/api/join")
def join(body: JoinIn, request: Request):
    ip = request.client.host if request.client else "?"
    _throttle(ip, _join_fail)
    if body.phone is not None:
        return join_by_phone(body, ip)
    if not body.code or len(body.code.strip()) < 4:
        raise HTTPException(400, "Vui lòng nhập mã lớp.")
    cls = db.q1("SELECT * FROM classes WHERE code=:c AND archived=0", c=body.code.strip().upper())
    if not cls:
        _join_fail[ip].append(now())
        raise HTTPException(404, "Mã lớp không hợp lệ hoặc lớp đã đóng. Vui lòng kiểm tra với giảng viên.")
    token = secrets.token_urlsafe(32)
    if body.rejoin:
        st = db.q1("SELECT * FROM students WHERE class_id=:c AND rejoin_hash=:h",
                   c=cls["id"], h=sha(f"{cls['id']}:{body.rejoin.strip().upper()}"))
        if not st:
            _join_fail[ip].append(now())
            raise HTTPException(404, "Mã vào lại cá nhân không hợp lệ. Vui lòng kiểm tra cả mã lớp và mã cá nhân.")
        # đăng nhập trên thiết bị mới: thay token, thiết bị cũ tự đăng xuất
        db.x("UPDATE students SET token_hash=:h, last_seen=:t WHERE id=:id", h=sha(token), t=now(), id=st["id"])
        return {"token": token, "name": st["name"], "rejoin": body.rejoin.strip().upper(), "cls": cls["code"]}
    name = (body.name or "").strip()
    if len(name) < 2:
        raise HTTPException(400, "Vui lòng nhập họ và tên để vào lớp.")
    rejoin = "".join(secrets.choice("ABCDEFGHJKLMNPQRSTUVWXYZ23456789") for _ in range(6))
    db.x("""INSERT INTO students (class_id, name, group_name, token_hash, rejoin_hash, created_at, last_seen)
            VALUES (:c, :n, :g, :h, :r, :t, :t)""",
         c=cls["id"], n=name, g="", h=sha(token), r=sha(f"{cls['id']}:{rejoin}"), t=now())
    return {"token": token, "name": name, "rejoin": rejoin, "cls": cls["code"]}


def join_by_phone(body, ip):
    phone = norm_phone(body.phone)
    if not phone:
        raise HTTPException(400, "Số điện thoại chưa đúng. Vui lòng nhập đủ 10 số, ví dụ 0912345678.")
    sql = """SELECT s.*, c.code AS class_code FROM students s JOIN classes c ON c.id = s.class_id
             WHERE s.phone_hash=:p AND c.archived=0"""
    params = {"p": phone_hash(phone)}
    if body.code and body.code.strip():
        sql += " AND c.code=:c"
        params["c"] = body.code.strip().upper()
    st = db.q1(sql + " ORDER BY c.created_at DESC", **params)
    if not st:
        _join_fail[ip].append(now())
        raise HTTPException(404, "Số điện thoại này chưa có trong danh sách lớp. Vui lòng kiểm tra với giảng viên.")
    token = secrets.token_urlsafe(32)
    # đăng nhập trên thiết bị mới: thay token, thiết bị cũ tự đăng xuất
    db.x("UPDATE students SET token_hash=:h, last_seen=:t WHERE id=:id", h=sha(token), t=now(), id=st["id"])
    return {"token": token, "name": st["name"], "rejoin": None, "cls": st["class_code"]}


def current_student(request: Request):
    auth = request.headers.get("authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(401, "Bạn chưa vào lớp. Vui lòng nhập mã lớp và thông tin cá nhân.")
    st = db.q1("""SELECT s.*, c.name AS class_name, c.code AS class_code, c.active_module, c.archived
                  FROM students s JOIN classes c ON c.id = s.class_id WHERE s.token_hash=:h""",
               h=sha(auth[7:].strip()))
    if not st or st["archived"]:
        raise HTTPException(401, "Phiên truy cập không còn hiệu lực hoặc lớp đã đóng. Vui lòng vào lại lớp.")
    return st


def visible_modules(class_id):
    rows = db.q("SELECT module_no FROM class_modules WHERE class_id=:c", c=class_id)
    return sorted({0} | {r["module_no"] for r in rows if r["module_no"] in MODULES})


# ---- nhịp đồng bộ: học viên hỏi mỗi giây, trả lời từ bộ nhớ, không truy vấn CSDL.
# Đúng với một tiến trình server (startCommand chạy một worker uvicorn).
BOOT = secrets.token_hex(4)
_tick = defaultdict(int)       # class_id -> số lần giảng viên thay đổi trạng thái lớp
_tok_cache = {}                # token_hash -> (class_id, hết hạn)
TOKEN_CACHE_SECONDS = 30


def bump(cid):
    _tick[cid] += 1


@app.get("/api/s/tick")
def student_tick(request: Request):
    auth = request.headers.get("authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(401, "Bạn chưa vào lớp.")
    h = sha(auth[7:].strip())
    hit = _tok_cache.get(h)
    if not hit or hit[1] < now():
        st = db.q1("""SELECT s.class_id FROM students s JOIN classes c ON c.id = s.class_id
                      WHERE s.token_hash=:h AND c.archived=0""", h=h)
        if not st:
            _tok_cache.pop(h, None)
            raise HTTPException(401, "Phiên truy cập không còn hiệu lực. Vui lòng vào lại lớp.")
        if len(_tok_cache) > 5000:
            _tok_cache.clear()
        hit = _tok_cache[h] = (st["class_id"], now() + TOKEN_CACHE_SECONDS)
    return {"v": f"{BOOT}.{_tick[hit[0]]}"}


@app.get("/api/s/state")
@db.batched
def student_state(st=Depends(current_student)):
    db.x("UPDATE students SET last_seen=:t WHERE id=:id", t=now(), id=st["id"])
    cid, active = st["class_id"], st["active_module"]
    view = view_row(cid, active, create=True)
    states = activity_states(cid)
    mods = visible_modules(cid)
    views = {r["module_no"]: r for r in db.q("SELECT * FROM class_modules WHERE class_id=:c", c=cid)}
    revealed = sorted(a for a, s in states.items() if s == "revealed")
    content_keys = {}
    for no in mods:
        v = views.get(no)
        rv = [a for a in revealed if a.startswith(f"m{no:02d}-")]
        content_keys[no] = f"{v['unlocked']}.{v['stage']}.{','.join(rv)}" if v else "all"
    mine = db.q("""SELECT activity_id, updated_at FROM responses
                   WHERE class_id=:c AND owner_key=:s""",
                c=cid, s=f"s:{st['id']}")
    done = {r["activity_id"] for r in mine}
    acts = [{"id": a["id"], "title": a["title"], "type": a["type"], "module": a["module"],
             "status": states.get(a["id"], "hidden"), "submitted": a["id"] in done}
            for a in ACTIVITIES.values() if states.get(a["id"], "hidden") != "hidden" and a["module"] in mods]
    return {
        "me": {"name": st["name"]},
        "cls": {"name": st["class_name"], "code": st["class_code"], "active_module": active},
        "modules": [{"no": n, "short": MODULES[n]["short"], "title": MODULES[n]["title"]} for n in mods],
        "view": {"module": active, "current_section": view["current_section"], "follow": bool(view["follow"])},
        "content_keys": content_keys,
        "activities": acts,
        "server_time": now(),
    }


@app.get("/api/s/module/{no}")
@db.batched
def student_module_content(no: int, st=Depends(current_student)):
    if no not in visible_modules(st["class_id"]):
        raise HTTPException(403, "Buổi học này chưa mở")
    states = activity_states(st["class_id"])
    revealed = {a for a, s in states.items() if s == "revealed"}
    view = None if no == 0 else view_row(st["class_id"], no)
    return student_module(no, view, revealed)


def my_response(cid, a, st):
    return db.q1("""SELECT r.*, g.score AS manual_score, g.max_score AS manual_max,
                          g.feedback, g.graded_at
                   FROM responses r LEFT JOIN response_grades g
                   ON g.response_id=r.id AND g.response_version=r.version
                   WHERE r.class_id=:c AND r.activity_id=:a AND r.owner_key=:o""",
                 c=cid, a=a["id"], o=owner_key(a, st))


def response_out(r, revealed=False):
    if not r:
        return None
    return {"payload": json.loads(r["payload"]),
            "score": (r["score"] if r["score"] is not None else r.get("manual_score")) if revealed else None,
            "max_score": (r["max_score"] if r["max_score"] is not None else r.get("manual_max")) if revealed else None,
            "feedback": r.get("feedback", "") if revealed else "",
            "version": r["version"], "updated_by": r["updated_by"], "updated_at": r["updated_at"]}


@app.get("/api/s/activity/{aid}")
@db.batched
def student_activity(aid: str, st=Depends(current_student)):
    a = get_activity(aid)
    status = activity_states(st["class_id"]).get(aid, "hidden")
    if status == "hidden" or a["module"] not in visible_modules(st["class_id"]):
        raise HTTPException(403, "Giảng viên chưa mở bài tập này.")
    out = public_activity(a, status)
    r = my_response(st["class_id"], a, st)
    out["response"] = response_out(r, revealed=status == "revealed")
    if status == "revealed" and a["type"] in ("mcq", "multi"):
        out["stats"] = mcq_stats(st["class_id"], a)
    return out


class SubmitIn(BaseModel):
    payload: dict


# Khóa cấu trúc của bài dạng bảng (vị trí module, đầu dây nối): không phải nội dung bài làm
BOARD_KEYS = {"id", "kind", "x", "y", "from", "to"}


def has_work(value):
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, dict):
        return any(has_work(v) for k, v in value.items() if k not in BOARD_KEYS)
    if isinstance(value, list):
        return any(has_work(v) for v in value)
    return value is True or isinstance(value, (int, float)) and not isinstance(value, bool)


@app.post("/api/s/activity/{aid}")
@db.batched
def student_submit(aid: str, body: SubmitIn, st=Depends(current_student)):
    a = get_activity(aid)
    status = activity_states(st["class_id"]).get(aid, "hidden")
    if a["module"] not in visible_modules(st["class_id"]):
        raise HTTPException(403, "Buổi học này chưa mở")
    if status != "open":
        raise HTTPException(409, "Bài đã ngừng nhận bài nộp. Vui lòng liên hệ giảng viên nếu cần cập nhật.")
    work = body.payload.get("fields" if a["type"] == "practice" else "answers", {})
    if not isinstance(work, dict) or not has_work(work):
        raise HTTPException(400, "Bạn chưa nhập bài làm. Hãy trả lời trước khi nộp.")
    raw = json.dumps(body.payload, ensure_ascii=False)
    if len(raw) > MAX_PAYLOAD:
        raise HTTPException(413, "Bài nộp vượt giới hạn dung lượng. Vui lòng rút gọn nội dung trước khi nộp lại.")
    pts, mx = score(a, body.payload)
    t = now()
    db.x("""INSERT INTO responses (class_id, activity_id, owner_key, student_id, group_name, payload, score, max_score,
                                   version, updated_by, updated_at)
            VALUES (:c, :a, :o, :s, :g, :p, :sc, :mx, 1, :by, :t)
            ON CONFLICT (class_id, activity_id, owner_key) DO UPDATE SET
              payload=excluded.payload, score=excluded.score, max_score=excluded.max_score,
              version=responses.version + 1, updated_by=excluded.updated_by, updated_at=excluded.updated_at,
              student_id=excluded.student_id""",
         c=st["class_id"], a=aid, o=owner_key(a, st), s=st["id"], g="", p=raw,
         sc=pts, mx=mx, by=st["name"], t=t)
    return {"ok": True, "response": response_out(my_response(st["class_id"], a, st))}


# ---------------------------------------------------------------- giảng viên

_login_fail = defaultdict(list)


class LoginIn(BaseModel):
    password: str = Field(max_length=200)


@app.post("/api/t/login")
def teacher_login(body: LoginIn, request: Request):
    ip = request.client.host if request.client else "?"
    _throttle(ip, _login_fail, limit=8)
    if not TEACHER_PASSWORD:
        raise HTTPException(500, "Chức năng đăng nhập giảng viên chưa sẵn sàng. Vui lòng liên hệ quản trị hệ thống.")
    if not hmac.compare_digest(body.password.encode(), TEACHER_PASSWORD.encode()):
        _login_fail[ip].append(now())
        raise HTTPException(401, "Mật khẩu chưa đúng. Vui lòng kiểm tra rồi đăng nhập lại.")
    request.session.clear()
    request.session["teacher"] = True
    return {"ok": True}


@app.post("/api/t/logout")
def teacher_logout(request: Request):
    request.session.clear()
    return {"ok": True}


def teacher(request: Request):
    if not request.session.get("teacher"):
        raise HTTPException(401, "Vui lòng đăng nhập vào khu vực giảng viên để tiếp tục.")
    return True


@app.get("/api/t/me")
def teacher_me(_=Depends(teacher)):
    return {"ok": True}


def get_class(cid):
    c = db.q1("SELECT * FROM classes WHERE id=:id", id=cid)
    if not c:
        raise HTTPException(404, "Không tìm thấy lớp học này.")
    return c


@app.get("/api/t/classes")
@db.batched
def list_classes(_=Depends(teacher)):
    rows = db.q("""SELECT c.*, (SELECT COUNT(*) FROM students s WHERE s.class_id=c.id) AS n_students
                   FROM classes c ORDER BY c.archived, c.created_at DESC""")
    return rows


class ClassIn(BaseModel):
    name: str = Field(min_length=2, max_length=100)


@app.post("/api/t/classes")
def create_class(body: ClassIn, _=Depends(teacher)):
    for _try in range(10):
        code = "".join(secrets.choice("ABCDEFGHJKLMNPQRSTUVWXYZ23456789") for _ in range(6))
        if not db.q1("SELECT id FROM classes WHERE code=:c", c=code):
            break
    rows = db.x("INSERT INTO classes (name, code, active_module, archived, created_at) VALUES (:n, :c, 1, 0, :t) RETURNING id",
                n=body.name.strip(), c=code, t=now())
    view_row(rows[0]["id"], 1, create=True)
    return get_class(rows[0]["id"])


class ClassPatch(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    active_module: Optional[int] = None
    archived: Optional[bool] = None


@app.patch("/api/t/classes/{cid}")
@db.batched
def patch_class(cid: int, body: ClassPatch, _=Depends(teacher)):
    get_class(cid)
    if body.name is not None:
        db.x("UPDATE classes SET name=:n WHERE id=:id", n=body.name.strip(), id=cid)
    if body.active_module is not None:
        if body.active_module not in MODULES or body.active_module == 0:
            raise HTTPException(400, "Buổi không hợp lệ")
        db.x("UPDATE classes SET active_module=:m WHERE id=:id", m=body.active_module, id=cid)
        view_row(cid, body.active_module, create=True)
    if body.archived is not None:
        db.x("UPDATE classes SET archived=:a WHERE id=:id", a=1 if body.archived else 0, id=cid)
    bump(cid)
    return get_class(cid)


@app.delete("/api/t/classes/{cid}")
def delete_class(cid: int, _=Depends(teacher)):
    get_class(cid)
    db.x("DELETE FROM classes WHERE id=:id", id=cid)
    return {"ok": True}


@app.get("/api/t/module/{no}")
def teacher_module(no: int, _=Depends(teacher)):
    if no not in MODULES:
        raise HTTPException(404)
    m = MODULES[no]
    return {**m, "activities": [ACTIVITIES[a["id"]] for a in m["activities"]]}


@app.get("/api/t/answers")
def answer_index(_=Depends(teacher)):
    return [{"id": aid, "title": a["title"], "module": a["module"]} for aid, a in ACTIVITIES.items() if aid in ANSWER_KEYS]


@app.get("/api/t/answers/{aid}")
def answer_key(aid: str, _=Depends(teacher)):
    if aid not in ANSWER_KEYS:
        raise HTTPException(404, "Bài này chưa có đáp án cho giảng viên.")
    return {**ANSWER_KEYS[aid], "activity": ACTIVITIES[aid]}


@app.get("/api/t/labs/rls/{bai}")
def rls_solution(bai: str, _=Depends(teacher)):
    # bài mẫu hoàn chỉnh của phòng thí nghiệm RLS (tools/build_rls_solutions.cjs dựng); không đặt trong /static để học viên không tải được
    path = BASE / "answer_keys" / "rls_solutions" / f"{bai}.json"
    if not bai.isalnum() or not path.is_file():
        raise HTTPException(404, "Bài này chưa có bài mẫu trên phòng thí nghiệm RLS.")
    return json.loads(path.read_text(encoding="utf-8"))


@app.get("/api/t/classes/{cid}/state")
@db.batched
def teacher_state(cid: int, module: Optional[int] = None, _=Depends(teacher)):
    cls = get_class(cid)
    no = module if module in MODULES else cls["active_module"]
    view = view_row(cid, no, create=no != 0) if no != 0 else None
    t = now()
    students = db.q("""SELECT id, name, group_name, last_seen, created_at, phone_hash IS NOT NULL AS by_phone
                       FROM students WHERE class_id=:c ORDER BY name""", c=cid)
    for s in students:
        s["online"] = t - s["last_seen"] < ONLINE_SECONDS
        s["by_phone"] = bool(s["by_phone"])
        s["joined"] = s["last_seen"] > s["created_at"]
    states = activity_states(cid)
    counts = {r["activity_id"]: r["n"] for r in
              db.q("SELECT activity_id, COUNT(*) AS n FROM responses WHERE class_id=:c GROUP BY activity_id", c=cid)}
    acts = [{"id": a["id"], "title": a["title"], "type": a["type"],
             "status": states.get(a["id"], "hidden"), "count": counts.get(a["id"], 0)}
            for a in MODULES[no]["activities"]]
    return {"cls": cls, "module": no, "view": view, "students": students, "activities": acts}


class ViewIn(BaseModel):
    module: int
    current_section: Optional[str] = Field(default=None, max_length=10)
    unlocked: Optional[int] = None
    follow: Optional[bool] = None
    stage: Optional[int] = None


@app.post("/api/t/classes/{cid}/view")
@db.batched
def set_view(cid: int, body: ViewIn, _=Depends(teacher)):
    get_class(cid)
    if body.module not in MODULES or body.module == 0:
        raise HTTPException(400, "Buổi không hợp lệ")
    v = view_row(cid, body.module, create=True)
    n = len(MODULES[body.module]["sections"])
    cur = body.current_section or v["current_section"]
    unlocked = v["unlocked"] if body.unlocked is None else max(-1, body.unlocked)
    if unlocked >= n - 1:
        # "Mở toàn bộ" gồm cả các phần thêm vào giáo trình sau này
        unlocked = OPEN_ALL
    if body.current_section:
        # trình chiếu phần nào thì tự mở đến phần đó
        unlocked = max(unlocked, section_index(body.module, cur))
    follow = v["follow"] if body.follow is None else int(body.follow)
    stage = v["stage"] if body.stage is None else max(0, min(body.stage, 20))
    db.x("""UPDATE class_modules SET current_section=:s, unlocked=:u, follow=:f, stage=:st, updated_at=:t
            WHERE class_id=:c AND module_no=:m""",
         s=cur, u=unlocked, f=follow, st=stage, t=now(), c=cid, m=body.module)
    bump(cid)
    return view_row(cid, body.module)


class StatusIn(BaseModel):
    status: Literal["hidden", "open", "closed", "revealed"]


@app.post("/api/t/classes/{cid}/activities/{aid}")
@db.batched
def set_activity_status(cid: int, aid: str, body: StatusIn, _=Depends(teacher)):
    get_class(cid)
    a = get_activity(aid)
    db.x("""INSERT INTO activity_states (class_id, activity_id, status, updated_at) VALUES (:c, :a, :s, :t)
            ON CONFLICT (class_id, activity_id) DO UPDATE SET status=excluded.status, updated_at=excluded.updated_at""",
         c=cid, a=aid, s=body.status, t=now())
    if body.status != "hidden":
        view_row(cid, a["module"], create=True)
    bump(cid)
    return {"ok": True, "status": body.status}


def mcq_stats(cid, a):
    rows = db.q("SELECT payload FROM responses WHERE class_id=:c AND activity_id=:a", c=cid, a=a["id"])
    stats = {}
    for qq in a["questions"]:
        stats[qq["id"]] = {"counts": {o["key"]: 0 for o in qq["options"]}, "correct": 0, "n": 0}
    for r in rows:
        ans = json.loads(r["payload"]).get("answers", {})
        for qq in a["questions"]:
            g = ans.get(qq["id"])
            if g is None or g == []:
                continue
            s = stats[qq["id"]]
            s["n"] += 1
            for k in (g if isinstance(g, list) else [g]):
                if k in s["counts"]:
                    s["counts"][k] += 1
            ok = (g == qq.get("correct")) if a["type"] == "mcq" else sorted(g) == sorted(qq.get("correct", []))
            s["correct"] += 1 if ok else 0
    return {"n": len(rows), "questions": stats}


@app.get("/api/t/classes/{cid}/activities/{aid}/results")
@db.batched
def activity_results(cid: int, aid: str, _=Depends(teacher)):
    get_class(cid)
    a = get_activity(aid)
    rows = db.q("""SELECT r.id, r.owner_key, r.student_id, r.payload,
                          COALESCE(r.score, g.score) AS score, COALESCE(r.max_score, g.max_score) AS max_score,
                          g.feedback, g.graded_at, r.version, r.updated_by,
                          r.updated_at, s.name AS student_name
                   FROM responses r LEFT JOIN students s ON s.id = r.student_id
                   LEFT JOIN response_grades g ON g.response_id=r.id AND g.response_version=r.version
                   WHERE r.class_id=:c AND r.activity_id=:a ORDER BY r.updated_at""", c=cid, a=aid)
    for r in rows:
        r["payload"] = json.loads(r["payload"])
    out = {"activity": a, "status": activity_states(cid).get(aid, "hidden"), "responses": rows}
    submitted = {r["student_id"] for r in rows}
    out["not_submitted"] = [s for s in db.q("SELECT id, name FROM students WHERE class_id=:c ORDER BY name", c=cid)
                            if s["id"] not in submitted]
    if a["type"] in ("mcq", "multi"):
        out["stats"] = mcq_stats(cid, a)
    return out


class GradeIn(BaseModel):
    version: int = Field(ge=1)
    score: float = Field(ge=0, le=1000, allow_inf_nan=False)
    max_score: float = Field(gt=0, le=1000, allow_inf_nan=False)
    feedback: str = Field(default="", max_length=4000)


@app.post("/api/t/classes/{cid}/responses/{rid}/grade")
@db.batched
def grade_response(cid: int, rid: int, body: GradeIn, _=Depends(teacher)):
    response = db.q1("SELECT * FROM responses WHERE id=:r AND class_id=:c", r=rid, c=cid)
    if not response:
        raise HTTPException(404, "Không tìm thấy bài nộp trong lớp này")
    if get_activity(response["activity_id"])["type"] not in ("open", "practice"):
        raise HTTPException(400, "Bài trắc nghiệm đã được chấm tự động")
    if body.score > body.max_score:
        raise HTTPException(400, "Điểm không được lớn hơn điểm tối đa")
    saved = db.x("""INSERT INTO response_grades
                    (response_id, response_version, score, max_score, feedback, graded_at)
                    SELECT id, version, :s, :m, :f, :t FROM responses
                    WHERE id=:r AND class_id=:c AND version=:v
                    ON CONFLICT (response_id) DO UPDATE SET
                    response_version=excluded.response_version, score=excluded.score,
                    max_score=excluded.max_score, feedback=excluded.feedback, graded_at=excluded.graded_at
                    RETURNING response_id""",
                 s=body.score, m=body.max_score, f=body.feedback.strip(), t=now(), r=rid, c=cid, v=body.version)
    if not saved:
        raise HTTPException(409, "Học viên đã nộp bản mới. Vui lòng tải lại bài và chấm bản nộp mới nhất.")
    return {"ok": True}


@app.delete("/api/t/classes/{cid}/responses/{rid}")
def delete_response(cid: int, rid: int, _=Depends(teacher)):
    db.x("DELETE FROM responses WHERE id=:id AND class_id=:c", id=rid, c=cid)
    return {"ok": True}


@app.delete("/api/t/classes/{cid}/students/{sid}")
def delete_student(cid: int, sid: int, _=Depends(teacher)):
    db.x("DELETE FROM responses WHERE student_id=:id AND class_id=:c AND owner_key=:o", id=sid, c=cid, o=f"s:{sid}")
    db.x("DELETE FROM students WHERE id=:id AND class_id=:c", id=sid, c=cid)
    return {"ok": True}


class RosterIn(BaseModel):
    text: str = Field(max_length=50_000)


def add_roster(cid, text):
    """Mỗi dòng: Họ và tên, số điện thoại[, đơn vị]; phân tách bằng tab, dấu phẩy hoặc chấm phẩy."""
    added, updated, errors = 0, 0, []
    for no, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        sep = "	" if "	" in line else (";" if ";" in line else ",")
        cells = [x.strip() for x in line.split(sep)]
        idx = next((i for i, x in enumerate(cells) if norm_phone(x)), None)
        name = cells[0] if cells else ""
        if idx is None or idx == 0 or len(name) < 2:
            errors.append(f"Dòng {no}: cần có họ tên và số điện thoại 10 số")
            continue
        phone = norm_phone(cells[idx])
        unit = ", ".join(x for i, x in enumerate(cells) if i not in (0, idx) and x)[:200]
        ph = phone_hash(phone)
        old = db.q1("SELECT id FROM students WHERE class_id=:c AND phone_hash=:p", c=cid, p=ph)
        if old:
            db.x("UPDATE students SET name=:n, group_name=:g WHERE id=:id", n=name[:60], g=unit, id=old["id"])
            updated += 1
        else:
            t = now()
            # token_hash/rejoin_hash ngẫu nhiên: chỉ đăng nhập được bằng số điện thoại
            db.x("""INSERT INTO students (class_id, name, group_name, token_hash, rejoin_hash, phone_hash, created_at, last_seen)
                    VALUES (:c, :n, :g, :h, :r, :p, :t, :t)""",
                 c=cid, n=name[:60], g=unit, h=sha(secrets.token_urlsafe(32)), r=sha(secrets.token_urlsafe(32)), p=ph, t=t)
            added += 1
    return {"added": added, "updated": updated, "errors": errors}


@app.post("/api/t/classes/{cid}/roster")
def import_roster(cid: int, body: RosterIn, _=Depends(teacher)):
    get_class(cid)
    return add_roster(cid, body.text)


def _csv_safe(v):
    # chống CSV injection khi mở bằng Excel (buổi 6)
    s = "" if v is None else str(v)
    return "'" + s if s[:1] in ("=", "+", "-", "@", "\t", "\r") else s


@app.get("/api/t/classes/{cid}/export.csv")
def export_csv(cid: int, _=Depends(teacher)):
    cls = get_class(cid)
    rows = db.q("""SELECT r.activity_id, COALESCE(s.name, r.updated_by) AS student_name,
                          COALESCE(r.score, g.score) AS score, COALESCE(r.max_score, g.max_score) AS max_score,
                          g.feedback, r.payload, r.updated_at
                   FROM responses r LEFT JOIN students s ON s.id = r.student_id
                   LEFT JOIN response_grades g ON g.response_id=r.id AND g.response_version=r.version
                   WHERE r.class_id=:c ORDER BY r.activity_id, student_name""", c=cid)
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["Buổi", "Hoạt động", "Mã hoạt động", "Học viên", "Điểm", "Tối đa", "Thời gian", "Bài làm (JSON)", "Nhận xét"])
    for r in rows:
        a = ACTIVITIES.get(r["activity_id"], {})
        w.writerow([_csv_safe(x) for x in [
            a.get("module"), a.get("title"), r["activity_id"], r["student_name"], r["score"], r["max_score"],
            datetime.fromtimestamp(r["updated_at"], VN_TZ).strftime("%Y-%m-%d %H:%M"), r["payload"], r["feedback"]]])
    data = "﻿" + buf.getvalue()
    return Response(data, media_type="text/csv; charset=utf-8",
                    headers={"Content-Disposition": f'attachment; filename="ket-qua-lop-{cls["code"]}.csv"'})
