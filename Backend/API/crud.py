import sqlite3
import random
from sqlite3 import Connection
from fastapi import HTTPException
from typing import List, Dict, Any
from datetime import datetime
from models import *


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
            raise HTTPException(status_code=404, detail=ERROR_UNGUELTIGE_ID,)
        
        return [dict(row) for row in result]
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database Error: {e}")


def get_all_themen(
    db: Connection
) -> List[str]:
    """Funktion zum auflisten aller Themen.

    Args:
        db(Connection): Datenbankverbindung

    Returns:
        list[str]: Liste mit allen Themenbezeichnungen

    Raises:
        HTTPException: Falls ein Fehler bei der Anfrage auf die Datenbank
        auftritt  
    """
    SQL_GET_THEMEN = "SELECT name FROM Thema"

    try:
        result = db.execute(SQL_GET_THEMEN).fetchall()
        return [row[0] for row in result]  
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database Error: {e}")


def get_aufgaben_by_thema(
    db: Connection
) -> Dict[str, List[dict]]:
    """Funktion um auflisten aller Aufgaben aus einem spezifischen Thema

    Args:
        db(Connection): Datenbankverbindung

    Returns:
        dict[str, List[dict]]: Liste mit allen Themen und den dazugehörigen
        Aufgaben

    Raises:
        HTTPException: Falls ein Fehler bei der Anfrage auf die Datenbank
        auftritt 
    """
    SQL_GET_AUFGABEN_FROM_THEMA = """
    SELECT t.name AS thema_name, a.aufgabeID, a.aussage1, 
    a.aussage2, a.lösung, a.feedback
    FROM Aufgaben AS a
    JOIN Thema AS t ON a.themaID = t.themaID
    """

    try:
        result = db.execute(SQL_GET_AUFGABEN_FROM_THEMA).fetchall()
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
    

