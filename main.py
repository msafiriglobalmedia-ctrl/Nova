from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Generator

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
DB_PATH = Path(os.getenv("DATABASE_PATH", str(BASE_DIR / "data" / "nova.db")))
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title="NOVA Social API",
    description="Early-stage API for the NOVA social application.",
    version="0.1.0",
)


@contextmanager
def get_db() -> Generator[sqlite3.Connection, None, None]:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def initialize_database() -> None:
    with get_db() as db:
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                author TEXT NOT NULL,
                handle TEXT NOT NULL,
                body TEXT NOT NULL,
                created_at TEXT NOT NULL,
                likes INTEGER NOT NULL DEFAULT 0,
                comments INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS post_likes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER NOT NULL,
                user_handle TEXT NOT NULL,
                UNIQUE(post_id, user_handle),
                FOREIGN KEY(post_id) REFERENCES posts(id) ON DELETE CASCADE
            );
            """
        )
        count = db.execute("SELECT COUNT(*) AS total FROM posts").fetchone()["total"]
        if count == 0:
            now = datetime.now(timezone.utc).isoformat()
            seed_posts = [
                (
                    "Rehema Kato",
                    "@rehema",
                    "Small steps every day can build something meaningful. What are you learning this week?",
                    now,
                    18,
                    4,
                ),
                (
                    "Baraka Joseph",
                    "@baraka",
                    "A good community is built when people share knowledge, encourage one another, and create together.",
                    now,
                    12,
                    2,
                ),
            ]
            db.executemany(
                "INSERT INTO posts(author, handle, body, created_at, likes, comments) VALUES (?, ?, ?, ?, ?, ?)",
                seed_posts,
            )


@app.on_event("startup")
def on_startup() -> None:
    initialize_database()


class PostCreate(BaseModel):
    body: str = Field(min_length=1, max_length=2000)
    author: str = Field(default="NOVA Member", min_length=1, max_length=80)
    handle: str = Field(default="@member", min_length=1, max_length=40)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "app": "NOVA Social", "version": app.version}


@app.get("/api/posts")
def list_posts() -> list[dict]:
    with get_db() as db:
        rows = db.execute(
            "SELECT id, author, handle, body, created_at, likes, comments FROM posts ORDER BY id DESC LIMIT 50"
        ).fetchall()
        return [dict(row) for row in rows]


@app.post("/api/posts", status_code=201)
def create_post(payload: PostCreate) -> dict:
    body = payload.body.strip()
    if not body:
        raise HTTPException(status_code=422, detail="Post cannot be empty.")
    created_at = datetime.now(timezone.utc).isoformat()
    with get_db() as db:
        cursor = db.execute(
            "INSERT INTO posts(author, handle, body, created_at) VALUES (?, ?, ?, ?)",
            (payload.author.strip(), payload.handle.strip(), body, created_at),
        )
        post_id = cursor.lastrowid
        row = db.execute(
            "SELECT id, author, handle, body, created_at, likes, comments FROM posts WHERE id = ?",
            (post_id,),
        ).fetchone()
        return dict(row)


@app.post("/api/posts/{post_id}/like")
def like_post(post_id: int) -> dict[str, int]:
    # Prototype behaviour: this endpoint increments a counter. Real accounts and
    # per-user like state will be added with authentication in a later phase.
    with get_db() as db:
        row = db.execute("SELECT id, likes FROM posts WHERE id = ?", (post_id,)).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Post not found.")
        new_likes = row["likes"] + 1
        db.execute("UPDATE posts SET likes = ? WHERE id = ?", (new_likes, post_id))
        return {"post_id": post_id, "likes": new_likes}


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/manifest.json", include_in_schema=False)
def manifest() -> FileResponse:
    return FileResponse(STATIC_DIR / "manifest.json", media_type="application/manifest+json")


@app.get("/sw.js", include_in_schema=False)
def service_worker() -> FileResponse:
    return FileResponse(STATIC_DIR / "sw.js", media_type="application/javascript")


@app.get("/", include_in_schema=False)
def home() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")
