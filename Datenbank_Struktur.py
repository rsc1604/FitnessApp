from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
import os

# Database connection
#DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:@localhost/fitnessappv33")


#connection_string = (
#    "mssql+pyodbc://"
#    "Sven:IEWeEiN!3Ch0A$@test123451.database.windows.net/Test"
#    "?driver=ODBC+Driver+18+for+SQL+Server"
#)
#engine = create_engine(connection_string, echo=True)
#SessionLocal = sessionmaker(bind=engine)
#try:
#    with engine.connect() as connection:
#        print("Connection successful!")
#except Exception as e:
#    print(f"Error: {e}")



Base = declarative_base()

class Gruppen(Base):
    __tablename__ = "Gruppen"
    id = Column(Integer, primary_key=True, autoincrement=True)
    beschreibung = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)

    mitglieder = relationship(
        "GruppenMitglieder",
        back_populates="gruppen",
        cascade="all, delete-orphan"
    )
    workouts = relationship(
        "GruppenWorkouts",
        back_populates="gruppen",
        cascade="all, delete-orphan"
    )

class GruppenMitglieder(Base):
    __tablename__ = "GruppenMitglieder"
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_gruppe = Column(Integer, ForeignKey("Gruppen.id"), nullable=False)
    id_user = Column(Integer, ForeignKey("AllUser.id"), nullable=False)

    gruppen = relationship("Gruppen", back_populates="mitglieder")
    AllUser = relationship("AllUser", back_populates="gruppen")

class GruppenWorkouts(Base):
    __tablename__ = "GruppenWorkouts"
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_workout = Column(Integer, ForeignKey("Workouts.id"), nullable=False)
    id_gruppe = Column(Integer, ForeignKey("Gruppen.id"), nullable=False)

    gruppen = relationship("Gruppen", back_populates="workouts")
    workouts = relationship("Workouts", back_populates="gruppen")

class Workouts(Base):
    __tablename__ = "Workouts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    duration = Column(Integer)
    calories = Column(Integer)
    addedby = Column(Integer, ForeignKey('AllUser.id'))

    # Relationship
    added_by_user = relationship("AllUser", back_populates="workouts")
    workout_exercises = relationship("WorkoutExercises", back_populates="workout")
    gruppen = relationship(
        "GruppenWorkouts",
        back_populates="workouts",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"Workout(id={self.id}, name={self.name}, duration={self.duration}, calories={self.calories}, addedby={self.addedby})"

class WorkoutExercises(Base):
    __tablename__ = "WorkoutExercises"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    workout_id = Column(Integer, ForeignKey('Workouts.id'), nullable=False)  # Umbenannt von workouts
    specific_exercise_id = Column(Integer, ForeignKey('SpecificExercises.id'), nullable=False)  # Umbenannt von spezific
    workoutexercises_count = Column(Integer, nullable=False)

    # Relationships to link with Workout and SpecificExercise tables
    workout = relationship("Workouts", back_populates="workout_exercises")  # Verweis auf die Beziehung zu Workouts
    specific_exercise = relationship("SpecificExercises", back_populates="workout_exercises")

    def __repr__(self):
        return f"WorkoutExercises(id={self.id}, workout_id={self.workout_id}, specificexercise_id={self.specific_exercise_id})"
 
class Exercises(Base):
    __tablename__ = "Exercises"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    addedby = Column(Integer, ForeignKey('AllUser.id'))

    # Relationship to link with AllUser table
    added_by = relationship("AllUser", back_populates="exercises")
    specific_exercises = relationship("SpecificExercises", back_populates="exercise", cascade="all, delete-orphan")


    def __repr__(self):
        return f"Exercise(id={self.id}, name={self.name}, addedby={self.addedby})"

class SpecificExercises(Base):
    __tablename__ = "SpecificExercises"

    id = Column(Integer, primary_key=True, index=True)
    id_exercise = Column(Integer, ForeignKey('Exercises.id'))
    sets = Column(Integer)
    reps = Column(Integer)
    weight = Column(Integer)
    addedby = Column(Integer, ForeignKey('AllUser.id'))

    # Relationship to link with Exercise and AllUser tables
    exercise = relationship("Exercises", back_populates="specific_exercises")
    added_by_u = relationship("AllUser", back_populates="specific_exercise")
    workout_exercises = relationship("WorkoutExercises", back_populates="specific_exercise", cascade="all, delete-orphan")

class AllUser(Base):
    __tablename__ = "AllUser"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(255), index=True)
    email = Column(String(255), index=True)
    password = Column(String(255), index=True)
    age = Column(Integer, index=True)
    weight = Column(Integer, index=True)
    gender = Column(String(255), index=True)

    exercises = relationship("Exercises", back_populates="added_by")
    workouts = relationship("Workouts", back_populates="added_by_user")
    specific_exercise = relationship("SpecificExercises", back_populates="added_by_u")
    gruppen = relationship(
        "GruppenMitglieder",
        back_populates="AllUser",
        cascade="all, delete-orphan"
    )
    rezepte = relationship("Rezepte", back_populates="koch")
    
    def __repr__(self):
        return f"User(id={self.id}, name={self.username}, email={self.email}, password={self.password} age={self.age}, weight={self.user}, gender={self.gender})"

class Rezepte(Base):
    __tablename__ = "Rezepte"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    rezept_name = Column(String(255))
    beschreibung = Column(String(255))
    creator_id = Column(Integer, ForeignKey('AllUser.id'))

    koch = relationship("AllUser", back_populates="rezepte",)


#Base.metadata.create_all(engine)
