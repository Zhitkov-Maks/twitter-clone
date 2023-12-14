from pathlib import Path

from httpx import AsyncClient

OUT_PATH = Path(__file__).parent / "files_for_tests"
OUT_PATH.mkdir(exist_ok=True, parents=True)
OUT_PATH = OUT_PATH.absolute()


async def test_upload_image(ac: AsyncClient):
    """Test for saving an image with valid data"""
    response = await ac.post(
        "/api/medias",
        headers={"api-key": "test"},
        files={
            "file": (
                "1629370050_m6.jpg",
                open(f"{OUT_PATH}/1629370050_m6.jpg", "rb"),
                "image/jpg",
            )
        },
    )
    data = response.json()
    assert response.status_code == 201
    assert data.get("result")
    assert isinstance(data.get("media_id"), int)


async def test_upload_invalid_file(ac: AsyncClient):
    """Test for saving an image with PDF file"""
    response = await ac.post(
        "/api/medias",
        headers={"api-key": "test"},
        files={
            "file": (
                "test_file_pdf.txt",
                open(f"{OUT_PATH}/test_file_pdf.txt", "rb"),
                "application/txt",
            )
        },
    )
    data = response.json()
    assert response.status_code == 415
    assert not data.get("result")


async def test_upload_unsupported_format(ac: AsyncClient):
    """Test for saving an image with an image of an unsupported type"""
    response = await ac.post(
        "/api/medias",
        headers={"api-key": "test"},
        files={
            "file": (
                "images.gif",
                open(f"{OUT_PATH}/images.gif", "rb"),
                "images/webp",
            )
        },
    )
    data = response.json()
    assert response.status_code == 415
    assert not data.get("result")
