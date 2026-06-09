import mysql.connector
<<<<<<< HEAD
import os

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        port=os.getenv("DB_PORT")
    )
=======
import os 

def get_connection():
    return mysql.connector.connect(
        host = os.getenv("host"),
        user = os.getenv("user"),
        password = os.getenc("password"),
        database = os.getenv("database"),
        port = os.getenv("port")
    )


def create_booking():
    conn = get_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reservations(
                reservation_id INT PRIMARY KEY AUTO_INCREMENT,
                user_id INT NOT NULL,
                table_id INT,
                booking_date DATE NOT NULL,
                booking_time TIME NOT NULL,
                size INT NOT NULL,
                status VARCHAR(30) NOT NULL DEFAULT 'booked',

                CONSTRAINT fk_reservations_user
                    FOREIGN KEY (user_id) REFERENCES Users(user_id),

                CONSTRAINT fk_reservations_table
                    FOREIGN KEY (table_id) REFERENCES RestaurantTables(table_id)
            );
        ''')
>>>>>>> 5111370 (Creation of main home page and tempates for many of the pages that will be included, creating a connection  to the db and adding the reservation table, added some logic and a basic form for the booking page, yet to hook up to the db as users and other tables are needed. CSS for the pages included, add as you go along)
