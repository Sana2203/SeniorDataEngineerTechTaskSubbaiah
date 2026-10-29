
"""Load users and transformed posts into a local SQLite database."""

import json
import logging
import sqlite3

logger = logging.getLogger(__name__)


SCHEMA = """
CREATE TABLE IF NOT EXISTS SC_users (
    user_id INTEGER PRIMARY KEY,
    name TEXT,
    username TEXT,
    email TEXT,
    address_json TEXT,
    phone TEXT,
    website TEXT,
    company_json TEXT
);

CREATE TABLE IF NOT EXISTS SC_posts (
    post_id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    body_length INTEGER NOT NULL,
    post_length INTEGER NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('lengthy', 'concise')),
    user_name TEXT,
    user_email TEXT,
    address_json TEXT,
    company_json TEXT,
    FOREIGN KEY (user_id) REFERENCES SC_users(user_id)
);

CREATE INDEX IF NOT EXISTS idx_sc_posts_user_id
ON SC_posts(user_id);

CREATE INDEX IF NOT EXISTS idx_sc_posts_status
ON SC_posts(status);
"""


def load_to_database(db_path, users, posts):
    """Create tables and upsert users and transformed posts.

    Args:
        db_path: SQLite database file path, e.g. "etl_data.db".
        users: Raw user records from JSONPlaceholder.
        posts: Transformed post records from transform_data().
    """
    if not isinstance(users, list) or not isinstance(posts, list):
        raise ValueError("users and posts must both be lists.")

    connection = sqlite3.connect(db_path)

    try:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.executescript(SCHEMA)

        with connection:
            user_rows = [
                (
                    user["id"],
                    user.get("name"),
                    user.get("username"),
                    user.get("email"),
                    json.dumps(user.get("address", {}), sort_keys=True),
                    user.get("phone"),
                    user.get("website"),
                    json.dumps(user.get("company", {}), sort_keys=True),
                )
                for user in users
            ]

            connection.executemany(
                """
                INSERT INTO SC_users (
                    user_id, name, username, email,
                    address_json, phone, website, company_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    name = excluded.name,
                    username = excluded.username,
                    email = excluded.email,
                    address_json = excluded.address_json,
                    phone = excluded.phone,
                    website = excluded.website,
                    company_json = excluded.company_json
                """,
                user_rows,
            )

            post_rows = [
                (
                    post["post_id"],
                    post["user_id"],
                    post["title"],
                    post["body"],
                    post["body_length"],
                    post["post_length"],
                    post["status"],
                    post.get("user_name"),
                    post.get("user_email"),
                    post.get("address_json"),
                    post.get("company_json"),
                )
                for post in posts
            ]

            connection.executemany(
                """
                INSERT INTO SC_posts (
                    post_id, user_id, title, body,
                    body_length, post_length, status,
                    user_name, user_email, address_json, company_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(post_id) DO UPDATE SET
                    user_id = excluded.user_id,
                    title = excluded.title,
                    body = excluded.body,
                    body_length = excluded.body_length,
                    post_length = excluded.post_length,
                    status = excluded.status,
                    user_name = excluded.user_name,
                    user_email = excluded.user_email,
                    address_json = excluded.address_json,
                    company_json = excluded.company_json
                """,
                post_rows,
            )

        logger.info(
            "Loaded %d users and %d posts into %s",
            len(users),
            len(posts),
            db_path,
        )

    except Exception:
        connection.rollback()
        logger.exception("Database load failed")
        raise
    finally:
        connection.close()


# Optional compatibility alias if other files import load_data().
def load_data(db_path, users, posts):
    """Alias for load_to_database()."""
    return load_to_database(db_path, users, posts)
