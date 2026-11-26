import markdown
import bleach
import re

from collections import Counter
from datetime import datetime
from pathlib import Path

from .db import DB
from fastapi import Depends, FastAPI, Form, Request, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from markupsafe import Markup

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "posts_db.db"

app = FastAPI()

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

ALLOWED_TAGS = [
    "p",
    "br",
    "strong",
    "b",
    "em",
    "i",
    "u",
    "s",
    "del",
    "ins",
    "kbd",
    "mark",
    "sub",
    "sup",
    "blockquote",
    "code",
    "pre",
    "h1",
    "h2",
    "h3",
    "h4",
    "ul",
    "ol",
    "li",
    "a",
    "div",
    "span",
]

ALLOWED_ATTRS = {
    "a": ["href", "title", "target"],
    "div": ["align"],
    "p": ["align"],
}

TAG_COLORS = [
    ("#16a34a", "#ffffff"),  # Зелёный (как на твоей картинке)
    ("#2563eb", "#ffffff"),  # Синий
    ("#9333ea", "#ffffff"),  # Фиолетовый
    ("#d97706", "#ffffff"),  # Оранжевый
    ("#db2777", "#ffffff"),  # Розовый
    ("#0d9488", "#ffffff"),  # Бирюзовый
]


def render_markdown(text: str) -> Markup:
    if not text:
        return Markup("")

    # Нативный синтаксис Obsidian для зачёркивания и выделения маркером
    text = re.sub(r"~~(.*?)~~", r"<s>\1</s>", text)
    text = re.sub(r"==(.*?)==", r"<mark>\1</mark>", text)

    raw_html = markdown.markdown(
        text, extensions=["fenced_code", "nl2br", "sane_lists"]
    )
    clean_html = bleach.clean(
        raw_html, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS, strip=True
    )
    return Markup(clean_html)


templates.env.filters["md"] = render_markdown


def tag_color(tag_name: str) -> str:
    idx = sum(ord(ch) for ch in tag_name.lower()) % len(TAG_COLORS)
    bg, _ = TAG_COLORS[idx]
    return bg


templates.env.filters["tag_color"] = tag_color


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
async def posts_index(
    request: Request,
    tag: str | None = None,
    q: str | None = None,
    db: DB = Depends(get_db),
):
    posts = db.get_posts()
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
            "all_tags": db.get_all_tags(),
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


@app.get("/posts/{post_id}", include_in_schema=False)
async def post_page(request: Request, post_id: int, db: DB = Depends(get_db)):
    posts = db.get_posts()
    post = next((p for p in posts if str(p.get("id")) == str(post_id)), None)

    if not post:
        raise HTTPException(status_code=404, detail="Статья не найдена")

    return templates.TemplateResponse(
        request,
        "post_page.html",
        {
            "title": post["title"],
            "post": post,
            "all_tags": db.get_all_tags(),
        },
    )


@app.post("/posts/{post_id}/edit", include_in_schema=False)
async def edit_post(
    post_id: int,
    title: str = Form(...),
    content: str = Form(...),
    tags: str = Form(""),
    db: DB = Depends(get_db),
):
    tags_list = [t.strip() for t in tags.split(",") if t.strip()]
    db.update_post(post_id=post_id, title=title, content=content, tags=tags_list)
    return RedirectResponse(url=f"/posts/{post_id}", status_code=303)


@app.post("/posts/{post_id}/delete", include_in_schema=False)
async def delete_post(post_id: int, db: DB = Depends(get_db)):
    db.delete_post(post_id=post_id)
    return RedirectResponse(url="/posts", status_code=303)


@app.post("/api/preview", include_in_schema=False)
async def preview_markdown(content: str = Form("")):
    return HTMLResponse(content=str(render_markdown(content)))


@app.get("/about", include_in_schema=False)
async def about_index(request: Request):
    return templates.TemplateResponse(request, "about.html", {"title": "About"})


@app.get("/api/posts")
async def get_posts(db: DB = Depends(get_db)):
    return db.get_posts()
