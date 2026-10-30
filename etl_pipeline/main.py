
import argparse
import logging
import sqlite3
from pathlib import Path

import requests

BASE_URL = "https://jsonplaceholder.typicode.com"


def fetch_data(endpoint):
    """Extract records from JSONPlaceholder."""
    response = requests.get(f"{BASE_URL}/{endpoint}", timeout=20)
    response.raise_for_status()
    data = response.json()

    if not isinstance(data, list):
        raise ValueError(f"Expected a list from {endpoint}")

    return data


def transform_data(posts, users):
    """Enrich posts with user details and calculate post status."""
    users_by_id = {user["id"]: user for user in users}
    result = []

    for post in posts:
        user = users_by_id.get(post["userId"])
        if user is None:
            raise ValueError(f"Unknown user ID: {post['userId']}")

        title = post.get("title", "")
        body = post.get("body", "")
        address = user.get("address", {})
        company = user.get("company", {})

        result.append({
            "post_id": post["id"],
            "user_id": post["userId"],
            "title": title,
            "body": body,
            "body_length": len(body),
            "post_length": len(title) + len(body),
            "status": "lengthy" if len(body) > 150 else "concise",
            "user_name": user.get("name", ""),
            "user_email": user.get("email", ""),
            "address_json": __import__("json").dumps(address),
            "company_json": __import__("json").dumps(company),
        })

    return result


def load_data(db_path, users, posts):
    """Load transformed data into SQLite."""
    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON")

        conn.executescript("""
            CREATE TABLE IF NOT EXISTS sc_users (
                user_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT,
                address_json TEXT,
                company_json TEXT
            );

            CREATE TABLE IF NOT EXISTS sc_posts (
                post_id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                body TEXT NOT NULL,
                body_length INTEGER NOT NULL,
                post_length INTEGER NOT NULL,
                status TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES sc_users(user_id)
            );
        """)

        with conn:
            conn.executemany("""
                INSERT INTO sc_users
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    name=excluded.name,
                    email=excluded.email,
                    address_json=excluded.address_json,
                    company_json=excluded.company_json
            """, [
                (
                    u["id"], u.get("name", ""), u.get("email", ""),
                    __import__("json").dumps(u.get("address", {})),
                    __import__("json").dumps(u.get("company", {}))
                )
                for u in users
            ])

            conn.executemany("""
                INSERT INTO sc_posts
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(post_id) DO UPDATE SET
                    user_id=excluded.user_id,
                    title=excluded.title,
                    body=excluded.body,
                    body_length=excluded.body_length,
                    post_length=excluded.post_length,
                    status=excluded.status
            """, [
                (
                    p["post_id"], p["user_id"], p["title"], p["body"],
                    p["body_length"], p["post_length"], p["status"]
                )
                for p in posts
            ])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default="sc_blog.db")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    users = fetch_data("users")
    posts = fetch_data("posts")
    transformed_posts = transform_data(posts, users)
    load_data(args.db, users, transformed_posts)

    print(f"ETL successful: {len(users)} users, "
          f"{len(transformed_posts)} posts loaded into {args.db}")


if __name__ == "__main__":
    main()
