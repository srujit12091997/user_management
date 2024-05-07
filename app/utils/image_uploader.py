from fastapi import UploadFile
from minio import Minio
from minio.error import S3Error
import os
from uuid import UUID
from settings.config import settings
from PIL import Image

# Ensure these settings are correctly configured in your settings.config module
# Example:
# MINIO_ENDPOINT = 'localhost:9000'
# MINIO_ACCESS_KEY = 'admin'  # Change as per your configuration
# MINIO_SECRET_KEY = 'YourPassword'  # Change as per your configuration
# MINIO_BUCKET_NAME = 'test'  # Make sure this is the name of your Minio bucket

minio_client = Minio(
    settings.MINIO_ENDPOINT,
    access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_SECRET_KEY,
    secure=False  # Set to True if you enable SSL/TLS
)


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB limit

async def upload(file: UploadFile, user_id: UUID) -> str:
    try:
        # Validate file size and extension
        if not allowed_file(file) or file.spool(MAX_FILE_SIZE):
            raise ValueError("Invalid file")

        file_path = f"/tmp/{file.filename}"
        size = (200, 200)  # Resize dimensions

        # Save the uploaded file temporarily
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        # Resize image and get the new path
        resized_image_path = resize_image(file_path, size, user_id)

        image_name = f"{str(user_id)}.{file.filename.split('.')[1]}"
        # Upload the file to Minio
        minio_client.fput_object(settings.MINIO_BUCKET_NAME, image_name, resized_image_path)

        # Clean up temporary files
        os.remove(file_path)
        os.remove(resized_image_path)


        # Return the URL to access the file
        return f"http://{settings.MINIO_ENDPOINT}/{settings.MINIO_BUCKET_NAME}/{image_name}"
    except S3Error as exc:
        print("Error occurred:", exc)
        return None

def allowed_file(file: UploadFile):
    filename = file.filename
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def resize_image(image_path, size, user_id):
    with Image.open(image_path) as img:
        resized_img = img.resize(size, Image.Resampling.LANCZOS)
        output_path = f"/tmp/{str(user_id)}.{image_path.split('.')[-1]}"
        resized_img.save(output_path)
        return output_path
