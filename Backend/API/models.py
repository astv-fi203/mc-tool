from pydantic import BaseModel
from typing import Literal

# Models
class Aufgaben(BaseModel):
    aussage1: str
    aussage2: str
    lösung: int
    feedback: str
    
    def aktualisiereaussage(self, newAussagetext):
        self.aussgetext = newAussagetext

class Antwort(BaseModel):
    antwortID: int
    aussageID: int
    antwortText: str
    isKorrekt: bool
    
class Thema(BaseModel):
    themaID: int
    themaName: str
    
class Quiz(BaseModel):
    quizID: int
    freigabelink: str
    erstelldatum: str
    modiID: int
    
    def generiereQuiz(): 
        list[Thema]
    
class Quizzfragen(BaseModel):
    quizID: int
    aussageID: int

class Modi(BaseModel):
        modiID: int
        name: str
        beschreibung: str
        
class Lehrer(BaseModel):
    lehrerID: int
    lehrerkennzahl: str

class Feedback(BaseModel):
    feedbackID: int
    feedbackText: str
    auswahlNR: str
    
