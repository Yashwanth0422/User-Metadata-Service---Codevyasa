import psycopg2

def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="usersdb",
        user="user",
        password="password"
    )
