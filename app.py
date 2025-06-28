import uvicorn
import os
from pathlib import Path
from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.responses import JSONResponse

from utils.file_utils import is_allowed_file, MAX_FILE_SIZE, ALLOWED_EXTENSIONS, is_file_size, get_unique_filename

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/images", StaticFiles(directory="images"), name="images")
templates = Jinja2Templates(directory="templates")
IMAGE_DIR = Path("images")
IMAGE_DIR.mkdir(exist_ok=True)

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """ Стартовая страница """
    context = {"request": request}
    return templates.TemplateResponse("index.html", {"request": context})


@app.get("/upload/", response_class=HTMLResponse)
async def get_upload(request: Request):
    """ Страница Upload get запрос """
    context = {"request": request}
    return templates.TemplateResponse("upload.html", {"request": context})

@app.post("/upload/")
async def post_upload(file: UploadFile = File(...)):
    """Загрузка изображения"""

    my_file = Path(file.filename)
    content = await file.read()

    # Проверка файла на расширение
    if not is_allowed_file(my_file):
        raise HTTPException(
            status_code=400,
            detail=f"Неверное расширение файла. Допустимы: {' '.join(ALLOWED_EXTENSIONS)}"
        )

    # Проверка размера файла
    if not is_file_size(file.size):
        raise HTTPException(
            status_code=400,
            detail=f"Размер файла превышает {MAX_FILE_SIZE / (1024 * 1024)} МБ"
        )

    # Генерация уникального имени и сохранение
    new_file_name = get_unique_filename(my_file)
    image_dir = Path("images")
    image_dir.mkdir(exist_ok=True)  # Создаём папку, если её нет
    save_path = image_dir / new_file_name

    with open(save_path, "wb") as buffer:
        buffer.write(content)

    # Возвращаем URL или сообщение
    file_url = f"/images/{new_file_name}"
    return JSONResponse({"url": file_url})

@app.get("/images", response_class=HTMLResponse)
async def images_page(request: Request):
    context = {"request": request}
    return templates.TemplateResponse("images.html", {"request": context})

@app.get("/api/images", response_model=list)
async def get_images():
    """Получение списка изображений"""
    images = []
    for file_path in IMAGE_DIR.iterdir():
        if file_path.is_file():
            images.append({
                "id": file_path.stem,
                "name": file_path.name,
                "url": f"/images/{file_path.name}"
            })
    return images

# Эндпоинт для удаления изображения
@app.delete("/api/images/{image_id}")
async def delete_image(image_id: str):
    """Удаление изображения по ID"""
    file_path = IMAGE_DIR / f"{image_id}.png"  # Пример расширения .png
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Image not found")

    os.remove(file_path)
    return {"message": "Image deleted successfully"}

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
