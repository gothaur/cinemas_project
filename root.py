from flask import Flask, render_template, request, redirect, flash, session, url_for
from models.models import Users, Movies, Cinemas, MoviesCinemas, Orders
from database.database import connect_


app = Flask(__name__)
app.secret_key = "klucz sekretny"


@app.route("/", methods=['POST', 'GET'])
@app.route("/home", methods=['POST', 'GET'])
def root():
    return render_template("index.html")


@app.route("/cinemas", methods=['POST', 'GET'])
@app.route("/kina", methods=['POST', 'GET'])
def cinemas():
    if request.method == 'GET':
        _cinemas = Cinemas.get_all(connection)
        if "user" in session:
            return render_template('cinemas.html', cinemas=_cinemas, user_id=session['user'])
        else:
            return render_template('cinemas.html', cinemas=_cinemas)
    else:
        name = request.form.get('name')
        address = request.form.get('address')
        sits = request.form.get('sits')
        if name != "" and address != "" and sits != "":
            cinema = Cinemas(None, name, address, sits)
            cinema.add_to_database(connection)
        else:
            flash("Wszystkie pola muszą być uzupełnione")
        return redirect(url_for('cinemas'))


@app.route("/cinema/<int:cinema_id>", methods=["POST", "GET"])
@app.route("/kino/<int:cinema_id>", methods=["POST", "GET"])
def cinema(cinema_id):
    if request.method == "GET":
        _movies = Movies.get_all(connection, cinema_id=cinema_id)
        _list_of_movies = Movies.get_all(connection)
        if "user" in session:
            return render_template("in_cinema.html", movies=_movies, list_of_movies=_list_of_movies,
                                   user_id=session['user'])
        else:
            return render_template("in_cinema.html", movies=_movies)
    else:
        _cinema_id = cinema_id
        _movie_id = request.form.get('movie_id')
        _date = request.form.get("datetime")
        movie_cinema = MoviesCinemas(None, _movie_id, _cinema_id, _date)
        movie_cinema.add(connection)
        return redirect(f"/cinema/{cinema_id}")


@app.route("/movies", methods=['POST', 'GET'])
@app.route("/filmy", methods=['POST', 'GET'])
def movies():
    if request.method == "GET":
        _movies = Movies.get_all(connection)
        if "user" in session:
            return render_template("movies.html", movies=_movies, user_id=session['user'])
        else:
            return render_template("movies.html", movies=_movies)
    else:
        name = request.form.get("name")
        description = request.form.get("description")
        rate = request.form.get("rate")
        movie = Movies(None, name, description, rate)
        movie.add_to_database(connection)
        return redirect(url_for("movies"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        email = request.form.get("email")
        password = request.form.get("password")
        button = request.form.get("button_name")
        if button == "login":
            if Users.validate(connection, email, password):
                user = Users.get_user_by_email(connection, email)
                session["user"] = user.get_user_id()
                flash("Zalogowano poprawnie")
                return redirect("/")
            else:
                flash("Błędny login lub hasło")
                return redirect(url_for('login'))
        if button == "register":
            user = Users(None, email, password)
            user.add_to_database(connection)
            flash("Zarejestrowano poprawnie. Zaloguj się aby kontynuować")
            return redirect(url_for("login"))


@app.route("/logout", methods=['POST', 'GET'])
def logout():
    if request.method == 'GET':
        if "user" in session:
            session.pop("user", None)
        return render_template("index.html")


if __name__ == '__main__':
    connection = connect_('postgres', 'coderslab', 'localhost', 'cinemas_project')
    app.run(debug=True)
    connection.close()
