import sqlite3
import random
from sqlite3 import Connection
from fastapi import HTTPException
from typing import List, Dict, Any
from datetime import datetime
from models import AntwortRequest, ErgebnisRequest, ErgebnissSchema

def get_all_aufgaben(
    db: Connection,
) -> list[Dict[str, Any]]:
    """Funktion für Abruf von allen Aufgaben

    Args:
        db (Connection): Datenbankverbindung

    Returns:
        list[dict[str, Any]]: Liste mit Dictionaries, die Details zu den
        Aufgaben enthalten

    Raises:
        HTTPException: Falls ein Fehler bei der Anfrage auf die Datenbank
        auftritt
    """
    SQL_GET_ALL_AUFGABEN = "SELECT * FROM Aufgaben"

    try:
        result = db.execute(SQL_GET_ALL_AUFGABEN ).fetchall()
        return [dict(row) for row in result]  
    except sqlite3.DatabaseError as e:
        raise HTTPException(status_code=500, detail=f"Database query error: {e}")


def get_lehrerkennzahl(
    lehrerkennzahl: str, db: Connection,
) -> list[Dict[str, Any]]:
    """Funktion zum validieren einer Lehrerkennzahl

        Args:
        input_lehrerkennzahl (str),
        db(Connection): Datenbankverbindung

    Returns:
        list[dict[str, Any]]: Liste mit Dictionaries, die Details zu den
        Aufgaben enthalten

    Raises:
        HTTPException: Falls ein Fehler bei der Anfrage auf die Datenbank
        auftritt
    """
    SQL_GET_LEHRER_BY_ID = "SELECT * FROM Lehrer WHERE lehrerkennzahl = ?"
    ERROR_UNGUELTIGE_ID = "Ungültige Lehrerkennzahl. Bitte versuchen Sie es erneut."

    try:
        result = db.execute(
            SQL_GET_LEHRER_BY_ID, (lehrerkennzahl,)
        ).fetchall()

        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"Ungültige Lehrerkennzahl. Bitte versuchen Sie es erneut.",
            )
        return [dict(row) for row in result]  # Konvertiert sqlite3.Row in Dict
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database Error: {e}")


# Listet alle Themen auf
def get_all_themen(db: Connection) -> List[str]:
    try:
        result = db.execute("SELECT name FROM Thema").fetchall()
        return [row[0] for row in result]  # Extrahiert die Themennamen aus den Tupeln
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database Error: {e}")


# Listet alle Aufgaben aus jeweiligen Themen
def get_aufgaben_by_thema(db: Connection) -> Dict[str, List[Dict]]:
    try:
        # Abfrage, um Aufgaben und Themen zu verknüpfen
        query = """
        SELECT Thema.name AS thema_name, Aufgaben.aufgabeID, Aufgaben.aussage1, Aufgaben.aussage2, Aufgaben.lösung, Aufgaben.feedback
        FROM Aufgaben
        JOIN Thema ON Aufgaben.themaID = Thema.themaID
        """
        result = db.execute(query).fetchall()
        
        return result
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")


def get_all_quizze(
    db: Connection
) -> list[dict[str, Any]]:
    """Mit dieser Funktion lassen sich alle Quizze abrufen.

    Args:
        db(Connection): Datenbankverbindung

    Returns:
        list[dict[str, Any]]: Liste mit allen Quizzen und deren Details

    Raises:
        HTTPException: Falls ein Fehler bei der Anfrage auf die Datenbank
        auftritt 
    """
    SQL_GET_ALL_QUIZZE = """
    SELECT q.quizID, q.bezeichnung, 
    Count(qf.aufgabeID) as Anzahl_Aufgaben, q.freigabelink,
    m.name AS modi_name, q.erstelldatum
    FROM Quiz AS q
    LEFT JOIN Modi AS m ON q.modiID = m.modiID
    LEFT JOIN Quizzfragen AS qf ON q.quizID = qf.quizID
    GROUP BY q.quizID, q.freigabelink, q.erstelldatum, m.name;
    """

    try:
        quizze = db.execute(SQL_GET_ALL_QUIZZE).fetchall()
        return quizze
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database Error: {e}")
    

