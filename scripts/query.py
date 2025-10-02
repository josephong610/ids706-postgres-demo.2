import os
import psycopg2
from dotenv import load_dotenv

# Load .env if present (does nothing if file not found)
load_dotenv()

DB_NAME = os.getenv("DB_NAME", os.getenv("PGDATABASE", "duke_restaurants"))
DB_USER = os.getenv("DB_USER", os.getenv("PGUSER", "vscode"))
DB_PASSWORD = os.getenv("DB_PASSWORD", os.getenv("PGPASSWORD", "vscode"))
# In devcontainer, host is 'db'; on your laptop use 'localhost'
DB_HOST = os.getenv("DB_HOST", os.getenv("PGHOST", "localhost"))
DB_PORT = os.getenv("DB_PORT", os.getenv("PGPORT", "5432"))

def main():
    print(f"Connecting to {DB_NAME} at {DB_HOST}:{DB_PORT} as {DB_USER} ...")
    conn = psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
    )
    cur = conn.cursor()

    # --- Existing queries ---
    print("\nTop rated places:")
    cur.execute("""
        SELECT name, rating
        FROM restaurants
        ORDER BY rating DESC, name ASC;
    """)
    for row in cur.fetchall():
        print(row)

    print("\nInserting a new restaurant...")
    cur.execute("""
        INSERT INTO restaurants (name, address, distance_miles, rating, cuisine, avg_cost, personal_rank)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id, name;
    """, ("Queeny's", "321 E Chapel Hill St, Durham, NC", 1.5, 4.3, "American", 22.00, 7))
    print("Inserted:", cur.fetchone())

    print("\nUpdating rating for NuvoTaco...")
    cur.execute("""
        UPDATE restaurants
        SET rating = rating + 0.1
        WHERE name = %s
        RETURNING name, rating;
    """, ("NuvoTaco",))
    print("Updated:", cur.fetchone())

    print("\nDeleting lowest-rated place...")
    cur.execute("""
        DELETE FROM restaurants
        WHERE id = (
          SELECT id FROM restaurants
          ORDER BY rating ASC, id ASC
          LIMIT 1
        )
        RETURNING id, name, rating;
    """)
    print("Deleted:", cur.fetchone())

    # --- Added queries ---
    print("\n5 Cheapest Restaurants:")
    cur.execute("""
        SELECT name, cuisine, avg_cost
        FROM restaurants
        ORDER BY avg_cost ASC
        LIMIT 5;
    """)
    for row in cur.fetchall():
        print(row)

    print("\nNearby highly rated (within 5 miles, rating >= 4.0):")
    cur.execute("""
        SELECT name, cuisine, distance_miles, rating
        FROM restaurants
        WHERE distance_miles <= 5 AND rating >= 4.0
        ORDER BY rating DESC, distance_miles ASC;
    """)
    for row in cur.fetchall():
        print(row)

    print("\nRestaurants within 2 miles:")
    cur.execute("""
        SELECT name, distance_miles
        FROM restaurants
        WHERE distance_miles <= 2.0
        ORDER BY distance_miles ASC;
    """)
    for row in cur.fetchall():
        print(row)

    print("\nTop 3 Restaurants by Rating:")
    cur.execute("""
        SELECT name, rating
        FROM restaurants
        ORDER BY rating DESC
        LIMIT 3;
    """)
    for row in cur.fetchall():
        print(row)

    print("\nRestaurants with avg_cost and cost_with_tax:")
    cur.execute("""
        SELECT name, avg_cost, avg_cost * 1.075 AS cost_with_tax
        FROM restaurants;
    """)
    for row in cur.fetchall():
        print(row)

    print("\nNumber of restaurants per cuisine:")
    cur.execute("""
        SELECT cuisine, COUNT(*) AS num_restaurants
        FROM restaurants
        GROUP BY cuisine
        ORDER BY num_restaurants DESC;
    """)
    for row in cur.fetchall():
        print(row)

    # --- End of queries ---

    conn.commit()
    cur.close()
    conn.close()
    print("\nDone.")

if __name__ == "__main__":
    main()
