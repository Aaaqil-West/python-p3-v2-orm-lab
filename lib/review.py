from __init__ import CURSOR, CONN
from department import Department
from employee import Employee


class Review:

    # Dictionary of objects saved to the database.
    all = {}

    def __init__(self, year, summary, employee_id, id=None):
        self.id = id
        self.year = year
        self.summary = summary
        self.employee_id = employee_id

    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, value):
        if not isinstance(value, int):
            raise ValueError("Year must be an integer")
        if value < 2000:
            raise ValueError("Year must be >= 2000")
        self._year = value

    @property
    def summary(self):
        return self._summary

    @summary.setter
    def summary(self, value):
        if not isinstance(value, str) or len(value) == 0:
            raise ValueError("Summary must be a non-empty string")
        self._summary = value

    @property
    def employee_id(self):
        return self._employee_id

    @employee_id.setter
    def employee_id(self, value):
        # Check if employee_id exists in the employees table
        if not isinstance(value, int):
            raise ValueError("employee_id must be an integer")
        sql = "SELECT id FROM employees WHERE id = ?"
        row = CURSOR.execute(sql, (value,)).fetchone()
        if row is None:
            raise ValueError("employee_id must reference a valid Employee in the database")
        self._employee_id = value

    def __repr__(self):
        return (
            f"<Review {self.id}: {self.year}, {self.summary}, "
            + f"Employee: {self.employee_id}>"
        )

    @classmethod
    def create_table(cls):
        """ Create a new table to persist the attributes of Review instances """
        sql = """
            CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY,
            year INT,
            summary TEXT,
            employee_id INTEGER,
            FOREIGN KEY (employee_id) REFERENCES employee(id))
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        """ Drop the table that persists Review  instances """
        sql = """
            DROP TABLE IF EXISTS reviews;
        """
        CURSOR.execute(sql)
        CONN.commit()

    def save(self):
        """Insert or update the review in the database and update the object's id and all dict."""
        if self.id is None:
            sql = """
                INSERT INTO reviews (year, summary, employee_id)
                VALUES (?, ?, ?)
            """
            CURSOR.execute(sql, (self.year, self.summary, self.employee_id))
            CONN.commit()
            self.id = CURSOR.lastrowid
            type(self).all[self.id] = self
        else:
            self.update()

    @classmethod
    def create(cls, year, summary, employee_id):
        """Initialize a new Review instance and save the object to the database. Return the new instance."""
        review = cls(year, summary, employee_id)
        review.save()
        return review
   
    @classmethod
    def instance_from_db(cls, row):
        """Return a Review instance having the attribute values from the table row."""
        if row is None:
            return None
        review_id = row[0]
        if review_id in cls.all:
            instance = cls.all[review_id]
            instance.year = row[1]
            instance.summary = row[2]
            instance.employee_id = row[3]
            return instance
        instance = cls(row[1], row[2], row[3], id=row[0])
        cls.all[review_id] = instance
        return instance
   

    @classmethod
    def find_by_id(cls, id):
        """Return a Review instance having the attribute values from the table row."""
        sql = "SELECT * FROM reviews WHERE id = ?"
        row = CURSOR.execute(sql, (id,)).fetchone()
        return cls.instance_from_db(row) if row else None

    def update(self):
        """Update the table row corresponding to the current Review instance."""
        if self.id is not None:
            sql = """
                UPDATE reviews SET year = ?, summary = ?, employee_id = ? WHERE id = ?
            """
            CURSOR.execute(sql, (self.year, self.summary, self.employee_id, self.id))
            CONN.commit()

    def delete(self):
        """Delete the table row corresponding to the current Review instance,
        delete the dictionary entry, and reassign id attribute"""
        if self.id is not None:
            sql = "DELETE FROM reviews WHERE id = ?"
            CURSOR.execute(sql, (self.id,))
            CONN.commit()
            if self.id in type(self).all:
                del type(self).all[self.id]
            self.id = None

    @classmethod
    def get_all(cls):
        """Return a list containing one Review instance per table row"""
        sql = "SELECT * FROM reviews"
        rows = CURSOR.execute(sql).fetchall()
        return [cls.instance_from_db(row) for row in rows] if rows else []

