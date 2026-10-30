1. Find the top 5 users with the highest number of posts.
2. For each of these top 5 users, calculate the average post length.
3. Identify the day of the week when the most `lengthy` posts are created (assume all posts were created in the UTC timezone).

# SQL Analysis Answers

## Question 1: Top five users with the longest posts

**Approach:** Join users to posts, calculate the maximum body length
for each user, and sort in descending order. The title is excluded.

**SQL:** See Question 1 in `sample_queries.sql`.

## Question 2: Average post length for the top five users

**Approach:** Use the same five users ranked in Question 1.
Calculate the average of title length plus body length for each user.

The `post_length` column is calculated as:

`length(title) + length(body)`

**SQL:** See Question 2 in `sample_queries.sql`.

## Question 3: Weekday with the most lengthy posts

**Approach:** Filter posts where status is `lengthy`. Treat each post
ID as a day offset from 1970-01-01, group by weekday, and count posts.

SQLite weekday numbering:
- Sunday = 0
- Monday = 1
- Tuesday = 2
- Wednesday = 3
- Thursday = 4
- Friday = 5
- Saturday = 6

**SQL:** See Question 3 in `sample_queries.sql`.

## Assumptions

1. A post is `lengthy` only when its body contains more than 150
   characters. Exactly 150 characters is `concise`.
2. Question 1 ranks users by their longest individual post body.
3. Question 2 calculates the average across all posts belonging to
   those same five users.
4. Post IDs are interpreted as days after the Unix epoch.
5. Ties are resolved deterministically using user ID or weekday number.

## Actual Results

Run the queries against the database created by `main.py` and record
the actual result rows here before submitting.
