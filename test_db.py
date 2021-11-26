import psycopg2

# Connect to your postgres DB
conn = psycopg2.connect(dbname="pgDB", user="postgres", password="@dm1nP@ssw0rd", host="localhost", port="5432")
print("Opened DB")
# Open a cursor to perform database operations
cur = conn.cursor()

# cur.execute("INSERT INTO users (email) VALUES ('tangkoona@gmail.com' )");
# cur.execute("DELETE from users where email='tangkoona@gmail.com';")

# conn.commit()

# Execute a query
cur.execute("SELECT * FROM users")

# Retrieve query results
records = cur.fetchall()

print(records)
