from sqlalchemy import Column, Integer, String, Float
from database import db

class Students(db):
    __tablename__ = 'students'

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(50), index=True)
    subject_name = Column(String(50), index=True)
    semester_number = Column(Integer)
    grade = Column(Float)
    start_year = Column(Integer)
    age = Column(Integer)
