from sqlalchemy import create_engine, URL, text

url = URL.create(
    drivername="mysql+pymysql",
    username="artemisa",
    password="1xMMHfeMUBJGTRcVHE",
    host="localhost",
    database="artemisa",
)

engine = create_engine(url)

with engine.connect() as conn:
    result = conn.execute(text("SELECT DATABASE(), CURRENT_USER()"))
    print(result.fetchone())