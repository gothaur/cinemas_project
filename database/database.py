from psycopg2 import connect, OperationalError


def connect_(username, password, host, database):
    try:
        connection = connect(user=username, password=password, host=host, database=database)
    except OperationalError as e:
        print(f"Błąd połączenia: {e}")
    else:
        connection.autocommit = True
        return connection
