"""Kết nối cơ sở dữ liệu: Supabase Postgres khi có DATABASE_URL, SQLite khi chạy thử trên máy."""
import os

from sqlalchemy import create_engine, event, text

_url = os.environ.get("DATABASE_URL", "").strip()
if _url.startswith("postgres://"):
    _url = "postgresql+psycopg://" + _url[len("postgres://"):]
elif _url.startswith("postgresql://"):
    _url = "postgresql+psycopg://" + _url[len("postgresql://"):]

IS_PG = bool(_url)

if IS_PG:
    # prepare_threshold=None: tương thích với Supabase pooler (chế độ transaction, cổng 6543)
    engine = create_engine(_url, pool_pre_ping=True, pool_size=5, max_overflow=5, pool_recycle=300,
                           connect_args={"prepare_threshold": None})
else:
    engine = create_engine("sqlite:///" + os.environ.get("SQLITE_PATH", "local.db"),
                           connect_args={"check_same_thread": False})

    @event.listens_for(engine, "connect")
    def _sqlite_pragmas(conn, _):
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("PRAGMA journal_mode=WAL")

ID = "BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY" if IS_PG else "INTEGER PRIMARY KEY AUTOINCREMENT"

SCHEMA = [
    f"""CREATE TABLE IF NOT EXISTS classes (
        id {ID},
        name TEXT NOT NULL,
        code TEXT NOT NULL UNIQUE,
        active_module INTEGER NOT NULL DEFAULT 1,
        archived INTEGER NOT NULL DEFAULT 0,
        created_at DOUBLE PRECISION NOT NULL
    )""",
    """CREATE TABLE IF NOT EXISTS class_modules (
        class_id BIGINT NOT NULL REFERENCES classes(id) ON DELETE CASCADE,
        module_no INTEGER NOT NULL,
        current_section TEXT NOT NULL DEFAULT 's0',
        unlocked INTEGER NOT NULL DEFAULT 0,
        follow INTEGER NOT NULL DEFAULT 1,
        stage INTEGER NOT NULL DEFAULT 1,
        updated_at DOUBLE PRECISION NOT NULL,
        PRIMARY KEY (class_id, module_no)
    )""",
    f"""CREATE TABLE IF NOT EXISTS students (
        id {ID},
        class_id BIGINT NOT NULL REFERENCES classes(id) ON DELETE CASCADE,
        name TEXT NOT NULL,
        group_name TEXT NOT NULL,
        token_hash TEXT NOT NULL UNIQUE,
        rejoin_hash TEXT NOT NULL,
        created_at DOUBLE PRECISION NOT NULL,
        last_seen DOUBLE PRECISION NOT NULL
    )""",
    "CREATE INDEX IF NOT EXISTS students_class ON students(class_id)",
    """CREATE TABLE IF NOT EXISTS activity_states (
        class_id BIGINT NOT NULL REFERENCES classes(id) ON DELETE CASCADE,
        activity_id TEXT NOT NULL,
        status TEXT NOT NULL,
        updated_at DOUBLE PRECISION NOT NULL,
        PRIMARY KEY (class_id, activity_id)
    )""",
    f"""CREATE TABLE IF NOT EXISTS responses (
        id {ID},
        class_id BIGINT NOT NULL REFERENCES classes(id) ON DELETE CASCADE,
        activity_id TEXT NOT NULL,
        owner_key TEXT NOT NULL,
        student_id BIGINT REFERENCES students(id) ON DELETE CASCADE,
        group_name TEXT,
        payload TEXT NOT NULL,
        score DOUBLE PRECISION,
        max_score DOUBLE PRECISION,
        version INTEGER NOT NULL DEFAULT 1,
        updated_by TEXT NOT NULL,
        updated_at DOUBLE PRECISION NOT NULL,
        UNIQUE (class_id, activity_id, owner_key)
    )""",
    """CREATE TABLE IF NOT EXISTS response_grades (
        response_id BIGINT PRIMARY KEY REFERENCES responses(id) ON DELETE CASCADE,
        response_version INTEGER NOT NULL,
        score DOUBLE PRECISION NOT NULL,
        max_score DOUBLE PRECISION NOT NULL,
        feedback TEXT NOT NULL DEFAULT '',
        graded_at DOUBLE PRECISION NOT NULL
    )""",
]

TABLES = ["classes", "class_modules", "students", "activity_states", "responses", "response_grades"]


def init_db():
    with engine.begin() as c:
        for stmt in SCHEMA:
            c.execute(text(stmt))
        if IS_PG:
            # Supabase tự mở các bảng trong schema public qua Data API (khóa anon).
            # Bật RLS và không tạo policy nào => API công khai không đọc/ghi được;
            # chỉ ứng dụng (kết nối bằng chuỗi DATABASE_URL) truy cập.
            for t in TABLES:
                c.execute(text(f"ALTER TABLE {t} ENABLE ROW LEVEL SECURITY"))


def q(sql, **params):
    with engine.connect() as c:
        return [dict(r._mapping) for r in c.execute(text(sql), params)]


def q1(sql, **params):
    rows = q(sql, **params)
    return rows[0] if rows else None


def x(sql, **params):
    with engine.begin() as c:
        res = c.execute(text(sql), params)
        return [dict(r._mapping) for r in res] if res.returns_rows else []
