"""Website portofolio dan blog pribadi berbasis Flask."""

import sqlite3

from flask import Flask, render_template, request

app = Flask(__name__)
DATABASE = "portfolio.db"


def get_db_connection():
    """Membuka koneksi ke database SQLite."""
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def create_tables(cursor):
    """Membuat seluruh tabel aplikasi."""
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            tech_stack TEXT NOT NULL,
            link TEXT
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            author TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_name TEXT NOT NULL,
            sender_email TEXT NOT NULL,
            message_body TEXT NOT NULL,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )


def seed_user(cursor):
    """Membuat akun administrator contoh."""
    cursor.execute(
        """
        INSERT OR IGNORE INTO users (username, password)
        VALUES (?, ?)
        """,
        ("admin", "admin123"),
    )


def seed_projects(cursor):
    """Membuat data project contoh."""
    project_count = cursor.execute(
        "SELECT COUNT(*) FROM projects"
    ).fetchone()[0]

    if project_count > 0:
        return

    projects_data = [
        (
            "Website Toko Sepatu",
            "Website penjualan sepatu berbasis Flask.",
            "Python, Flask, MariaDB, Nginx",
            "#",
        ),
        (
            "Aplikasi Lost and Found",
            "Aplikasi untuk membantu pengguna menemukan barang hilang.",
            "Flutter, REST API, SQLite",
            "#",
        ),
        (
            "DevSecOps Pipeline",
            "Implementasi CI/CD dengan security gate.",
            "GitHub Actions, Semgrep, Pylint, Docker",
            "#",
        ),
    ]

    cursor.executemany(
        """
        INSERT INTO projects (title, description, tech_stack, link)
        VALUES (?, ?, ?, ?)
        """,
        projects_data,
    )


def seed_posts(cursor):
    """Membuat artikel blog contoh."""
    post_count = cursor.execute(
        "SELECT COUNT(*) FROM posts"
    ).fetchone()[0]

    if post_count > 0:
        return

    posts_data = [
        (
            "Mengenal DevSecOps",
            "DevSecOps menggabungkan pengembangan, keamanan, dan operasi.",
            "Admin",
        ),
        (
            "Apa Itu CI/CD?",
            "CI/CD membantu pengujian dan deployment dilakukan otomatis.",
            "Admin",
        ),
    ]

    cursor.executemany(
        """
        INSERT INTO posts (title, content, author)
        VALUES (?, ?, ?)
        """,
        posts_data,
    )


def init_db():
    """Membuat database dan data awal."""
    connection = get_db_connection()
    cursor = connection.cursor()

    create_tables(cursor)
    seed_user(cursor)
    seed_projects(cursor)
    seed_posts(cursor)

    connection.commit()
    connection.close()


def authenticate_user(username, password):
    """Memeriksa username dan password administrator."""
    connection = get_db_connection()

    user = connection.execute(
        """
        SELECT *
        FROM users
        WHERE username = ? AND password = ?
        """,
        (username, password),
    ).fetchone()

    connection.close()

    return user


@app.route("/")
def index():
    """Menampilkan halaman utama."""
    connection = get_db_connection()

    projects = connection.execute(
        """
        SELECT *
        FROM projects
        ORDER BY id DESC
        LIMIT 3
        """
    ).fetchall()

    connection.close()

    return render_template(
        "index.html",
        projects=projects,
    )


@app.route("/projects")
def projects():
    """Menampilkan seluruh project."""
    connection = get_db_connection()

    project_list = connection.execute(
        """
        SELECT *
        FROM projects
        ORDER BY id DESC
        """
    ).fetchall()

    connection.close()

    return render_template(
        "projects.html",
        projects=project_list,
    )


@app.route("/blog")
def blog():
    """Menampilkan daftar artikel."""
    connection = get_db_connection()

    posts = connection.execute(
        """
        SELECT *
        FROM posts
        ORDER BY created_at DESC
        """
    ).fetchall()

    connection.close()

    return render_template(
        "blog.html",
        posts=posts,
    )


@app.route("/blog/<int:post_id>")
def post_detail(post_id):
    """Menampilkan detail artikel."""
    connection = get_db_connection()

    post = connection.execute(
        """
        SELECT *
        FROM posts
        WHERE id = ?
        """,
        (post_id,),
    ).fetchone()

    connection.close()

    if post is None:
        return render_template("404.html"), 404

    return render_template(
        "post_detail.html",
        post=post,
    )


@app.route("/contact", methods=["GET", "POST"])
def contact():
    """Menampilkan dan memproses form kontak."""
    message = None
    status = None

    if request.method == "POST":
        sender_name = request.form.get(
            "sender_name",
            "",
        ).strip()

        sender_email = request.form.get(
            "sender_email",
            "",
        ).strip()

        message_body = request.form.get(
            "message_body",
            "",
        ).strip()

        if not sender_name or not sender_email or not message_body:
            message = "Semua kolom harus diisi."
            status = "danger"
        else:
            connection = get_db_connection()

            connection.execute(
                """
                INSERT INTO messages
                (sender_name, sender_email, message_body)
                VALUES (?, ?, ?)
                """,
                (
                    sender_name,
                    sender_email,
                    message_body,
                ),
            )

            connection.commit()
            connection.close()

            message = "Pesan berhasil dikirim."
            status = "success"

    return render_template(
        "contact.html",
        message=message,
        status=status,
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    """Menampilkan dan memproses login administrator."""
    message = None
    status = None

    if request.method == "POST":
        username = request.form.get(
            "username",
            "",
        ).strip()

        password = request.form.get(
            "password",
            "",
        )

        user = authenticate_user(
            username,
            password,
        )

        if user:
            message = (
                "Login berhasil. Selamat datang, "
                f"{user['username']}!"
            )
            status = "success"
        else:
            message = "Username atau password salah."
            status = "danger"

    return render_template(
        "login.html",
        message=message,
        status=status,
    )


@app.route("/health")
def health():
    """Menyediakan endpoint healthcheck."""
    return {"status": "healthy"}, 200


@app.errorhandler(404)
def page_not_found(_error):
    """Menampilkan halaman 404."""
    return render_template("404.html"), 404


if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=5000)