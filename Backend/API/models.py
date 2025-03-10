from pydantic import BaseModel
from typing import List

# Models
class Aufgabenschema(BaseModel):
    aussage1: str
    aussage2: str
    lösung: int
    feedback: str
    thema: str
    
class UpdateAufgabe(BaseModel):
    aufgabe_id: int
    aufgabenschema: Aufgabenschema  
      
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
    schuelernummer: int
    klasse: str

class AntwortSchema(BaseModel):
    aufgabeID: int
    auswahl: int

class AntwortRequest(BaseModel):
    quizID: int  # quizID wird im Request-Body erwartet
    teilnehmerID: int  # teilnehmerID wird im Request-Body erwartet
    antworten: List[AntwortSchema]
    
class ErgebnissSchema(BaseModel):
    schuelernummer: int
    klasse: str
    ergebnis: float
    
class ErgebnisRequest(BaseModel):
    quizID: int
    quizbezeichnung: str
    teilnehmer: List[ErgebnissSchema]
