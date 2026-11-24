from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from collections import Counter

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI()

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


posts: list[dict] = [
    {
        "id": 1,
        "autor": "melloj",
        "title": "FastAPI for beginers",
        "content": "This is framework is really easy d to work programming to use musicians and dj producersMethod to work programming to use musicians and dj producersMethod to work programming to use musicians and dj producersMethod to work programming to use musicians and dj producersMethod to work programming to use musicians and dj producersMethod to work programmincians and dj producersMethod to work programming to use musicians and dj producersMethod to work programming to use musiciad to work programming to use musicians and dj producersMethod to work programming to use musicians and dj producersMethod to work programming to use musicians and dj producersMethod to work programming to use musicians and dj producersMethod to work programming to use musicians and dj producersMethod to work programminns and dj producersMethod to work programming to use musicians and dj producersMethod to work programmin",
        "tag": ["API", "Web", "Beginers"],
        "date_posted": "April 20, 2025",
    },
    {
        "id": 2,
        "autor": "melloj",
        "title": "Music in programming",
        "content": "Method to work programming to use musicians and dj producersMethod to work programming to use musicians and dj producersMethod to work programming to use musicians and dj producersMethod to work programming to use musicians and dj producersMethod to work programming to use musicians and dj producersMethod to work programming to use musicians and dj producersMethod to work programming to use musicians and dj producersMethod to work programming to use musicians and dj producersMethod to work programming to use musicians and dj producersMethod to work programming to use musicians and dj producersMethod to work programming to use musicians and dj producers",
        "tag": ["Programming", "Music"],
        "date_posted": "September 20, 2026",
    },
]


@app.get("/", include_in_schema=False)
async def home_index(request: Request):
    return templates.TemplateResponse(request, "index.html", {"title": "Home", "latest_post": posts[:2]})


@app.get("/posts", include_in_schema=False)
async def posts_index(request: Request, tag: str | None = None, q: str | None = None):
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
            "search_query": q
        },
    )


@app.get("/about", include_in_schema=False)
async def about_index(request: Request):
    return templates.TemplateResponse(request, "about.html", {"title": "About"})


@app.get("/api/posts")
async def get_posts():
    return posts
