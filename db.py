import mysql.connector
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