def get_quiz_with_fragen(
    quiz_id: int, db: Connection = None
) -> Dict:
    """Funktion zum auslesen festgelegter Details eines Quizzes. 

    Args:
        quiz_id (int): ID des Quizzes,
        db(Connection): Datenbankverbindung

    Returns:
        Dict: Dict mit Details zum Quiz und einer Liste mit allen Aufgabendetails

    Raises:
        HTTPException: Falls QuizID keinem Quiz zugeordnet werden kann oder
        ein Fehler in der Datenbankabfrage vorliegt
    """

    SQL_GET_QUIZ_BY_ID ="""
    SELECT quizID, freigabelink, erstelldatum, modiID
    FROM Quiz
    WHERE quizID = ?
    """
    SQL_GET_ALL_AUFGABEN_FOR_QUIZ ="""
    SELECT a.aufgabeID, a.aussage1, a.aussage2, a.lösung, a.feedback
    FROM Quizzfragen AS qf
    JOIN Aufgaben AS a ON qf.aufgabeID = a.aufgabeID
    WHERE qf.quizID = ?
    """
    ERROR_UNGUELTIGE_QUIZ_ID = f"Quiz mit ID {quiz_id} nicht gefunden."

    try:
        quiz = db.execute(SQL_GET_QUIZ_BY_ID, (quiz_id,)).fetchone()
        
        if not quiz:
            raise HTTPException(status_code=404, 
                                detail=ERROR_UNGUELTIGE_QUIZ_ID)
        
        modus_id = quiz['modiID']
        aufgaben = db.execute(SQL_GET_ALL_AUFGABEN_FOR_QUIZ, 
                              (quiz_id,)).fetchall()
        
        # Konvertiere sqlite3.Row in Dict
        aufgaben_dict = [dict(aufgabe) for aufgabe in aufgaben]
        
        # Bei Prüfungsmodus entfernen von Anzeige Lösung und Feedback
        if modus_id == 2:  
            for aufgabe in aufgaben_dict:
                if 'lösung' or 'feedback' in aufgabe:
                    del aufgabe['lösung']
                    del aufgabe['feedback'] 
        quiz_dict = dict(quiz)

        #Füge Aufgaben in Quiz Dict hinzu
        quiz_dict["Aufgaben"] = aufgaben_dict
        return quiz_dict
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")


# Neuer Thema wird erstellt
def create_new_thema(
    thema_name: str, db: Connection
) -> Dict:
    """Diese Funktion dient dazu ein neues Thema zu erstellen

    Args:
        themaName (str): Themenname,
        db(Connection): Datenbankverbindung

    Returns:
        Dict: Liste mit allen Quizzen und deren Details

    Raises:
        HTTPException: Falls ein Fehler bei der Anfrage auf die Datenbank
        auftritt 
    """
    SQL_GET_THEMA_BY_ID = "SELECT * FROM Thema WHERE name = ?"
    ERROR_THEMA_DUPLIKAT = f"Thema '{thema_name}' existiert bereits."
    SQL_INSERT_THEMA = "INSERT INTO Thema (name) VALUES (?)"
    THEMA_ANGELEGT = f"Thema '{thema_name}' wurde erfolgreich angelegt."

    try:
        # Prüft, ob Thema existiert
        existing_thema = db.execute(SQL_GET_THEMA_BY_ID, 
                                    (thema_name,)).fetchone()

        if existing_thema:
            raise HTTPException(status_code=400, detail=ERROR_THEMA_DUPLIKAT)
        
        # Fügt Thema ein, wenn es noch nicht vorhanden ist
        db.execute(SQL_INSERT_THEMA, (thema_name,))
        db.commit()

        return {"message": THEMA_ANGELEGT}
    except Exception as e:
        # Rollback bei Fehlern
        db.rollback()  
        raise HTTPException(status_code=500, detail=f"Ein Fehler ist aufgetreten: {e}")


