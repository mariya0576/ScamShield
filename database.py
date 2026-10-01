import sqlite3


DATABASE_NAME = "scamshield.db"


def create_database():

    connection = sqlite3.connect(DATABASE_NAME)

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analysis_history (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            analyzer_type TEXT NOT NULL,

            analyzed_content TEXT,

            risk_level TEXT NOT NULL,

            risk_score INTEGER NOT NULL,

            indicators TEXT,

            recommendation TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
    """)

    cursor.execute("""
        PRAGMA table_info(analysis_history)
    """)

    columns = [
        column[1]
        for column in cursor.fetchall()
    ]

    if "analyzed_content" not in columns:

        cursor.execute("""
            ALTER TABLE analysis_history
            ADD COLUMN analyzed_content TEXT
        """)

    connection.commit()

    connection.close()


def save_analysis(
    analyzer_type,
    analyzed_content,
    risk_level,
    risk_score,
    indicators,
    recommendation
):

    connection = sqlite3.connect(DATABASE_NAME)

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO analysis_history
        (
            analyzer_type,
            analyzed_content,
            risk_level,
            risk_score,
            indicators,
            recommendation
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            analyzer_type,
            analyzed_content,
            risk_level,
            risk_score,
            "\n".join(indicators),
            recommendation
        )
    )

    connection.commit()

    connection.close()


def get_history():

    connection = sqlite3.connect(DATABASE_NAME)

    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM analysis_history
        ORDER BY created_at DESC
        """
    )

    history = cursor.fetchall()

    connection.close()

    return history


def delete_analysis(record_id):

    connection = sqlite3.connect(DATABASE_NAME)

    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM analysis_history
        WHERE id = ?
        """,
        (record_id,)
    )

    connection.commit()

    connection.close()


