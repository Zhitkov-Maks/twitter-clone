from httpx import AsyncClient


async def test_get_user_me(ac: AsyncClient):
    response = await ac.get("/api/users/me", headers={"api-key": "test"})
    data = response.json()
    assert data.get("result"), data.get("user")
    assert response.status_code == 200


async def test_get_tweets_user_is_not_register(ac: AsyncClient):
    response = await ac.get("/api/tweets", headers={"api-key": "notRegisterUser"})
    data = response.json()
    assert not data.get("result")
    assert response.status_code == 404


async def test_get_user_by_id(ac: AsyncClient):
    response = await ac.get("/api/users/1", headers={"api-key": "test"})
    data = response.json()
    assert data.get("result"), data.get("user")
    assert response.status_code == 200


async def test_get_user_by_id_not_exists(ac: AsyncClient):
    response = await ac.get("/api/users/100", headers={"api-key": "test"})
    data = response.json()
    assert not data.get("result"), not data.get("user")
    assert response.status_code == 404


async def test_user_add_followed(ac: AsyncClient):
    response = await ac.post("/api/users/4/follow", headers={"api-key": "test"})
    data = response.json()
    assert data.get("result")
    assert response.status_code == 201


async def test_user_add_followed_twice(ac: AsyncClient):
    response = await ac.post("/api/users/4/follow", headers={"api-key": "test"})
    data = response.json()
    assert not data.get("result")
    assert data.get("detail").get("error_message") == "User has already been added"
    assert response.status_code == 400


async def test_user_remove_followed(ac: AsyncClient):
    response = await ac.delete("/api/users/4/follow", headers={"api-key": "test"})
    data = response.json()
    assert data.get("result")
    assert response.status_code == 200


async def test_user_remove_followed_twice(ac: AsyncClient):
    response = await ac.delete("/api/users/4/follow", headers={"api-key": "test"})
    data = response.json()
    assert not data.get("result")
    assert data.get("detail").get("error_message") == "User has already been deleted"
    assert response.status_code == 400


async def test_user_add_followed_not_exists_user(ac: AsyncClient):
    response = await ac.post("/api/users/100/follow", headers={"api-key": "test"})
    data = response.json()
    assert data.get("detail").get("error_type") == "Not Found"
    assert response.status_code == 404
