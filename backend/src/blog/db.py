import sqlite3

__ERROR_DB = "Соединение не открыто. Используйте 'with DB() as db:"


class DB:
    def __init__(self, name: str = "default_db.db"):
        self.name = name
        self.con = None

    def __enter__(self):
        self.con = sqlite3.connect(self.name, check_same_thread=False)
        self.con.row_factory = sqlite3.Row
        self.con.execute("PRAGMA foreign_keys = ON;")
        return self

    def __exit__(self, exc_type, exc, tb):
        if self.con:
            if exc_type is None:
                self.con.commit()
            else:
                self.con.rollback()
            self.con.close()

    def init_db(self):
        if self.con is None:
            raise RuntimeError(__ERROR_DB)
        self.con.executescript("""
                CREATE TABLE IF NOT EXISTS posts(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                data_posted TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
                );

                CREATE TABLE IF NOT EXISTS post_tags(
                post_id INTEGER NOT NULL,
                tag_id INTEGER NOT NULL,
                PRIMARY KEY (post_id, tag_id),
                FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
                FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
                );
""")

    def add_post(self, title: str, content: str, data_posted, tags: list[str]) -> int:
        if self.con is None:
            raise RuntimeError(__ERROR_DB)
        cur = self.con.execute(
            "INSERT INTO posts (title, content, data_posted) VALUES (?, ?, ?)",
            (title, content, data_posted),
        )
        post_id = cur.lastrowid
        assert post_id is not None

        clean_tags = {tag.strip().lower() for tag in tags if tag.strip()}
        for tag in clean_tags:
            self.con.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (tag,))
            tag_row = self.con.execute(
                "SELECT id FROM tags WHERE name = ?", (tag,)
            ).fetchone()
            self.con.execute(
                "INSERT INTO post_tags (post_id, tag_id) VALUES (?, ?)",
                (post_id, tag_row["id"]),
            )
        return post_id

    def get_all_tags(self) -> list[str]:
        if self.con is None:
            raise RuntimeError(__ERROR_DB)
        rows = self.con.execute("SELECT name FROM tags ORDER BY name").fetchall()
        return [row["name"] for row in rows]

    def get_posts_with_tags(self) -> list[dict]:
        if self.con is None:
            raise RuntimeError(__ERROR_DB)
        # GROUP_CONCAT собирает все теги поста в одну строку через запятую
        rows = self.con.execute("""
                SELECT 
                    p.id, 
                    p.title, 
                    p.content, 
                    p.data_posted,
                    GROUP_CONCAT(t.name, ', ') AS tags
                FROM posts p
                LEFT JOIN post_tags pt ON p.id = pt.post_id
                LEFT JOIN tags t ON pt.tag_id = t.id
                GROUP BY p.id
                ORDER BY p.id DESC
            """).fetchall()
        return [dict(row) for row in rows]

    def get_posts(self) -> list[dict]:
        if self.con is None:
            raise RuntimeError(__ERROR_DB)

        rows = self.con.execute("""
                SELECT 
                    p.id, 
                    p.title, 
                    p.content, 
                    p.data_posted,
                    GROUP_CONCAT(t.name, ',') AS raw_tags
                FROM posts p
                LEFT JOIN post_tags pt ON p.id = pt.post_id
                LEFT JOIN tags t ON pt.tag_id = t.id
                GROUP BY p.id
                ORDER BY p.id DESC
            """).fetchall()

        result = []
        for row in rows:
            tags_list = row["raw_tags"].split(",") if row["raw_tags"] else []
            result.append(
                {
                    "id": row["id"],
                    "author": "melloj",
                    "title": row["title"],
                    "content": row["content"],
                    "tag": tags_list,
                    "date_posted": row["data_posted"],
                }
            )
        return result

    def update_post(self, post_id: int, title: str, content: str, tags: list[str]) -> None:
        if self.con is None:
            raise RuntimeError(__ERROR_DB)

        self.con.execute(
            "UPDATE posts SET title = ?, content = ? WHERE id = ?",
            (title, content, post_id),
        )

        self.con.execute("DELETE FROM post_tags WHERE post_id = ?", (post_id,))

        clean_tags = {tag.strip().lower() for tag in tags if tag.strip()}
        for tag in clean_tags:
            self.con.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (tag,))
            tag_row = self.con.execute(
                "SELECT id FROM tags WHERE name = ?", (tag,)
            ).fetchone()
            self.con.execute(
                "INSERT INTO post_tags (post_id, tag_id) VALUES (?, ?)",
                (post_id, tag_row["id"]),
            )
        self.con.execute("DELETE FROM tags WHERE id NOT IN (SELECT DISTINCT tag_id FROM post_tags)")


    def delete_post(self, post_id: int) -> None:
        if self.con is None:
            raise RuntimeError(__ERROR_DB)
        self.con.execute("DELETE FROM posts WHERE id = ?", (post_id,))
        self.con.execute("DELETE FROM tags WHERE id NOT IN (SELECT DISTINCT tag_id FROM post_tags)")

