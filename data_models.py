from datetime import date
from typing import Optional
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Author(db.Model):
    """Repräsentiert einen Autor in der Datenbank."""

    __tablename__ = 'authors'

    id: int = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name: str = db.Column(db.String(100), nullable=False)
    birth_date: Optional[date] = db.Column(db.Date, nullable=True)
    date_of_death: Optional[date] = db.Column(db.Date, nullable=True)

    books = db.relationship('Book', backref='author', lazy=True)

    def __str__(self) -> str:
        return f"{self.name}"

    def __repr__(self) -> str:
        return f"<Author {self.id}: {self.name}>"


class Book(db.Model):
    """Repräsentiert ein Buch in der Datenbank."""

    __tablename__ = 'books'

    id: int = db.Column(db.Integer, primary_key=True, autoincrement=True)
    isbn: str = db.Column(db.String(13), unique=True, nullable=False)
    title: str = db.Column(db.String(200), nullable=False)
    publication_year: Optional[int] = db.Column(db.Integer, nullable=True)
    author_id: int = db.Column(
        db.Integer, db.ForeignKey('authors.id'), nullable=False
    )

    def __str__(self) -> str:
        return f"'{self.title}' (ISBN: {self.isbn})"

    def __repr__(self) -> str:
        return f"<Book {self.id}: {self.title}>"