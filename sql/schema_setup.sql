-- SQL queries to set up schemas in BigQuery


PRAGMA foreign_keys = ON;

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
    status TEXT NOT NULL
        CHECK (status IN ('lengthy', 'concise')),
    FOREIGN KEY (user_id) REFERENCES sc_users(user_id)
);

CREATE INDEX IF NOT EXISTS idx_sc_posts_user_id
    ON sc_posts(user_id);

CREATE INDEX IF NOT EXISTS idx_sc_posts_status
    ON sc_posts(status);
