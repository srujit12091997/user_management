import os
import pytest
from app.utils.image_uploader import upload, allowed_file, resize_image
from uuid import uuid4
from fastapi import UploadFile
from PIL import Image
from io import BytesIO

from app.dependencies import get_settings
settings = get_settings()


@pytest.fixture
def test_image():
    # Create a test image
    image = Image.new('RGB', (500, 300), color='red')
    image.save('/tmp/test_img.jpg')
    return '/tmp/test_img.jpg'


@pytest.fixture
def test_file():
     image = Image.new('RGB', (500, 300), color='red')
     image.save('/tmp/test_img.jpg')
     return UploadFile(filename="test_img.jpg", file=BytesIO(image.tobytes()))

@pytest.fixture
def test_user_id():
    return uuid4()

def test_allowed_file():
    file_data = b"image_data"
    assert allowed_file(UploadFile(filename="image.png", file=file_data))
    assert allowed_file(UploadFile(filename="image.jpg", file=file_data))
    assert allowed_file(UploadFile(filename="image.jpeg", file=file_data))
    assert not allowed_file(UploadFile(filename="image.txt", file=file_data))
    assert not allowed_file(UploadFile(filename="image.gif", file=file_data))


def test_resize_image(test_image, test_user_id):
    resized_image_path = resize_image(test_image, (200, 200), test_user_id)
    assert os.path.exists(resized_image_path)
    assert resized_image_path == f"/tmp/{str(test_user_id)}.jpg"

    os.remove(test_image)
    os.remove(resized_image_path)