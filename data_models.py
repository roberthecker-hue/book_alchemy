from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Author(db.Model):
    __tablename__ = 'authors'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(db.Date, nullable=True)
    date_of_death = db.Column(db.Date, nullable=True)

    # Ermöglicht book.author.name und author.books
    books = db.relationship('Book', backref='author', lazy=True)

    def __str__(self):
        return f"{self.name}"

    def __repr__(self):
        return f"<Author {self.id}: {self.name}>"


class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    isbn = db.Column(db.String(13), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    publication_year = db.Column(db.Integer, nullable=True)

    # Fremdschlüssel auf die Spalte 'id' in der Tabelle 'authors'
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'), nullable=False)

    def __str__(self):
        return f"'{self.title}' (ISBN: {self.isbn})"

    def __repr__(self):
        return f"<Book {self.id}: {self.title}>"