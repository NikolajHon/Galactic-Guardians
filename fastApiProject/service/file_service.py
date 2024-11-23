import os
import shutil
from fastapi import UploadFile

class FileService:
    def __init__(self, upload_directory: str = "uploads"):
        # Инициализация папки для загрузки
        self.upload_directory = upload_directory
        if not os.path.exists(self.upload_directory):
            os.makedirs(self.upload_directory)

    def save_file(self, file: UploadFile) -> str:
        try:
            # Определяем путь сохранения файла
            file_location = os.path.join(self.upload_directory, file.filename)

            # Сохраняем файл
            with open(file_location, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            return file_location
        except Exception as e:
            raise Exception(f"Ошибка при сохранении файла: {str(e)}")
