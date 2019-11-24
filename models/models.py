from clcrypto import check_password, password_hash
from psycopg2 import connect, OperationalError


class Movies:

    def __init__(self, movie_id, title, description, rate):
        self._movie_id = movie_id
        self.title = title
        self.description = description
        self.rate = rate

    def get_movie_id(self):
        return self._movie_id

    def set_movie_id(self, movie_id):
        self._movie_id = movie_id

    def add_to_database(self, database_connection):
        cursor = database_connection.cursor()
        cursor.execute("INSERT INTO Movies(title, description, rate) VALUES(%s, %s, %s) "
                       "RETURNING movie_id;", [self.title, self.description, self.rate])
        self.set_movie_id(cursor.fetchone()[0])
        cursor.close()

    @staticmethod
    def delete(database_connection, movie_id):
        cursor = database_connection.cursor()
        cursor.execute("DELETE FROM Movies WHERE movie_id=%s;", [movie_id])
        cursor.close()

    # @staticmethod
    # def get_all(database_connection, cinema_id=None):
    #     cursor = database_connection.cursor()
    #     cursor.execute("SELECT movie_id, title, description, rate FROM Movies")
    #     movies = []
    #     movies_data = cursor.fetchall()
    #     for movie_data in movies_data:
    #         movie = Movies(movie_data[0], movie_data[1], movie_data[2], movie_data[3])
    #         movies.append(movie)
    #     cursor.close()
    #
    #     return movies

    @staticmethod
    def get_all(database_connection, cinema_id=None):
        cursor = database_connection.cursor()
        if cinema_id:
            sql = "SELECT Movies.movie_id, Movies.title, Cinemas.sits, Movies_Cinemas.date " \
                  "FROM Movies " \
                  "JOIN Movies_Cinemas ON Movies_Cinemas.movie_id=Movies.movie_id " \
                  "JOIN Cinemas ON Movies_Cinemas.cinema_id=Cinemas.cinema_id " \
                  "WHERE Cinemas.cinema_id = %s"
        else:
            sql = "SELECT movie_id, title, description, rate FROM Movies"
        cursor.execute(sql, [cinema_id])
        movies = []
        movies_data = cursor.fetchall()
        for movie_data in movies_data:
            movie = Movies(movie_data[0], movie_data[1], movie_data[2], movie_data[3])
            movies.append(movie)
        cursor.close()

        return movies

    @staticmethod
    def search_by_title(database_connection, title):
        cursor = database_connection.cursor()
        title = '%' + title + '%'
        cursor.execute("SELECT movie_id, title, description, rate FROM Movies "
                       "WHERE title LIKE %s", [title])
        movies = []
        movies_data = cursor.fetchall()
        for movie_data in movies_data:
            movie = Movies(movie_data[0], movie_data[1], movie_data[2], movie_data[3])
            movies.append(movie)
        cursor.close()
        if len(movies) > 0:
            return movies


class Cinemas:

    def __init__(self, cinema_id, name, address, sits):
        self._cinema_id = cinema_id
        self.name = name
        self.address = address
        self.sits = sits

    def get_cinema_id(self):
        return self._cinema_id

    def set_cinema_id(self, cinema_id):
        self._cinema_id = cinema_id

    def add_to_database(self, database_connection):
        cursor = database_connection.cursor()
        cursor.execute("INSERT INTO Cinemas(name, address, sits) VALUES (%s, %s, %s) RETURNING cinema_id",
                       [self.name, self.address, self.sits])
        self.set_cinema_id(cursor.fetchone()[0])
        cursor.close()

    @staticmethod
    def get_all(database_connection):
        cursor = database_connection.cursor()
        cursor.execute("SELECT cinema_id, name, address, sits FROM Cinemas")
        cinemas = []
        cinemas_data = cursor.fetchall()
        for cinema_data in cinemas_data:
            cinema = Cinemas(cinema_data[0], cinema_data[1], cinema_data[2], cinema_data[3],)
            cinemas.append(cinema)
        return cinemas

    @staticmethod
    def search_by_name(database_connection, name):
        cursor = database_connection.cursor()
        name = '%' + name + '%'
        cursor.execute("SELECT cinema_id, name, address, sits FROM Cinemas "
                       "WHERE name LIKE %s", [name])
        cinemas = []
        cinemas_data = cursor.fetchall()
        for cinema_data in cinemas_data:
            cinema = Cinemas(cinema_data[0], cinema_data[1], cinema_data[2], cinema_data[3])
            cinemas.append(cinema)
        cursor.close()
        if len(cinemas) > 0:
            return cinemas


class MoviesCinemas:

    def __init__(self, pic_id, movie_id, cinema_id, date):
        self._pic_id = pic_id
        self.movie_id = movie_id
        self.cinema_id = cinema_id
        self.date = date

    def add(self, database_connection):
        cursor = database_connection.cursor()
        cursor.execute("INSERT INTO Movies_Cinemas(movie_id, cinema_id, date) VALUES (%s, %s, %s)"
                       "RETURNING pic_id", [self.movie_id, self.cinema_id, self.date])
        self._pic_id = cursor.fetchone()[0]
        cursor.close()


class Users:
    """
    superuser: email: admin password: admin
    """

    def __init__(self, user_id, email, password):
        self._user_id = user_id
        self.email = email
        self.password = password

    def get_user_id(self):
        return self._user_id

    def set_user_id(self, user_id):
        self._user_id = user_id

    def add_to_database(self, database_connection):
        cursor = database_connection.cursor()
        self.password = password_hash(self.password)
        cursor.execute("INSERT INTO Users(email, password) VALUES (%s, %s) RETURNING user_id;",
                       [self.email, self.password])
        self.set_user_id(cursor.fetchone()[0])
        cursor.close()

    @staticmethod
    def get_user_by_email(database_connection, email):
        cursor = database_connection.cursor()
        cursor.execute("SELECT user_id, email, password FROM Users WHERE email=%s", [email])
        user = None
        if cursor.rowcount > 0:
            user_data = cursor.fetchone()
            user = Users(user_data[0], user_data[1], user_data[2])
        cursor.close()
        return user

    @staticmethod
    def validate(database_connection, email, password):
        cursor = database_connection.cursor()
        cursor.execute("SELECT password FROM Users WHERE email=%s;", [email])
        result = False
        if cursor.rowcount > 0:
            hashed_password = cursor.fetchone()[0]
            result = check_password(password, hashed_password)
        cursor.close()
        return result


class Orders:

    def __init__(self, user_id, pic_id, quantity,	price):
        self._order_id = None
        self.user_id = user_id
        self.pic_id = pic_id
        self.quantity = quantity
        self.price = price


# def db_conn():
#     username = "postgres"
#     passwd = "coderslab"
#     hostname = "127.0.0.1"  # lub "localhost"
#     db_name = "cinemas_project"
#     try:
#         # tworzymy nowe połączenie
#         db_connection = connect(user=username, password=passwd, host=hostname, database=db_name)
#         db_connection.autocommit = True
#         return db_connection
#     except OperationalError as e:
#         print(e)
#
#
# def main():
#     # user = Users(None, 'admin', 'admin')
#     # user.add_to_database(db_conn())
#     user = Users.get_user_by_email(db_conn(), 'admin2')
#     print(user.email)
#
#
# main()
