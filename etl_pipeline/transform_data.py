
"""Transform and enrich JSONPlaceholder post records."""

import json

LENGTHY_POST_THRESHOLD = 150


def transform_data(posts, users):
    """Enrich posts with user information and calculated fields.

    Args:
        posts: List of post dictionaries.
        users: List of user dictionaries.

    Returns:
        A list of transformed post dictionaries.

    Raises:
        ValueError: If required fields are missing or a post references
            a user that does not exist.
    """
    if not isinstance(posts, list) or not isinstance(users, list):
        raise ValueError("posts and users must both be lists.")

    users_by_id = {}

    for user in users:
        if "id" not in user:
            raise ValueError("Each user must contain an 'id' field.")
        users_by_id[user["id"]] = user

    transformed_posts = []

    for post in posts:
        required_fields = ("id", "userId", "title", "body")
        missing_fields = [
            field for field in required_fields if field not in post
        ]

        if missing_fields:
            raise ValueError(
                f"Post is missing required fields: {missing_fields}"
            )

        user_id = post["userId"]
        user = users_by_id.get(user_id)

        if user is None:
            raise ValueError(
                f"Post {post['id']} references unknown userId {user_id}."
            )

        body = post["body"]
        title = post["title"]

        if not isinstance(body, str) or not isinstance(title, str):
            raise ValueError(
                f"Post {post['id']} title and body must be strings."
            )

        address = user.get("address", {})
        company = user.get("company", {})

        transformed_posts.append(
            {
                "post_id": post["id"],
                "user_id": user_id,
                "title": title,
                "body": body,
                "body_length": len(body),
                "post_length": len(title) + len(body),
                "status": (
                    "lengthy"
                    if len(body) > LENGTHY_POST_THRESHOLD
                    else "concise"
                ),
                "user_name": user.get("name"),
                "user_email": user.get("email"),
                "address_json": json.dumps(
                    address, sort_keys=True
                ),
                "company_json": json.dumps(
                    company, sort_keys=True
                ),
            }
        )

    return transformed_posts
