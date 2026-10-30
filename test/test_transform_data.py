
import json
import pytest

from main import transform_data


def sample_users():
    return [{
        "id": 1,
        "name": "Ada Example",
        "email": "ada@example.com",
        "address": {"city": "London"},
        "company": {"name": "Example Inc"}
    }]


def sample_posts(body):
    return [{
        "id": 10,
        "userId": 1,
        "title": "Hello",
        "body": body
    }]


def test_status_boundary():
    concise = transform_data(
        sample_posts("x" * 150), sample_users()
    )[0]
    lengthy = transform_data(
        sample_posts("x" * 151), sample_users()
    )[0]

    assert concise["status"] == "concise"
    assert concise["body_length"] == 150
    assert concise["post_length"] == 155
    assert lengthy["status"] == "lengthy"
    assert lengthy["body_length"] == 151


def test_user_enrichment_and_nested_json():
    row = transform_data(
        sample_posts("body"), sample_users()
    )[0]

    assert row["user_name"] == "Ada Example"
    assert row["user_email"] == "ada@example.com"
    assert json.loads(row["address_json"])["city"] == "London"
    assert json.loads(row["company_json"])["name"] == "Example Inc"


def test_missing_user_raises_error():
    with pytest.raises(ValueError, match="Unknown user ID"):
        transform_data(sample_posts("body"), [])
