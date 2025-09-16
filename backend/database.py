import os
import json
from dotenv import load_dotenv

load_dotenv()

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

_ROOT = os.path.dirname(__file__)
_ROLES_FILE = os.path.join(_ROOT, 'data', 'roles.json')

# Lazy import of psycopg2 to avoid hard dependency when not available
try:
    import psycopg2
    from psycopg2.extras import Json
    _HAS_PG = True
except Exception:
    psycopg2 = None
    Json = None
    _HAS_PG = False

def _get_db_connection():
    if not _HAS_PG:
        raise RuntimeError('psycopg2 not available')
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        host=DB_HOST,
        port=DB_PORT
    )

def _load_roles_from_file():
    if not os.path.exists(_ROLES_FILE):
        return []
    with open(_ROLES_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def _write_roles_to_file(roles):
    os.makedirs(os.path.dirname(_ROLES_FILE), exist_ok=True)
    with open(_ROLES_FILE, 'w', encoding='utf-8') as f:
        json.dump(roles, f, indent=2, ensure_ascii=False)

def init_db():
    # Attempt to initialize Postgres; if unavailable, skip and rely on JSON file
    if not _HAS_PG:
        print('psycopg2 not installed; skipping DB init and using JSON fallback.')
        return
    try:
        conn = _get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS roles (
                id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                tags JSONB,
                required_skills JSONB
            );
        """)
        conn.commit()

        cursor.execute("SELECT COUNT(*) FROM roles;")
        if cursor.fetchone()[0] == 0:
            roles_data = _load_roles_from_file()
            if roles_data:
                print('Populating database with initial data...')
                for role in roles_data:
                    try:
                        add_role(role)
                    except Exception as e:
                        print(f'Failed to add role {role.get("title")} to DB: {e}')
                print('Database population complete.')

        cursor.close()
        conn.close()
    except Exception as e:
        print(f'Postgres init failed, falling back to JSON file. Error: {e}')

def get_roles(interest=None):
    # Try DB first; on any failure, return roles from JSON file
    if _HAS_PG:
        try:
            conn = _get_db_connection()
            cursor = conn.cursor()
            if interest:
                cursor.execute("SELECT * FROM roles WHERE tags @> %s;", (Json([interest]),))
            else:
                cursor.execute("SELECT * FROM roles;")
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            roles = []
            for r in rows:
                # Include description if it exists
                role_data = {'title': r[1], 'tags': r[2], 'requiredSkills': r[3]}
                if len(r) > 4 and r[4]:  # Check if description exists
                    role_data['description'] = r[4]
                roles.append(role_data)
            return roles
        except Exception as e:
            print(f'Postgres read failed, using JSON fallback. Error: {e}')

    # JSON fallback
    roles = _load_roles_from_file()
    if interest:
        filtered = [r for r in roles if interest in (r.get('tags') or [])]
        return filtered
    return roles

def add_role(role_data):
    # Try DB insert first; if it fails, append to JSON file
    if _HAS_PG:
        try:
            conn = _get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO roles (title, tags, required_skills) VALUES (%s, %s, %s);
            """, (role_data.get('title'), Json(role_data.get('tags') or []), Json(role_data.get('requiredSkills') or [])))
            conn.commit()
            cursor.close()
            conn.close()
            return
        except Exception as e:
            print(f'Postgres insert failed, falling back to JSON file. Error: {e}')

    # JSON append fallback
    roles = _load_roles_from_file() or []
    roles.append(role_data)
    _write_roles_to_file(roles)
