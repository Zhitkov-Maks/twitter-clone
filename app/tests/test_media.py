from pathlib import Path

from httpx import AsyncClient

OUT_PATH = Path(__file__).parent / 'files_for_tests'
OUT_PATH.mkdir(exist_ok=True, parents=True)
OUT_PATH = OUT_PATH.absolute()


async def test_upload_image(ac: AsyncClient):
    response = await ac.post(
        "/api/medias",
        headers={
            "api-key": "test"
        },
        files={
            "file": (
                "1629370050_m6.jpg",
                open(f"{OUT_PATH}/1629370050_m6.jpg", "rb"),
                "image/jpg"
            )
        }
    )
    data = response.json()
    assert response.status_code == 201
    assert data.get('result')
    assert isinstance(data.get('media_id'), int)


async def test_upload_invalid_file(ac: AsyncClient):
    response = await ac.post(
        "/api/medias",
        headers={
            "api-key": "test"
        },
        files={
            "file":
                (
                    "test_file_pdf.txt",
                    open(f"{OUT_PATH}/test_file_pdf.txt", "rb"),
                    "application/txt"
                )
        }
    )
    data = response.json()
    assert response.status_code == 415
    assert not data.get("result")


async def test_upload_unsupported_format(ac: AsyncClient):
    response = await ac.post(
        "/api/medias",
        headers={
            "api-key": "test"
        },
        files={
            "file":
                ("images.webp",
                 open(f"{OUT_PATH}/images.webp", "rb"),
                 "images/webp")
        }
    )
    data = response.json()
    assert response.status_code == 415
    assert not data.get("result")
