<<<<<<< HEAD
from fastapi import FastAPI, HTTPException, Depends, Query, Path, Body, Response
=======
from fastapi import FastAPI, HTTPException, Depends, Query, Path, Body
>>>>>>> 2d5aeae22637f94b0c6ac790ab58b067309ef494
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict
from sqlite3 import Connection
from models import TeilnehmerRequest, AntwortRequest, Aufgabenschema, QuizSchema
from crud import *
from database import get_db_connection

# FastAPI-App
app = FastAPI()

# CORS-Einstellungen
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://127.0.0.1:8000",
        "http://localhost:8000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Teste die Datenbankverbindung
@app.get("/quizze/test-connection")
def test_connection(db: Connection = Depends(get_db_connection)):
    try:
        get_all_aufgaben(db)
        return {"status": "success", "message": "Database connection is working!"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Überprüft die Lehrerkennzahl
@app.get("/quizze/lehrer/")
<<<<<<< HEAD
def check_lehrerkennzahl(lehrerkennzahl: str, response:Response, db: Connection = Depends(get_db_connection)):
    result = get_lehrerkennzahl(lehrerkennzahl, db)
    
    if result:
        # send a cookie to the browser to notify that a teacher is using the tool
        response.set_cookie(key="role", value="teacher")
        return {"status": "success", "data": result}
    else:
        # Fehler bei ungültiger Lehrerkennzahl
        raise HTTPException(status_code=401, detail="Ungültige Lehrerkennzahl")
=======
def check_lehrerkennzahl(lehrerkennzahl: str, db: Connection = Depends(get_db_connection)):
    result = get_lehrerkennzahl(lehrerkennzahl, db)
    return {"status": "success", "data": result}
>>>>>>> 2d5aeae22637f94b0c6ac790ab58b067309ef494

@app.get("/aufgaben")
def get_aufgaben(db: Connection = Depends(get_db_connection)):
    try:
        result = get_all_aufgaben(db)
        return {"status": "success", "data": result}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

@app.get("/modi")
def get_modi(db: Connection = Depends(get_db_connection)):
    try:
        result = get_all_modi(db)
        return {"status": "success", "data": result}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

#Listet die Beziechnung von allen Quizzen
@app.get("/quizze/")
def get_quizze(db: Connection = Depends(get_db_connection)):
    try:
        result = get_all_quizze(db)
        return {"status": "success", "data": result}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

# Liste alle Aufgaben von jeweiligen Themen auf
@app.get("/quizze/aufgaben/")
def get_aufgaben(db: Connection = Depends(get_db_connection)):
    try:
        aufgaben = get_aufgaben_by_thema(db)
        return {"status": "success", "data": aufgaben}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

#Listet den gebauten Quiz mit den zufälligen Aufgaben
@app.get("/quizze/{quizID}")
def get_quiz(quizID: int, db: Connection = Depends(get_db_connection)):
    try:
        quiz = get_quiz_with_fragen(quizID, db)
        return {"status": "success", "data": quiz}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

#Listet alle Aufgaben vom jeweiligem Thema
@app.get("/quizze/aufgaben/{thema_name}")
def get_aufgaben_by_thema_name(thema_name: str, db: Connection = Depends(get_db_connection)):
    try:
        aufgaben = get_aufgaben_by_thema(db)
        
        # Wenn das Thema nicht gefunden wurde
        if thema_name not in aufgaben:
            return {"status": "success", "message": f"Keine Aufgaben für Thema '{thema_name}' gefunden.", "data": []}
        
        return {"status": "success", "data": aufgaben[thema_name]}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

# Listet alle vorhandenen Themen
@app.get("/quizze/themen/")
def get_alle_themen(db: Connection = Depends(get_db_connection)):
    try:
        themen = get_all_themen(db)
        return {"status": "success", "data": themen}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

# Neue Thema erstellen
@app.post("/quizze/themen/")
def post_new_thema(themaName: str, db: Connection = Depends(get_db_connection)):
    result = create_new_thema(themaName, db)
    return result

# Erstelle neue Aufgabe
@app.post("/quizze/aufgaben/")
def post_new_aufgabe(
    aufgabe: Aufgabenschema = Body(...),  # Body(...) stellt sicher, dass JSON-Body verarbeitet wird
    db: Connection = Depends(get_db_connection)
):
    result = create_new_aufgabe(aufgabe.aussage1, aufgabe.aussage2, aufgabe.lösung, aufgabe.feedback, aufgabe.thema, db)
    return {"status": "success", "data": result}
    
# Erstelle Quiz
@app.post("/quizze/")
def create_new_quiz(
    quiz: QuizSchema,
    db: Connection = Depends(get_db_connection)
):
    # Erstelle ein neues Quiz
    quiz_data = create_quiz(quiz.bezeichnung, quiz.modus, db)  # Quiz erstellen
    quizID = quiz_data["quizID"]
    freigabelink = quiz_data["freigabelink"]
    
    # Übergebe die 'themen' korrekt an die Funktion zum Hinzufügen von Aufgaben
    add_aufgabe_to_quiz(quizID, quiz.themen, quiz.anzahl_aufgaben, db)
    
    return {"status": "success", "quizID": quizID, "freigabelink": freigabelink}

# Aktualisieren einer Aufgabe
@app.put("/quizze/aufgaben/{aufgabe_id}")
def put_update_aufgabe(
    aufgabe_id: int = Path(..., description="Die ID der Aufgabe, die aktualisiert werden soll."),
    aussage1: str = None,
    aussage2: str = None,
    lösung: int = None,
    feedback: str = None,
    db: Connection = Depends(get_db_connection)
):
    try:
        # Überprüfen, ob mindestens ein Feld zum Aktualisieren angegeben wurde
        if all(field is None for field in [aussage1, aussage2, lösung, feedback]):
            raise HTTPException(status_code=400, detail="Mindestens ein Feld muss zum Aktualisieren angegeben werden.")
        
        # Aktualisieren der Aufgabe
        updated_aussage = update_aufgabe(aufgabe_id, aussage1, aussage2, lösung, feedback, db)
        return {"status": "success", "data": updated_aussage}
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")
    

# Erstelle Teilnehmer
@app.post("/quizze/teilnehmern/")
def post_new_teilnehmer(
    teilnehmer: TeilnehmerRequest,  
    db: Connection = Depends(get_db_connection)
):
<<<<<<< HEAD
    result = create_new_teilnehmer(teilnehmer.schuelernummer, teilnehmer.klasse, db)
=======
    result = create_new_teilnehmer(teilnehmer.name, teilnehmer.klasse, db)
>>>>>>> 2d5aeae22637f94b0c6ac790ab58b067309ef494
    return {"status": "success", "data": result}


# Überprüfung der Ergebnisse 
@app.post("/quizze/{quizID}/pruefung/")
def check_antworten(
    schema: AntwortRequest,
    db: Connection = Depends(get_db_connection)
):
<<<<<<< HEAD
    result = calculate_result(schema, db)
    return {"status": "success", "data": result}


# Übergibt alle prüfungen, die erstellt wurden 
@app.get("/quizze/pruefung/bezeichnungen")
def get_prüfung_bezeichnung(
    db: Connection = Depends(get_db_connection)
):
    pruefung_bezeichnung = show_pruefung_bezeichnungen(db)
    
    return {"status": "success", "data": pruefung_bezeichnung}


# Übergibt Teilnehmer und Ergebnisse, die in Prüfung teilgenommen hatten
@app.get("/quizze/pruefung/ergebnisse")
def get_prüfung_ergebnisse(
    pruefung_bezeichnung: str,
    db: Connection = Depends(get_db_connection)
):
    result = show_pruefung_ergebnisse(pruefung_bezeichnung, db)
    
    return {"status": "success", "data": result}

# Delete a task by its ID
@app.delete("/quizze/aufgaben/{aufgabe_id}")
def delete_aufgabe(
    aufgabe_id: int = Path(..., description="Die ID der Aufgabe, die gelöscht werden soll."),
    db: Connection = Depends(get_db_connection)
):
    try:
        # Check if the task exists
        cursor = db.cursor()
        cursor.execute("SELECT * FROM aufgaben WHERE aufgabeID = ?", (aufgabe_id,))
        task = cursor.fetchone()

        if not task:
            raise HTTPException(status_code=404, detail="Aufgabe nicht gefunden.")

        # Delete the task
        cursor.execute("DELETE FROM aufgaben WHERE aufgabeID = ?", (aufgabe_id,))
        db.commit()

        return {"status": "success", "message": f"Aufgabe mit ID {aufgabe_id} wurde erfolgreich gelöscht."}
=======
    quizID = schema.quizID
    teilnehmerID = schema.teilnehmerID
    antworten = schema.antworten
    anz_richtig = 0
    
    try:
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
        erfolgsquote = (anz_richtig / len(antworten)) * 100

        # Speichere die Prüfung und das Ergebnis
        cursor = db.cursor()
        cursor.execute("INSERT INTO Prüfung (quizID) VALUES (?)", (quizID,))
        prüfungsID = cursor.lastrowid

        cursor.execute("INSERT INTO Prüfung_Teilnehmer (T_ID, P_ID, Ergebnis) VALUES (?, ?, ?)", 
                       (teilnehmerID, prüfungsID, erfolgsquote))
        db.commit()

        return {"status": "success", "msg": "Vielen danke für Ihre Abgabe!"}
>>>>>>> 2d5aeae22637f94b0c6ac790ab58b067309ef494

    except HTTPException as e:
        raise e
    except Exception as e:
<<<<<<< HEAD
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")
=======
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

# Quiz löschen    
@app.delete("/quizze/{quiz_id}")
def remove_quiz(
    quiz_id: int,
    db: Connection = Depends(get_db_connection) 
    ):

    try:
        delete_quiz(quiz_id, db)
        return {"status": "success", "deleted_quiz": {quiz_id}}

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")
    

>>>>>>> 2d5aeae22637f94b0c6ac790ab58b067309ef494
