import os
from datetime import datetime
from flask import Flask, render_template, request, flash, redirect, url_for  # Flask hier ergänzt

from data_models import db, Author, Book

# Flask-Instanz erstellen
app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data/library.sqlite')}"
app.config['SECRET_KEY'] = 'dein-geheimer-schluessel-hier'  # Wichtig für flash()!

db.init_app(app)

"""
# Wird zum Datenbank anlegen genutzt. Wird nur einmal ausgeführt und dann auskommentiert.
with app.app_context():
    db.create_all()
"""

@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    if request.method == 'POST':
        name = request.form.get('name')
        birthdate_str = request.form.get('birthdate')
        date_of_death_str = request.form.get('date_of_death')

        # Strings in datetime.date Objekte umwandeln (oder None, falls leer)
        birth_date = datetime.strptime(birthdate_str, '%Y-%m-%d').date() if birthdate_str else None
        date_of_death = datetime.strptime(date_of_death_str, '%Y-%m-%d').date() if date_of_death_str else None

        # Neues Author-Objekt erstellen und speichern
        new_author = Author(
            name=name,
            birth_date=birth_date,
            date_of_death=date_of_death
        )
        db.session.add(new_author)
        db.session.commit()

        flash("Autor erfolgreich hinzugefügt!", "success")
        return redirect(url_for('add_author'))

    return render_template('add_author.html')


@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form.get('title')
        isbn = request.form.get('isbn')
        publication_year = request.form.get('publication_year')
        author_id = request.form.get('author_id')

        # Jahreszahl in Integer umwandeln (oder None, falls leer)
        pub_year = int(publication_year) if publication_year else None

        # Neues Book-Objekt erstellen
        new_book = Book(
            title=title,
            isbn=isbn,
            publication_year=pub_year,
            author_id=int(author_id)
        )
        db.session.add(new_book)
        db.session.commit()

        flash("Buch erfolgreich hinzugefügt!", "success")
        return redirect(url_for('add_book'))

    # Bei GET: Alle Autoren aus der DB holen, damit wir sie im Dropdown anzeigen können
    authors = Author.query.all()
    return render_template('add_book.html', authors=authors)


@app.route('/')
def home():
    sort_by = request.args.get('sort_by', 'title')
    search_query = request.args.get('q', '').strip()

    # Grund-Query aufbauen
    query = Book.query

    # Falls ein Suchbegriff eingegeben wurde, nach Titel filtern
    if search_query:
        query = query.filter(Book.title.ilike(f"%{search_query}%"))

    # Sortierung anwenden
    if sort_by == 'author':
        books = query.join(Author).order_by(Author.name.asc()).all()
    else:
        books = query.order_by(Book.title.asc()).all()

    return render_template('home.html', books=books, current_sort=sort_by, search_query=search_query)


@app.route('/book/<int:book_id>/delete', methods=['POST'])
def delete_book(book_id):
    # Buch anhand der ID suchen
    book = Book.query.get_or_404(book_id)
    author = book.author
    book_title = book.title

    # 1. Buch löschen
    db.session.delete(book)
    db.session.commit()

    # 2. Prüfen, ob der Autor noch andere Bücher besitzt
    if not author.books:
        author_name = author.name
        db.session.delete(author)
        db.session.commit()
        flash(f"Das Buch '{book_title}' und der Autor '{author_name}' (keine weiteren Bücher vorhanden) wurden gelöscht.", "success")
    else:
        flash(f"Das Buch '{book_title}' wurde erfolgreich gelöscht.", "success")

    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True, port=5001)