def create_quiz(
        bezeichnung, modus: str, db: Connection = None
) -> int:
    """Mit dieser Funktion soll eine neues Quiz erstellt werden
    
    Args:
    bezeichnung (str): Erste Aussage,
    modus (str): Zweite Aussage,  
    db (Connection): Datenbankverbindung

    Returns:
        Dict: Dict mit ID des neuen Quizzes und dem Freigabelink 

    Raises:
        HTTPException: Falls ein Fehler in der Datenbankabfrage aufgetreten ist
    """

    SQL_SELECT_MODI_ID = "SELECT modiID FROM Modi WHERE name = ?"
    SQL_INSERT_QUIZ = """
    INSERT INTO Quiz (bezeichnung, freigabelink, erstelldatum, modiID)
    VALUES (?, ?, ?, ?)
    """
    SQL_UPDATE_QUIZ ="""UPDATE QUIZ SET freigabelink = ? 
    WHERE quizID = ?
    """

    try:
        cursor = db.cursor()
        cursor.execute(SQL_SELECT_MODI_ID, (modus,))
        modus_row = cursor.fetchone()
        
        modiID = modus_row['modiID']
        cursor.execute(SQL_INSERT_QUIZ,(bezeichnung, None, datetime.now(), 
                                        modiID)
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
        cursor.execute(SQL_UPDATE_QUIZ, (freigabelink, quizID))
        db.commit()
        
        # Rückgabe der quizID und des Freigabelinks
        return {"quizID": quizID, "freigabelink": freigabelink}
    except sqlite3.Error as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    

def create_new_teilnehmer(
        name: str, klasse: str, db: Connection = None
) -> int:
    """Mit dieser Funktion soll ein neuer Teilnehmer erstellt werden
    
    Args:
    name (str): Teilnehmername,
    klasse (str): Klasse des Teilnehmers,  
    db (Connection): Datenbankverbindung

    Returns:
        Dict: Dict mit ID des neuen Teilnehmers und einer Bestätigung
    Raises:
        HTTPException: Falls ein Fehler in der Datenbankabfrage aufgetreten ist
    """
    SQL_INSERT_INTO_TEILNEHMER ="""
    INSERT INTO Teilnehmer (name, klasse)
    VALUES (?, ?)
    """

    try:
        cursor = db.cursor()
        cursor.execute(SQL_INSERT_INTO_TEILNEHMER,(name, klasse,))
        db.commit()
        
        # Rückgabe der Teilnehmer-ID
        teilnehmerID = cursor.lastrowid
        return {"T_ID": teilnehmerID, "message": "Teilnehmer erfolgreich erstellt."}
        
    except sqlite3.Error as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    

def add_aufgabe_to_quiz(
        quizID: int, themen: List[str], anzahl_aufgaben: int,
        db: Connection = None
)-> None:
    """Mit dieser Funktion soll zufällige themebezogene Aufgaben ins Quiz hinzugefügt werden
    
    Args:
    quizID (int): Teilnehmername,
    themen (List[str]): Klasse des Teilnehmers,  
    db (Connection): Datenbankverbindung

    Returns:
        Kein Rückgabewert
    Raises:
        HTTPException: Falls keine Themen vorhanden
        HTTPException: Falls keine Aufgabe für Thema gefunden wurde
        HTTPException: Falls ein Fehler in der Datenbankabfrage aufgetreten ist
    """
    if not themen:
        raise HTTPException(status_code=400, detail="Fehlende Themen im Quiz.")
    
    SQL_SELECT_THEMEN = """
    SELECT Aufgaben.aufgabeID
    FROM Aufgaben
    JOIN Thema ON Aufgaben.themaID = Thema.themaID
    WHERE Thema.name IN ({})
    """.format(", ".join(["?" for _ in themen]))

    SQL_INSERT_INTO_QUIZFRAGEN= """
    INSERT INTO Quizzfragen (quizID, aufgabeID)
    VALUES (?, ?)
    """

    ERROR_KEINE_THEMEN = "Keine Aufgaben für die ausgewählten Themen gefunden."

    try:
        cursor = db.cursor()
        result = db.execute(SQL_SELECT_THEMEN, themen).fetchall()

        if not result:
            raise HTTPException(status_code=404, detail=ERROR_KEINE_THEMEN)

        aufgabeIDs = [row["aufgabeID"] for row in result]

        if len(aufgabeIDs) > anzahl_aufgaben:
            aufgabeIDs = random.sample(aufgabeIDs, anzahl_aufgaben)

        for aufgabeID in aufgabeIDs:
            cursor.execute(SQL_INSERT_INTO_QUIZFRAGEN,(quizID, aufgabeID))
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
)-> Dict:
    """Mit dieser Funktion soll ein Aufgabe berbeitet werden können
    
    Args:
    aufgabe_id (int): Aufgaben ID,
    aussage1 (str): Erste Aussage, 
    aussage2 (str): Zweite Aussage, 
    lösung (int): Lösung der Aufgabe
    Feedback (str): Feedback zur Lösung
    db (Connection): Datenbankverbindung

    Returns:
        Dict: Dict mit der aktualisierten Aufgabe
    Raises:
        HTTPException: Falls Aufgabe mittels ID nicht gefunden werden kann
        HTTPException: Falls ein Fehler in der Datenbankabfrage aufgetreten ist
    """
    SQL_GET_FROM_AUFGABE = "SELECT * FROM Aufgaben WHERE aufgabeID = ?"
    SQL_UPDATE_AUFGABE ="""
    UPDATE Aufgaben
    SET aussage1 = ?, aussage2 = ?, lösung = ?, feedback = ?
    WHERE aufgabeID = ?
    """
    SQL_GET_ALL_FROM_AUFGABE = """
    SELECT aufgabeID, aussage1, aussage2, lösung, feedback 
    FROM Aufgaben WHERE aufgabeID = ?
    """
    ERROR_ID_NICHT_GEFUNDEN = f"Aufgabe mit ID {aufgabe_id} nicht gefunden."
    ERROR_AUFGABE_AUFRUF = "Fehler beim Abrufen der aktualisierten Aufgabe."

    try:
        # Überprüfen, ob die Aufgabe existiert
        cursor = db.cursor()
        cursor.execute(SQL_GET_FROM_AUFGABE, (aufgabe_id,))
        existing_aussage = cursor.fetchone()
        
        if not existing_aussage:
            raise HTTPException(status_code=404, detail=ERROR_ID_NICHT_GEFUNDEN)
        
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
        cursor.execute(SQL_UPDATE_AUFGABE,(
                current_values["aussage1"],
                current_values["aussage2"],
                current_values["lösung"],
                current_values["feedback"],
                aufgabe_id,
            ),
        )
        db.commit()
        
        # Rückgabe der aktualisierten Aufgabe
        updated_aussage = db.execute(SQL_GET_ALL_FROM_AUFGABE,(aufgabe_id,)
        ).fetchone()
        
        if not updated_aussage:
            raise HTTPException(status_code=500, detail=ERROR_AUFGABE_AUFRUF)
        
        return dict(updated_aussage)  # Konvertiert sqlite3.Row in Dict
    except sqlite3.Error as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    
# Quiz löschen
def delete_quiz(
        quiz_id: int, db: Connection = None
)->None:
    """Mit dieser Funktion soll ein Aufgabe berbeitet werden können
    
    Args:
    quiz_id (int): Quiz ID,
    db (Connection): Datenbankverbindung

    Returns:
        None
    Raises:
        HTTPException: Falls Aufgabe mittels ID nicht gefunden werden kann
        HTTPException: Falls ein Fehler in der Datenbankabfrage aufgetreten ist
    """
    SQL_GET_ALL_FROM_QUIZ = "SELECT * FROM Quiz WHERE quizID = ?"
    SQL_DELETE_FROM_QUIZ = "DELETE FROM Quiz WHERE quizID = ?"
    ERROR_ID_NICHT_GEFUNDEN = f"Aufgabe mit ID {quiz_id} nicht gefunden."

    try:
        cursor = db.cursor()
        cursor.execute(SQL_GET_ALL_FROM_QUIZ, (quiz_id,))
        existing_quiz = cursor.fetchone()
        
        if not existing_quiz:
            raise HTTPException(status_code=404, detail=ERROR_ID_NICHT_GEFUNDEN)
        
        cursor.execute(SQL_DELETE_FROM_QUIZ,(quiz_id,),)
        db.commit()

    except sqlite3.Error as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

        