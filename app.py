import os
from datetime import datetime
from flask import Flask, flash, redirect, render_template, request, url_for
from data_models import Author, Book, db

app = Flask(__name__)

BASEDIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"sqlite:///{os.path.join(BASEDIR, 'data/library.sqlite')}"
)
app.config['SECRET_KEY'] = os.urandom(24)

db.init_app(app)


@app.route('/')
def home():
    """Startseite mit Buchliste, Sortierung und Suche."""
    sort_by = request.args.get('sort_by', 'title')
    search_query = request.args.get('q', '').strip()

    query = Book.query

    if search_query:
        query = query.filter(Book.title.ilike(f"%{search_query}%"))

    if sort_by == 'author':
        books = query.join(Author).order_by(Author.name.asc()).all()
    else:
        books = query.order_by(Book.title.asc()).all()

    return render_template(
        'home.html',
        books=books,
        current_sort=sort_by,
        search_query=search_query,
    )


@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    """Formular und Verarbeitungs-Route zum Hinzufügen von Autoren."""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        birthdate_str = request.form.get('birthdate')
        date_of_death_str = request.form.get('date_of_death')

        try:
            birth_date = (
                datetime.strptime(birthdate_str, '%Y-%m-%d').date()
                if birthdate_str
                else None
            )
            date_of_death = (
                datetime.strptime(date_of_death_str, '%Y-%m-%d').date()
                if date_of_death_str
                else None
            )
        except ValueError:
            flash("Ungültiges Datumsformat eingegeben.", "error")
            return redirect(url_for('add_author'))

        new_author = Author(
            name=name, birth_date=birth_date, date_of_death=date_of_death
        )
        db.session.add(new_author)
        db.session.commit()

        flash("Autor erfolgreich hinzugefügt!", "success")
        return redirect(url_for('add_author'))

    return render_template('add_author.html')


@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    """Formular und Verarbeitungs-Route zum Hinzufügen von Büchern."""
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        isbn = request.form.get('isbn', '').strip()
        publication_year = request.form.get('publication_year')
        author_id = request.form.get('author_id')

        pub_year = int(publication_year) if publication_year else None

        new_book = Book(
            title=title,
            isbn=isbn,
            publication_year=pub_year,
            author_id=int(author_id),
        )
        db.session.add(new_book)
        db.session.commit()

        flash("Buch erfolgreich hinzugefügt!", "success")
        return redirect(url_for('add_book'))

    authors = Author.query.all()
    return render_template('add_book.html', authors=authors)


@app.route('/book/<int:book_id>/delete', methods=['POST'])
def delete_book(book_id: int):
    """Löscht ein Buch und entfernt verwaiste Autoren automatisch."""
    book = Book.query.get_or_404(book_id)
    author = book.author
    book_title = book.title

    db.session.delete(book)
    db.session.commit()

    if not author.books:
        author_name = author.name
        db.session.delete(author)
        db.session.commit()
        flash(
            f"Das Buch '{book_title}' und der Autor '{author_name}' wurden gelöscht.",
            "success",
        )
    else:
        flash(f"Das Buch '{book_title}' wurde gelöscht.", "success")

    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True, port=5001)