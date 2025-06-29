import uvicorn
import os
from pathlib import Path
from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.responses import JSONResponse

from utils.file_utils import is_allowed_file, MAX_FILE_SIZE, ALLOWED_EXTENSIONS, is_file_size, get_unique_filename, THUMBNAIL_SIZE, create_thumbnail

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/images", StaticFiles(directory="images"), name="images")
app.mount("/templates", StaticFiles(directory="templates"), name="templates")
app.mount("/thumbnails", StaticFiles(directory="thumbnails"), name="thumbnails")
templates = Jinja2Templates(directory="templates")
IMAGE_DIR = Path("images")
IMAGE_DIR.mkdir(exist_ok=True)
THUMBNAIL_DIR = Path("thumbnails")
THUMBNAIL_DIR.mkdir(exist_ok=True)
TEMPLATES_DIR = Path("templates")
TEMPLATES_DIR.mkdir(exist_ok=True)

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
    my_file = Path(file.filename)
    content = await file.read()

    # Проверка расширения
    if not is_allowed_file(my_file):
        raise HTTPException(
            status_code=400,
            detail=f"Неверное расширение файла. Допустимы: {' '.join(ALLOWED_EXTENSIONS)}"
        )

    # Проверка размера
    if not is_file_size(file.size):
        raise HTTPException(
            status_code=400,
            detail=f"Размер файла превышает {MAX_FILE_SIZE / (1024 * 1024)} МБ"
        )

    # Генерация уникального имени и сохранение
    new_file_name = get_unique_filename(my_file)
    save_path = IMAGE_DIR / new_file_name
    with open(save_path, "wb") as buffer:
        buffer.write(content)

    # Создание миниатюры
    thumbnail_path = THUMBNAIL_DIR / new_file_name
    create_thumbnail(save_path, thumbnail_path)

    # Возвращаем URL
    file_url = f"/images/{new_file_name}"
    return JSONResponse({"url": file_url})

@app.get("/images", response_class=HTMLResponse)
async def images_page(request: Request):
    context = {"request": request}
    return templates.TemplateResponse("images.html", {"request": context})

# Эндпоинт для получения списка изображений
@app.get("/api/images")
async def get_images():
    image_files = []
    for file in IMAGE_DIR.iterdir():
        if file.is_file():
            thumbnail_url = f"/thumbnails/{file.name}"
            image_files.append({
                "id": file.stem,
                "name": file.name,
                "url": f"/images/{file.name}",
                "thumbnail_url": thumbnail_url
            })
    return image_files

# Эндпоинт для удаления изображения
@app.delete("/api/images/{image_id}")
async def delete_image(image_id: str):
    for ext in [".jpg", ".jpeg", ".png", ".gif"]:
        file_path = IMAGE_DIR / f"{image_id}{ext}"
        thumbnail_path = THUMBNAIL_DIR / f"{image_id}{ext}"
        if file_path.exists():
            os.remove(file_path)
            if thumbnail_path.exists():
                os.remove(thumbnail_path)
            return {"message": "Image deleted successfully"}

    raise HTTPException(status_code=404, detail="Image not found")

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
