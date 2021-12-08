import psycopg2
from io import BytesIO
from PIL import Image

# Connect to your postgres DB
conn = psycopg2.connect(dbname="pgDB", user="postgres", password="1133557799", host="localhost", port="5432")
print("Opened DB")
# Open a cursor to perform database operations
cur = conn.cursor()

# cur.execute("INSERT INTO users (email) VALUES ('tangkoona@gmail.com' )");
# cur.execute("DELETE from users where email='tangkoona@gmail.com';")

# conn.commit()

# Execute a query
cur.execute("SELECT * FROM slides")

records = cur.fetchall()
img = BytesIO(records[0][3])
image = Image.open(img)
image.show()

cur.close()
conn.close()
