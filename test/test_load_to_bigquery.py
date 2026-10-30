
import sqlite3

from main import load_data, transform_data


def test_database_load_and_rerun(tmp_path):
    db_path = tmp_path / "test_blog.db"

    users = [{
        "id": 1,
        "name": "Ada",
        "email": "ada@example.com",
        "address": {},
        "company": {}
    }]

    posts = [{
        "id": 10,
        "userId": 1,
        "title": "Hello",
        "body": "Sample post"
    }]

    transformed = transform_data(posts, users)

    load_data(db_path, users, transformed)
    load_data(db_path, users, transformed)

    with sqlite3.connect(db_path) as conn:
        user_count = conn.execute(
            "SELECT COUNT(*) FROM sc_users"
        ).fetchone()[0]

        post_count = conn.execute(
            "SELECT COUNT(*) FROM sc_posts"
        ).fetchone()[0]

        status = conn.execute(
            "SELECT status FROM sc_posts WHERE post_id = 10"
        ).fetchone()[0]

    assert user_count == 1
    assert post_count == 1
    assert status == "concise"