# Erstellt eine Neue Aufgabe
def create_new_aufgabe(
    #aufgabe: Aufgabenschema,
    aussage_1: str,
    aussage_2: str, 
    lösung: int, 
    feedback: str, 
    thema: str, 
    db: Connection
) -> Dict:
    """Mit dieser Funktion soll eine neue Aufgabe erstellt werden

    Args:
        aussage_1 (str): Erste Aussage,
        aussage_2 (str): Zweite Aussage, 
        lösung (int): Lösungsnummer, 
        feedback (str): Lösungsfeedback, 
        thema (str): Thema zur Aufgabe, 
        db(Connection): Datenbankverbindung

    Returns:
        Dict: Dict mit allen Aufgabendatails 

    Raises:
        HTTPException: Falls ein Thema nicht gefunden wurde, eine Aufgabe
        nicht abgerufen werden konnte oder ein Fehler in der Datenbank-
        abfrage aufgetreten ist
    """

    SQL_GET_THEMA_ID_BY_NAME = "SELECT themaID FROM Thema WHERE name = ?"
    SQL_INSERT_INTO_AUFGABEN = """
    INSERT INTO Aufgaben (themaID, aussage1, aussage2, lösung, feedback) 
    VALUES (?, ?, ?, ?, ?)
    """
    SQL_GET_DETAILS_FROM_AUFGABE = """
    SELECT aufgabeID, themaID, aussage1, aussage2, lösung, feedback 
    FROM Aufgaben 
    WHERE aufgabeID = ?
    """
    ERROR_FEHLER_AUFRUFEN_AUFGABE = "Fehler beim Abrufen der neuen Aufgabe"

    try:
        cursor = db.cursor()
        cursor.execute(SQL_GET_THEMA_ID_BY_NAME, (thema,))
        thema_row = cursor.fetchone()
        
        if not thema_row:
            raise HTTPException(status_code=404, detail="Thema nicht gefunden")
        
        thema_id = thema_row['themaID']
        cursor.execute(SQL_INSERT_INTO_AUFGABEN,
                       (thema_id, aussage_1, aussage_2, 
                        lösung, feedback)
        )
        db.commit()
        
        new_aufgabe_id = cursor.lastrowid
        new_aufgabe = db.execute(SQL_GET_DETAILS_FROM_AUFGABE,
                                (new_aufgabe_id,)).fetchone()
        
        if not new_aufgabe:
            raise HTTPException(status_code=500, 
                                detail = ERROR_FEHLER_AUFRUFEN_AUFGABE)

        return dict(new_aufgabe) 
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ein Fehler ist aufgetreten: {e}")
    
    
# Erstelle Quiz
def create_quiz(bezeichnung, modus: str, db: Connection = None) -> int:
    try:
        # Füge ein neues Quiz in die Datenbank ein
        cursor = db.cursor()
        cursor.execute("SELECT modiID FROM Modi WHERE name = ?", (modus,))
        modus_row = cursor.fetchone()
        
        modiID = modus_row['modiID']
        cursor.execute(
            """
            INSERT INTO Quiz (bezeichnung, freigabelink, erstelldatum, modiID)
            VALUES (?, ?, ?, ?)
            """,
            (bezeichnung, None, datetime.now(), modiID)
        )
        db.commit()
        
        quizID = cursor.lastrowid
        
        # Generiere den Freigabelink
        if (modiID == 2):
            modi = 'pruefung'
        else:
            modi = 'uebung'
        freigabelink = f"http://127.0.0.1:5500/frontend/schuelerView/{modi}.html?quizID={quizID}"
 
        # Update das Quiz mit dem generierten Freigabelink
        cursor.execute(
            """
            UPDATE QUIZ
            SET freigabelink = ?
            WHERE quizID = ?
            """,
            (freigabelink, quizID)
        )
        db.commit()
        
        # Rückgabe der quizID und des Freigabelinks
        return {"quizID": quizID, "freigabelink": freigabelink}
    except sqlite3.Error as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    
    
# Erstelle Teilnemer
def create_new_teilnehmer(schuelernummer: str, klasse: str, db: Connection = None) -> int:
    try:
        # Füge ein neues Quiz in die Datenbank ein
        cursor = db.cursor()
        cursor.execute(
            """
            INSERT INTO Teilnehmer (Schuelernummer, klasse)
            VALUES (?, ?)
            """,
            (schuelernummer, klasse,)
        )
        db.commit()
        
        # Rückgabe der Teilnehmer-ID
        teilnehmerID = cursor.lastrowid
        return {"T_ID": teilnehmerID, "message": "Teilnehmer erfolgreich erstellt."}
        
    except sqlite3.Error as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    

