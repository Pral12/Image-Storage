import uvicorn
from pathlib import Path
from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates

from utils.file_utils import is_allowed_file, MAX_FILE_SIZE, ALLOWED_EXTENSIONS, is_file_size, get_unique_filename

app = FastAPI()
templates = Jinja2Templates(directory="templates")


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
    """ Страница Upload post запрос """

    my_file = Path(file.filename)
    content = await file.read()

    # Проверка файла на размер и расширение
    if not is_allowed_file(my_file):
        raise HTTPException(status_code=400, detail=f"Не верное расширение файла, допустимы {''.join(ALLOWED_EXTENSIONS).replace('.', ' ')}")
    elif not is_file_size(file.size):
        raise HTTPException(status_code=400, detail=f"Размер файла превышает {MAX_FILE_SIZE/1024/1024} МБ")

    # Сохранение файла с новым именем
    new_file_name = get_unique_filename(my_file)
    image_dir = Path("images")
    image_dir.mkdir(exist_ok=True)
    save_path = image_dir / new_file_name
    save_path.write_bytes(content)

    return PlainTextResponse(f"Загрузка {file.filename} прошла успешно")


@app.get("/images/", response_class=HTMLResponse)
async def get_images(request: Request):
    """ Страница images get запрос """
    context = {"request": request}
    return templates.TemplateResponse("images.html", {"request": context})

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
