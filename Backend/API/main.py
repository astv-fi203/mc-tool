from fastapi import FastAPI, HTTPException, Depends, Query, Path, Body, Response
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict
from sqlite3 import Connection
from models import TeilnehmerRequest, AntwortRequest, Aufgabenschema, QuizSchema
from crud import (
    get_all_aufgaben,
    get_all_quizze,
    get_all_themen,
    get_all_modis,
    get_lehrerkennzahl,
    get_aufgaben_by_thema,
    get_quiz_with_fragen,
    create_new_teilnehmer,
    create_new_thema,
    create_new_aufgabe,
    create_quiz,
    add_aufgabe_to_quiz,
    update_aufgabe
)
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
def check_lehrerkennzahl(lehrerkennzahl: str, response:Response, db: Connection = Depends(get_db_connection)):
    result = get_lehrerkennzahl(lehrerkennzahl, db)
    
    if result:
        # send a cookie to the browser to notify that a teacher is using the tool
        response.set_cookie(key="role", value="teacher")
        return {"status": "success", "data": result}
    else:
        # Fehler bei ungültiger Lehrerkennzahl
        raise HTTPException(status_code=401, detail="Ungültige Lehrerkennzahl")

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
    result = create_new_teilnehmer(teilnehmer.name, teilnehmer.klasse, db)
    return {"status": "success", "data": result}


# Überprüfung der Ergebnisse 
@app.post("/quizze/{quizID}/pruefung/")
def check_antworten(
    schema: AntwortRequest,
    db: Connection = Depends(get_db_connection)
):
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

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")