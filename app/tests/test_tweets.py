"""Module for testing work with tweets."""
from httpx import AsyncClient


async def test_get_all_tweets(ac: AsyncClient):
    """Tweet list extraction test."""
    response = await ac.get("/api/tweets", headers={"api-key": "test"})
    data = response.json()
    assert data.get("result"), len(data.get("tweets")) > 0
    assert response.status_code == 200


async def test_get_tweets_user_is_not_register(ac: AsyncClient):
    """Operation execution test if the user is not registered."""
    response = await ac.get("/api/tweets", headers={"api-key": "kfdjjhfhf"})
    data = response.json()
    assert not data.get("result")
    assert response.status_code == 404


async def test_add_tweets(ac: AsyncClient):
    """Test for adding a tweet"""
    response = await ac.post(
        "/api/tweets",
        headers={"api-key": "test"},
        json={
            "tweet_data": "Какое-то безумно важное послание",
            "tweet_media_ids": [1],
        },
    )
    data = response.json()
    assert data.get("result"), data.get("tweet_id")
    assert response.status_code == 201


async def test_add_tweets_not_valid_data(ac: AsyncClient):
    """Add test if required field is missing."""
    response = await ac.post(
        "/api/tweets",
        headers={"api-key": "test"},
        json={"tweet_data": "Какое-то безумно важное послание"},
    )
    assert response.status_code == 422


async def test_delete_tweet(ac: AsyncClient):
    """Tweet deletion test."""
    response = await ac.delete("/api/tweets/3", headers={"api-key": "test"})
    data = response.json()
    assert response.status_code == 200
    assert data.get("result")


async def test_delete_tweet_if_tweet_written_someone_else(ac: AsyncClient):
    """Deletion test if the tweet was posted by another user."""
    response = await ac.delete("/api/tweets/2", headers={"api-key": "qwerty"})
    data = response.json()
    assert response.status_code == 403
    assert not data.get("result")
    assert "You do not have permission to delete this tweet" == data.get(
        "detail").get("error_message")


async def test_delete_tweets_not_tweet_id(ac: AsyncClient):
    """Test for deleting a non-existent tweet."""
    response = await ac.delete("/api/tweets/100", headers={"api-key": "test"})
    data = response.json()
    assert not data.get("result")
    assert response.status_code == 404


async def test_add_like(ac: AsyncClient):
    """Testing adding likes"""
    response = await ac.post("/api/tweets/2/likes", headers={"api-key": "test"})
    assert response.status_code == 201


async def test_added_like_twice(ac: AsyncClient):
    """Testing adding likes twice"""
    response = await ac.post("/api/tweets/2/likes", headers={"api-key": "test"})
    data = response.json()
    assert response.status_code == 400
    assert data.get("detail").get("error_message") == "Can't like twice."


async def test_delete_like(ac: AsyncClient):
    """Like removal test"""
    response = await ac.delete("/api/tweets/2/likes", headers={"api-key": "test"})
    assert response.status_code == 200


async def test_delete_like_twice(ac: AsyncClient):
    """Trying to remove the like again"""
    response = await ac.delete("/api/tweets/2/likes", headers={"api-key": "test"})
    data = response.json()
    assert response.status_code == 404
    assert data.get("detail").get("error_message") == "No like found to delete it."
