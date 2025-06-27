import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    # Стартовая страница
    context = {"request": request}
    return templates.TemplateResponse("index.html", {"request": context})


@app.get("/upload/", response_class=HTMLResponse)
async def upload(request: Request):
    # Страница Upload
    context = {"request": request}
    return templates.TemplateResponse("upload.html", {"request": context})


@app.get("/images/", response_class=HTMLResponse)
async def images(request: Request):
    # Страница images
    context = {"request": request}
    return templates.TemplateResponse("images.html", {"request": context})

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
