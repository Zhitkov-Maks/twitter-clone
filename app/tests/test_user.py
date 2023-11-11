from httpx import AsyncClient


async def test_get_user_me(ac: AsyncClient):
    """Test for obtaining information about a user with valid data."""
    response = await ac.get("/api/users/me", headers={"api-key": "test"})
    data = response.json()
    assert data.get("result"), data.get("user")
    assert response.status_code == 200


async def test_get_tweets_user_is_not_register(ac: AsyncClient):
    """Test for obtaining information about the
    user if the user is not in the database."""
    response = await ac.get("/api/users/me", headers={"api-key": "notRegisterUser"})
    data = response.json()
    assert not data.get("result")
    assert response.status_code == 404


async def test_get_user_by_id(ac: AsyncClient):
    """Test for obtaining information about the user by ID."""
    response = await ac.get("/api/users/1", headers={"api-key": "test"})
    data = response.json()
    assert data.get("result"), data.get("user")
    assert response.status_code == 200


async def test_get_user_by_id_not_exists(ac: AsyncClient):
    """Test for obtaining information about a user by ID,
    if the ID does not exist or has been deleted."""
    response = await ac.get("/api/users/100", headers={"api-key": "test"})
    data = response.json()
    assert not data.get("result"), not data.get("user")
    assert response.status_code == 404


async def test_user_add_followed(ac: AsyncClient):
    """Test for adding a subscription to another user."""
    response = await ac.post("/api/users/4/follow", headers={"api-key": "test"})
    data = response.json()
    assert data.get("result")
    assert response.status_code == 201


async def test_user_add_followed_twice(ac: AsyncClient):
    """Test for the inability to subscribe twice, and the service does not crash."""
    response = await ac.post("/api/users/4/follow", headers={"api-key": "test"})
    data = response.json()
    assert not data.get("result")
    assert data.get("detail").get("error_message") == "You are already subscribed"
    assert response.status_code == 400


async def test_user_remove_followed(ac: AsyncClient):
    """Test for removing a user's subscription."""
    response = await ac.delete("/api/users/4/follow", headers={"api-key": "test"})
    data = response.json()
    assert data.get("result")
    assert response.status_code == 200


async def test_user_remove_followed_twice(ac: AsyncClient):
    """Test for removing a user's subscription twice and the service does not crash."""
    response = await ac.delete("/api/users/4/follow", headers={"api-key": "test"})
    data = response.json()
    assert not data.get("result")
    assert data.get("detail").get("error_message") == "You are not following this user"
    assert response.status_code == 404


async def test_user_add_followed_not_exists_user(ac: AsyncClient):
    """Test for trying to subscribe to a user who is not in the database."""
    response = await ac.post("/api/users/100/follow", headers={"api-key": "test"})
    data = response.json()
    assert data.get("detail").get("error_type") == "Not Found"
    assert response.status_code == 404
