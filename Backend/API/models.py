from pydantic import BaseModel
from typing import List

# Models
class Aufgabenschema(BaseModel):
    aussage1: str
    aussage2: str
    lösung: int
    feedback: str
    thema: str
    
class QuizSchema(BaseModel):
    bezeichnung: str
    themen: List[str]
    anzahl_aufgaben: int
    modus: str
    
class Quizzfragen(BaseModel):
    quizID: int
    aussageID: int

class Modi(BaseModel):
    name: str
    beschreibung: str
        
class Lehrer(BaseModel):
    lehrerID: int
    lehrerkennzahl: str

class TeilnehmerRequest(BaseModel):
<<<<<<< HEAD
    schuelernummer: int
=======
    name: str
>>>>>>> 2d5aeae22637f94b0c6ac790ab58b067309ef494
    klasse: str

class AntwortSchema(BaseModel):
    aufgabeID: int
    auswahl: int

class AntwortRequest(BaseModel):
    quizID: int
    teilnehmerID: int 
    antworten: List[AntwortSchema]
<<<<<<< HEAD
    
class ErgebnissSchema(BaseModel):
    schuelernummer: int
    klasse: str
    ergebnis: float
    
class ErgebnisRequest(BaseModel):
    quizID: int
    quizbezeichnung: str
    teilnehmer: List[ErgebnissSchema]
=======
>>>>>>> 2d5aeae22637f94b0c6ac790ab58b067309ef494
