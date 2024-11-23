from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
from service.file_service import FileService

# Создаем маршрутизатор
router = APIRouter()

# Инициализация FileService
file_service = FileService(upload_directory="uploads")

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Сохраняем файл через сервис
        file_path = file_service.save_file(file)

        return JSONResponse(content={"message": f"Файл {file.filename} успешно загружен!", "path": file_path}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"message": f"Ошибка при загрузке файла: {str(e)}"}, status_code=500)
