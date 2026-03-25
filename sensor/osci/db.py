import sqlite3
import pickle

class OscDb:
    def __init__(self, db_name="osc.db"):
        """Initialisiert die Verbindung zur SQLite-Datenbank und erstellt die Tabelle, falls sie nicht existiert."""
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self._create_table()

    def _create_table(self):
        """Erstellt eine Tabelle, falls sie nicht existiert."""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS data (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                data_blob BLOB
            )
        """)
        self.conn.commit()

    def insert_array(self, arr):
        """Speichert ein Integer-Array als BLOB in der Datenbank."""
        arr_blob = pickle.dumps(arr)  # Konvertiere Liste in Bytes
        self.cursor.execute("INSERT INTO data (data_blob) VALUES (?)", (arr_blob,))
        self.conn.commit()
        return self.cursor.lastrowid  # Gibt die ID des eingefügten Datensatzes zurück

    def get_array(self, id):
        """Ruft ein gespeichertes Integer-Array anhand der ID ab und gibt es als Liste zurück."""
        self.cursor.execute("SELECT data_blob FROM data WHERE id=?", (id,))
        row = self.cursor.fetchone()
        return pickle.loads(row[0]) if row else None  # Bytes zurück in Liste konvertieren

    def close(self):
        """Schließt die Datenbankverbindung."""
        self.conn.close()

# # Beispiel-Nutzung
# db = SQLiteArrayDB()
# id1 = db.insert_array([1, 2, 3, 4, 5])
# print(f"Gespeicherte ID: {id1}")
# print(f"Abgerufenes Array: {db.get_array(id1)}")
#
# db.close()
