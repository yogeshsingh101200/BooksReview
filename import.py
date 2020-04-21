""" Imports books.csv to SQL database"""

import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

ENGINE = create_engine(os.getenv("DATABASE_URL"))
DB = scoped_session(sessionmaker(bind=ENGINE))

def main():
    """ Opens csv file and imports it to database"""

    with open("books.csv") as file:
        rows = csv.DictReader(file)
        i = 0
        for row in rows:
            DB.execute("INSERT INTO books VALUES (:isbn, :title, :author, :year)",
                       {"isbn": row["isbn"], "title": row["title"],
                        "author": row["author"], "year": row["year"]})
            i += 1
            print(f"Added {i} books")
        DB.commit()
        print(f"Added {i} books")

if __name__ == "__main__":
    main()