# Fügt zufällige Aufgaben je nach Themen in den Quiz hinzu
def add_aufgabe_to_quiz(quizID: int, themen: List[str], anzahl_aufgaben: int, db: Connection = None):
    if not themen:
        raise HTTPException(status_code=400, detail="Fehlende Themen im Quiz.")
    
    try:
        cursor = db.cursor()
        
        # Platzhalter für jedes Thema erstellen
        query = """
        SELECT Aufgaben.aufgabeID
        FROM Aufgaben
        JOIN Thema ON Aufgaben.themaID = Thema.themaID
        WHERE Thema.name IN ({})
        """.format(", ".join(["?" for _ in themen]))

        result = db.execute(query, themen).fetchall()

        if not result:
            raise HTTPException(status_code=404, detail="Keine Aufgaben für die ausgewählten Themen gefunden.")

        aufgabeIDs = [row["aufgabeID"] for row in result]

        if len(aufgabeIDs) > anzahl_aufgaben:
            aufgabeIDs = random.sample(aufgabeIDs, anzahl_aufgaben)

        for aufgabeID in aufgabeIDs:
            cursor.execute(
                """
                INSERT INTO Quizzfragen (quizID, aufgabeID)
                VALUES (?, ?)
                """,
                (quizID, aufgabeID)
            )

        db.commit()

    except sqlite3.Error as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

    

# Bearbeitung einer Aufgabe
def update_aufgabe(
    aufgabe_id: int,
    aussage1: str = None,
    aussage2: str = None,
    lösung: int = None,
    feedback: str = None,
    db: Connection = None
):
    try:
        # Überprüfen, ob die Aufgabe existiert
        cursor = db.cursor()
        cursor.execute("SELECT * FROM Aufgaben WHERE aufgabeID = ?", (aufgabe_id,))
        existing_aussage = cursor.fetchone()
        
        if not existing_aussage:
            raise HTTPException(status_code=404, detail=f"Aufgabe mit ID {aufgabe_id} nicht gefunden.")
        
        # Erstellen eines Dictionaries mit den aktuellen Werten
        current_values = {
            "aussage1": existing_aussage["aussage1"],
            "aussage2": existing_aussage["aussage2"],
            "lösung": existing_aussage["lösung"],
            "feedback": existing_aussage["feedback"],
        }
        
        # Aktualisieren der Werte, falls neue Werte bereitgestellt wurden
        if aussage1 is not None:
            current_values["aussage1"] = aussage1
        if aussage2 is not None:
            current_values["aussage2"] = aussage2
        if lösung is not None:
            current_values["lösung"] = lösung
        if feedback is not None:
            current_values["feedback"] = feedback
        
        # Aktualisieren der Aufgabe in der Datenbank
        cursor.execute(
            """
            UPDATE Aufgaben
            SET aussage1 = ?, aussage2 = ?, lösung = ?, feedback = ?
            WHERE aufgabeID = ?
            """,
            (
                current_values["aussage1"],
                current_values["aussage2"],
                current_values["lösung"],
                current_values["feedback"],
                aufgabe_id,
            ),
        )
        db.commit()
        
        # Rückgabe der aktualisierten Aufgabe
        updated_aussage = db.execute(
            "SELECT aufgabeID, aussage1, aussage2, lösung, feedback FROM Aufgaben WHERE aufgabeID = ?",
            (aufgabe_id,)
        ).fetchone()
        
        if not updated_aussage:
            raise HTTPException(status_code=500, detail="Fehler beim Abrufen der aktualisierten Aufgabe.")
        
        return dict(updated_aussage)  # Konvertiert sqlite3.Row in Dict
    except sqlite3.Error as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

