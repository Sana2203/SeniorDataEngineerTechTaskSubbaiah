-- Write SQL queries to answer these questions using the data you have loaded into BigQuery:
-- 1. Find the top 5 users with the highest number of posts.
-- 2. For each of these top 5 users, calculate the average post length.
-- 3. Identify the day of the week when the most `lengthy` posts are created (assume all posts were created in the UTC timezone).


-- QUESTION 1:
-- Find the top five users by their longest post body.
-- The title is excluded from this ranking.

SELECT
    u.user_id,
    u.name,
    MAX(p.body_length) AS longest_body_length
FROM sc_users AS u
JOIN sc_posts AS p
    ON u.user_id = p.user_id
GROUP BY
    u.user_id,
    u.name
ORDER BY
    longest_body_length DESC,
    u.user_id ASC
LIMIT 5;


-- QUESTION 2:
-- Calculate average post length, including title,
-- for the same top five users.

WITH user_stats AS (
    SELECT
        u.user_id,
        u.name,
        MAX(p.body_length) AS longest_body_length,
        AVG(p.post_length * 1.0) AS average_post_length
    FROM sc_users AS u
    JOIN sc_posts AS p
        ON u.user_id = p.user_id
    GROUP BY
        u.user_id,
        u.name
),
top_five AS (
    SELECT *
    FROM user_stats
    ORDER BY
        longest_body_length DESC,
        user_id ASC
    LIMIT 5
)
SELECT
    user_id,
    name,
    longest_body_length,
    ROUND(average_post_length, 2)
        AS average_post_length_including_title
FROM top_five
ORDER BY
    longest_body_length DESC,
    user_id ASC;


-- QUESTION 3:
-- Find the weekday with the most lengthy posts.
-- Each post ID represents a day offset after the Unix epoch.
-- SQLite: Sunday=0, Monday=1, ..., Saturday=6.

WITH lengthy_by_weekday AS (
    SELECT
        strftime(
            '%w',
            date('1970-01-01', '+' || post_id || ' days')
        ) AS weekday_number,
        COUNT(*) AS lengthy_post_count
    FROM sc_posts
    WHERE status = 'lengthy'
    GROUP BY weekday_number
)
SELECT
    CASE weekday_number
        WHEN '0' THEN 'Sunday'
        WHEN '1' THEN 'Monday'
        WHEN '2' THEN 'Tuesday'
        WHEN '3' THEN 'Wednesday'
        WHEN '4' THEN 'Thursday'
        WHEN '5' THEN 'Friday'
        WHEN '6' THEN 'Saturday'
    END AS weekday,
    lengthy_post_count
FROM lengthy_by_weekday
ORDER BY
    lengthy_post_count DESC,
    weekday_number ASC
LIMIT 1;
