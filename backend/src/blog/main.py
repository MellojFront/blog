from collections import Counter
from datetime import datetime
from pathlib import Path

from .db import DB
from fastapi import Depends, FastAPI, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "posts_db.db"

app = FastAPI()

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


def get_db():
    with DB(str(DB_PATH)) as db:
        yield db


@app.get("/", include_in_schema=False)
async def home_index(request: Request, db: DB = Depends(get_db)):
    post = db.get_posts()
    return templates.TemplateResponse(
        request, "index.html", {"title": "Home", "latest_post": post[:2]}
    )


@app.get("/posts", include_in_schema=False)
async def posts_index(request: Request, tag: str | None = None, q: str | None = None, db: DB = Depends(get_db)):
    posts =db.get_posts()
    tag_counts = dict(
        sorted(Counter(t for post in posts for t in post.get("tag", [])).items())
    )

    filter_posts = posts
    if tag:
        filter_posts = [p for p in filter_posts if tag in p.get("tag", [])]
    if q:
        q_lower = q.lower()
        filter_posts = [
            p
            for p in filter_posts
            if q_lower in p["title"].lower() or q_lower in p["content"].lower()
        ]
    return templates.TemplateResponse(
        request,
        "posts.html",
        {
            "title": "Посты",
            "posts": filter_posts,
            "tags": tag_counts,
            "search_query": q,
        },
    )


@app.post("/posts", include_in_schema=False)
async def create_post(
    title: str = Form(...),
    content: str = Form(...),
    tags: str = Form(""),
    db: DB = Depends(get_db),
):
    tags_list = [t.strip() for t in tags.split(",") if t.strip()]
    date_str = datetime.now().strftime("%B %d, %Y")

    db.add_post(title=title, content=content, data_posted=date_str, tags=tags_list)
    return RedirectResponse(url="/posts", status_code=303)


@app.get("/about", include_in_schema=False)
async def about_index(request: Request):
    return templates.TemplateResponse(request, "about.html", {"title": "About"})


@app.get("/api/posts")
async def get_posts(db: DB = Depends(get_db)):
    return db.get_posts()