# Berechnet das Ergebnis des Teilnehmers
def calculate_result (
    schema: AntwortRequest,
    db: Connection = None
):
    try:
        quizID = schema.quizID
        teilnehmerID = schema.teilnehmerID
        antworten = schema.antworten
        anz_richtig = 0
        # Überprüfe, ob das Quiz existiert
        quiz = db.execute("SELECT * FROM Quiz WHERE quizID = ?", (quizID,)).fetchone()
        if not quiz:
            raise HTTPException(status_code=404, detail=f"Quiz {quizID} nicht gefunden.")

        # Überprüfe jede Antwort
        for ergebnis in antworten:
            aufgabe = db.execute("""
                SELECT aufgabeID, lösung
                FROM Aufgaben
                WHERE aufgabeID = ?
            """, (ergebnis.aufgabeID,)).fetchone()

            if not aufgabe:
                raise HTTPException(status_code=404, detail=f"Aufgabe mit ID {ergebnis['aufgabeID']} nicht gefunden.")

            if aufgabe["lösung"] == ergebnis.auswahl:
                anz_richtig += 1

        # Berechne die Erfolgsquote
        erfolgsquote = round((anz_richtig / len(antworten)) * 100, 2)

        # Speichere die Prüfung und das Ergebnis
        cursor = db.cursor()
        cursor.execute("INSERT INTO Prüfung (quizID) VALUES (?)", (quizID,))
        prüfungsID = cursor.lastrowid

        cursor.execute("INSERT INTO Prüfung_Teilnehmer (T_ID, P_ID, Ergebnis) VALUES (?, ?, ?)", 
                       (teilnehmerID, prüfungsID, erfolgsquote))
        db.commit()

        return {"msg": "Vielen danke für Ihre Abgabe!"}

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")
    
# Zeigt alle Prüfungen, die von Lehrer erstellt wurden
def show_pruefung_bezeichnungen(db: Connection = None):
    try:
        quiz_bezeichnung = db.execute("""
            SELECT bezeichnung
            FROM Quiz
            WHERE modiID = 2
        """).fetchall()
        
        if not quiz_bezeichnung:
                raise HTTPException(status_code=404, detail=f"Es wurden keine Prüfungen gefunden.")
        
        return [row[0] for row in quiz_bezeichnung]  # Extrahiert die Bezeichnungen aus den Quizzen mit modi = Prüfung
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

# Zeigt die Ergebnisse der Teilnehmer je nach Prüfung
def show_pruefung_ergebnisse(pruefung_bezeichnung: str, db: Connection = None) -> ErgebnisRequest:
    try:
        quiz = db.execute("""
            SELECT quizID
            FROM Quiz
            WHERE bezeichnung = ?               
        """, (pruefung_bezeichnung,)).fetchone()
        
        if not quiz:
            raise HTTPException(status_code=404, detail=f"Kein Quiz mit Bezeichnung '{pruefung_bezeichnung}' gefunden.")

        quizID = quiz["quizID"]

        # Hole alle Prüfungs-IDs basierend auf der Quiz-ID
        pruefungen = db.execute("""
            SELECT P_ID
            FROM Prüfung
            WHERE quizID = ?
        """, (quizID,)).fetchall()
        
        if not pruefungen:
            raise HTTPException(status_code=404, detail=f"Es wurden keine Prüfungen für die Quiz-ID {quizID} gefunden.")

        # Liste für die Teilnehmer-Ergebnisse
        teilnehmer_liste = []

        for pruefung in pruefungen:
            pruefungID = pruefung["P_ID"]

            # Hole alle Ergebnisse für diese Prüfung
            ergebnisse = db.execute("""
                SELECT Teilnehmer.schuelernummer, Teilnehmer.Klasse, Prüfung_Teilnehmer.Ergebnis
                FROM Prüfung_Teilnehmer 
                LEFT JOIN Teilnehmer on Prüfung_Teilnehmer.T_ID = Teilnehmer.T_ID
                WHERE Prüfung_Teilnehmer.P_ID = ?
            """, (pruefungID,)).fetchall()

            # Falls keine Teilnehmer-Ergebnisse gefunden wurden, weiter zur nächsten Prüfung
            if ergebnisse:
                for ergebnis in ergebnisse:
                    teilnehmer_liste.append(ErgebnissSchema(
                        schuelernummer=ergebnis["schuelernummer"],
                        klasse=ergebnis["Klasse"],
                        ergebnis=ergebnis["Ergebnis"]
                    ))

        if not teilnehmer_liste:
            raise HTTPException(status_code=404, detail=f"Es wurden keine Teilnehmer für das Quiz '{pruefung_bezeichnung}' gefunden.")

        # Rückgabe als Pydantic-Model
        return ErgebnisRequest(
            quizID=quizID,
            quizbezeichnung=pruefung_bezeichnung,
            teilnehmer=teilnehmer_liste
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")
