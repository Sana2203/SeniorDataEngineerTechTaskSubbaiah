
"""API client for retrieving posts and users from JSONPlaceholder."""

import logging

import requests

BASE_URL = "https://jsonplaceholder.typicode.com"
TIMEOUT_SECONDS = 20

logger = logging.getLogger(__name__)


def fetch_data(endpoint, session=None):
    """Fetch a list of records from a JSONPlaceholder endpoint.

    Args:
        endpoint: API resource, such as "posts" or "users".
        session: Optional requests-compatible session for testing.

    Returns:
        A list of dictionaries returned by the API.

    Raises:
        RuntimeError: If the HTTP request fails.
        ValueError: If the response is not a JSON list.
    """
    if endpoint not in {"posts", "users"}:
        raise ValueError(
            "Unsupported endpoint. Use 'posts' or 'users'."
        )

    client = session if session is not None else requests

    try:
        response = client.get(
            f"{BASE_URL}/{endpoint}",
            timeout=TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as exc:
        logger.exception("API request failed for endpoint %s", endpoint)
        raise RuntimeError(
            f"API request failed for endpoint '{endpoint}': {exc}"
        ) from exc
    except ValueError as exc:
        raise ValueError(
            f"Invalid JSON response from endpoint '{endpoint}'."
        ) from exc

    if not isinstance(data, list):
        raise ValueError(
            f"Expected a list of records from endpoint '{endpoint}'."
        )

    if not all(isinstance(item, dict) for item in data):
        raise ValueError(
            f"Expected each record from '{endpoint}' to be an object."
        )

    logger.info("Fetched %d records from %s", len(data), endpoint)
    return data


def fetch_posts(session=None):
    """Fetch all posts."""
    return fetch_data("posts", session=session)


def fetch_users(session=None):
    """Fetch all users."""
    return fetch_data("users", session=session)
