from fastapi import FastAPI, HTTPException, Depends, Query, Path
from typing import List
from sqlite3 import Connection
from crud import (
    get_all_aufgaben,
    get_lehrerkennzahl,
    get_aufgaben_by_thema,
    add_aufgabe_to_quiz,
    get_all_themen,
    get_all_modis,
    get_quiz_with_fragen,
    create_new_thema,
    create_new_aufgabe,
    create_quiz,
    update_aufgabe
)
from database import get_db_connection

# FastAPI-App
app = FastAPI()

# Teste die Datenbankverbindung
@app.get("/test-connection")
def test_connection(db: Connection = Depends(get_db_connection)):
    try:
        get_all_aufgaben(db)
        return {"status": "success", "message": "Database connection is working!"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Überprüft die Lehrerkennzahl
@app.get("/lehrer/")
def check_lehrerkennzahl(lehrerkennzahl: str, db: Connection = Depends(get_db_connection)):
    result = get_lehrerkennzahl(lehrerkennzahl, db)
    return {"status": "success", "data": result}

# Liste alle Aufgaben von jeweiligen Themen auf
@app.get("/aufgaben/")
def get_aufgaben(db: Connection = Depends(get_db_connection)):
    try:
        aufgaben = get_aufgaben_by_thema(db)
        return {"status": "success", "data": aufgaben}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

#Listet den gebauten Quiz mit den zufälligen Aufgaben
@app.get("/quiz/{quizID}")
def get_quiz(quizID: int, db: Connection = Depends(get_db_connection)):
    try:
        quiz = get_quiz_with_fragen(quizID, db)
        return {"status": "success", "data": quiz}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

#Listet alle Aufgaben vom jeweiligem Thema
@app.get("/aufgaben/{thema_name}")
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

# Neue Thema erstellen
@app.post("/themen/")
def post_new_thema(themaName: str, db: Connection = Depends(get_db_connection)):
    result = create_new_thema(themaName, db)
    return result

# Erstelle neue Aufgabe
@app.post("/aufgaben/")
def post_new_aufgabe(
    aussage1: str,
    aussage2: str, 
    lösung: int, 
    feedback: str, 
    thema: str = Query(..., description="Bitte wählen Sie ein Thema aus", enum=get_all_themen(get_db_connection())), 
    db: Connection = Depends(get_db_connection)
):
    result = create_new_aufgabe(aussage1, aussage2, lösung, feedback, thema, db)
    return {"data": result}
    
# Erstelle Quiz
@app.post("/quiz/")
def create_new_quiz(
    freigabelink: str,
    themen: List[str] = Query(..., description="Liste der Themen, aus denen Aufgaben ausgewählt werden sollen."),
    anzahl_aufgaben: int = Query(..., description="Anzahl der Aufgaben im Quiz."),
    modus: str = Query(..., description="Bitte wählen Sie ein Modi aus", enum=get_all_modis(get_db_connection())), 
    db: Connection = Depends(get_db_connection)
):
    try:
        # Erstelle ein neues Quiz
        quizID = create_quiz(freigabelink, modus, db)
        
        # Füge Fragen zum Quiz hinzu
        add_aufgabe_to_quiz(quizID, themen, anzahl_aufgaben, db)
        
        return {"status": "success", "quizID": quizID}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")    

# Aktualisieren einer Aufgabe
@app.put("/aufgaben/{aufgabe_id}")
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
    
