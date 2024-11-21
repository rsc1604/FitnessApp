from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import bcrypt
from Datenbank_Struktur import *
import json
#from models import AllUser

#DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:@localhost/fitnessappv33")
connection_string = (
    "mssql+pyodbc://"
    "Sven:IEWeEiN!3Ch0A$@test123451.database.windows.net/Test"
    "?driver=ODBC+Driver+18+for+SQL+Server"
)
engine = create_engine(connection_string, echo=True)
SessionLocal = sessionmaker(bind=engine)


# rezept funktionen
def add_rezept(name: str, description: str, user_id: int) -> int:
    """Erstelle eine neue Gruppe und gibt die Id der Gruppe zurück"""
    with SessionLocal() as session:
        if not name or not description:
            raise ValueError("Name und Beschreibung dürfen nicht leer sein.")
        new_rezept = Rezepte(rezept_name=name, beschreibung=description, creator_id=user_id)
        try:
            session.add(new_rezept)
            session.commit()
            return new_rezept.id
        except Exception as e:
            session.rollback()
            raise ValueError(f"Fehler beim Hinzufügen der Gruppe: {e}")
        
def update_rezept(rez_id: int, new_name: str = None, new_description: str = None):
    """Ändert die Daten einer Gruppe"""
    with SessionLocal() as session:
        try:
            rez = session.query(Rezepte).filter(Rezepte.id == rez_id).one_or_none()
            if rez:
                if new_name:
                    rez.rezept_name = new_name
                if new_description:
                    rez.beschreibung = new_description
                session.commit()
        except Exception as e:
            session.rollback()
            raise ValueError(f"Fehler beim Aktualisieren der Gruppe: {e}")
        
def find_all_recipes_by_user(user_id: int):
    try:
        with SessionLocal() as session:
            recipes = session.query(Rezepte).filter(Rezepte.creator_id == user_id).all()
            return [{"id": recipe.id, "name": recipe.rezept_name} for recipe in recipes]  
    except Exception as e:
        print(f"Fehler beim Abrufen der Rezepte: {e}")
        return []
    
def find_all_recipes():
    try:
        with SessionLocal() as session:
            recipes = session.query(Rezepte).all()
            return [{"id": recipe.id, "name": recipe.rezept_name} for recipe in recipes]  
    except Exception as e:
        print(f"Fehler beim Abrufen der Rezepte: {e}")
        return []

def find_rezept(rez_id: int) -> dict:
    """Gibt den Namen und die Beschreibung eines Rezepts zurück."""
    with SessionLocal() as session:
        rez = session.query(Rezepte).filter(Rezepte.id == rez_id).one_or_none()
        if rez:
            return {"name": rez.rezept_name, "beschreibung": rez.beschreibung, "creator_id" : rez.creator_id}
        else:
            return {}




# Gruppen Funktionen
def add_group(name: str, description: str) -> int:
    """Erstelle eine neue Gruppe und gibt die Id der Gruppe zurück"""
    with SessionLocal() as session:
        if not name or not description:
            raise ValueError("Name und Beschreibung dürfen nicht leer sein.")
        new_group = Gruppen(name=name, beschreibung=description)
        try:
            session.add(new_group)
            session.commit()
            return new_group.id
        except Exception as e:
            session.rollback()
            raise ValueError(f"Fehler beim Hinzufügen der Gruppe: {e}")

def add_group_user(group_id: int, user_id: int) -> int:
    """Fügt ein Mitglied zu einer Gruppe und gibt die ID des Nutzers zurück"""
    with SessionLocal() as session:
        group = session.query(Gruppen).filter_by(id=group_id).one_or_none()
        if not group:
            raise ValueError(f"Gruppe mit ID {group_id} nicht gefunden.")
        new_member = GruppenMitglieder(id_gruppe=group_id, id_user=user_id)
        try:
            session.add(new_member)
            session.commit()
            return new_member.id
        except Exception as e:
            session.rollback()
            raise ValueError(f"Fehler beim Hinzufügen des Gruppenmitglieds: {e}")

def add_group_workout(group_id: int, workout_id: int) -> int:
    """Fügt ein Workout zu einer Gruppe und gibt die ID des Workouts zurük"""
    with SessionLocal() as session:
        group = session.query(Gruppen).filter_by(id=group_id).one_or_none()
        if not group:
            raise ValueError(f"Gruppe mit ID {group_id} nicht gefunden.")
        new_workout = GruppenWorkouts(id_gruppe=group_id, id_workout=workout_id)
        try:
            session.add(new_workout)
            session.commit()
            return new_workout.id
        except Exception as e:
            session.rollback()
            raise ValueError(f"Fehler beim Hinzufügen des Gruppenworkouts: {e}")

def del_group(group_id: int):
    """Löscht eine Gruppe und alle damit verbunden Daten"""
    with SessionLocal() as session:
        try:
            group_to_delete = session.query(Gruppen).filter(Gruppen.id == group_id).one_or_none()
            if group_to_delete:
                session.delete(group_to_delete)
                session.commit()
        except Exception as e:
            session.rollback()
            raise ValueError(f"Fehler beim Löschen der Gruppe: {e}")

def del_group_user(group_id: int, user_id: int):
    """Entfernt ein Mitglied aus einer Gruppe"""
    with SessionLocal() as session:
        try:
            member_to_delete = session.query(GruppenMitglieder).filter(
                GruppenMitglieder.id_gruppe == group_id,
                GruppenMitglieder.id_user == user_id
            ).one_or_none()
            if member_to_delete:
                session.delete(member_to_delete)
                session.commit()
        except Exception as e:
            session.rollback()
            raise ValueError(f"Fehler beim Löschen des Mitglieds: {e}")

def del_group_workout(group_id: int, workout_id: int):
    """Entfernt ein Workout aus einer Gruppe"""
    with SessionLocal() as session:
        try:
            workout_to_delete = session.query(GruppenWorkouts).filter(
                GruppenWorkouts.id_gruppe == group_id,
                GruppenWorkouts.id_workout == workout_id
            ).one_or_none()
            if workout_to_delete:
                session.delete(workout_to_delete)
                session.commit()
        except Exception as e:
            session.rollback()
            raise ValueError(f"Fehler beim Löschen des Workouts: {e}")

def find_groups_from_user(user_id: int) -> list[int]:
    """Findet alle Gruppen IDs für einen Nutzer und gibt diese in einer Liste zurück"""
    with SessionLocal() as session:
        groups = session.query(GruppenMitglieder).filter(GruppenMitglieder.id_user == user_id).all()
        return [group.id_gruppe for group in groups] if groups else []

def find_groups_from_workout(workout_id: int) -> list[int]:
    """Findet alle Gruppen IDs eines Workouts und gibt diese in einer Liste zurück"""
    with SessionLocal() as session:
        groups = session.query(GruppenWorkouts).filter(GruppenWorkouts.id_workout == workout_id).all()
        return [group.id_gruppe for group in groups] if groups else []

def update_group(group_id: int, new_name: str = None, new_description: str = None):
    """Ändert die Daten einer Gruppe"""
    with SessionLocal() as session:
        try:
            group = session.query(Gruppen).filter(Gruppen.id == group_id).one_or_none()
            if group:
                if new_name:
                    group.name = new_name
                if new_description:
                    group.beschreibung = new_description
                session.commit()
        except Exception as e:
            session.rollback()
            raise ValueError(f"Fehler beim Aktualisieren der Gruppe: {e}")

def find_users_of_group(group_id: int) -> list[int]:
    """Findet alle Mitglieder IDs für einer Gruppe und gibt diese in einer Liste zurück"""
    with SessionLocal() as session:
        groups = session.query(GruppenMitglieder).filter(GruppenMitglieder.id_gruppe == group_id).all()
        return [group.id_user for group in groups] if groups else []
    
def find_workouts_of_group(group_id: int) -> list[int]:
    """Findet alle Workout IDs für einer Gruppe und gibt diese in einer Liste zurück"""
    with SessionLocal() as session:
        groups = session.query(GruppenWorkouts).filter(GruppenWorkouts.id_gruppe == group_id).all()
        return [group.id_workout for group in groups] if groups else []

def find_group(group_id: int) -> dict:
    """Gibt den Namen und Die Beschreibung einer Gruppe zurück"""
    with SessionLocal() as session:
        groups = session.query(Gruppen).filter(Gruppen.id == group_id).one_or_none()
        return {"name" : groups.name, "bechreibung" : groups.beschreibung} if groups else []


# User Funktionen
def add_user(username: str, email: str, password: str, age: int, weight: int, gender: str):
    with SessionLocal() as session:
        if not all([username, email, password, age, weight, gender]):
            raise ValueError("Nicht alle Parameter ausgefüllt")

        temp = find_user_by_username(username)
        if temp != None:
            raise ValueError(f"user already exists")
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())    
        user = AllUser(
        username=username,
        email=email,
        password=hashed_password,
        age=age,
        weight=weight,
        gender=gender
)

    try:
        session.add(user)
        session.commit()
        return user.id
    except Exception as e:
        session.rollback()
        raise ValueError(f"Fehler beim Hinzufügem der Gruppe: {e}")
    
def find_user_by_username(username: str):
    """Gibt die Daten des Nutzers """
    with SessionLocal() as session:
        user_info = session.query(AllUser).filter(AllUser.username == username).one_or_none()
        if user_info:
            return {
            "id": user_info.id,
            "username": user_info.username,
            "email": user_info.email,
            "age": user_info.age,
            "weight": user_info.weight,
            "gender": user_info.gender,
            "password": user_info.password
            }
        return None

def find_user_by_userid(user_id: int):
    """Gibt die Daten des Nutzers """
    with SessionLocal() as session:
        user_info = session.query(AllUser).filter(AllUser.id == user_id).one_or_none()
        if user_info:
            return {
            "id": user_info.id,
            "username": user_info.username,
            "email": user_info.email,
            "age": user_info.age,
            "weight": user_info.weight,
            "gender": user_info.gender,
            "password": user_info.password
            }
        return None
# Exercise Funktionen
def add_exercise(name: str):
    if not all([name]):
        raise ValueError("Nicht alle Parameter ausgefüllt")
    
    with SessionLocal() as session:
        exercise = Exercises(
            name = name
        )
        try:
            session.add(exercise)
            session.commit()
        except ValueError as e:
            session.rollback()
            raise ValueError(f"could not create new workout: {e}") 

def add_specificexercise(id_exercise: int, sets: int, reps: int, weight: int, addedby: int):
    if not all([id_exercise, sets,reps, weight, addedby]):
        raise ValueError("Nicht alle Parameter ausgefüllt")
    
    with SessionLocal() as session:
        specificexercise = SpecificExercises(
            id_exercise = id_exercise,
            sets = sets,
            reps = reps,
            weight = weight,
            addedby = addedby
        )
        try:
            session.add(specificexercise)
            session.commit()
        except ValueError as e:
            session.rollback()
            raise ValueError(f"could not create new workout: {e}")

def find_specificexercisebyuseridandexerciseid(userid: int, exerciseid: int):
    with SessionLocal() as session:
        try:
            # Query SpecificExercises based on the user id and exercise id
            temp = session.query(SpecificExercises).filter(SpecificExercises.addedby == userid).filter(SpecificExercises.id_exercise == exerciseid).all()
            
            # Return a list of ids for the found specific exercises
            return temp
        
        except Exception as e:
            # Print the exception message for debugging purposes
            print(f"Fehler: {e}")
            return []  # Return an empty list in case of an error

def find_all_specific_exercises(userid: int):
    with SessionLocal() as session:
        try:
            exercises = session.query(SpecificExercises).filter(SpecificExercises.addedby == userid).all()
            results = [
                {
                    "id": exercise.id,
                    "sets": exercise.sets,
                    "reps": exercise.reps,
                    "weight": exercise.weight,
                    "addedby": exercise.addedby,
                    "id_exercise": exercise.id_exercise
                }
                for exercise in exercises
            ]
            
            return results
        except Exception as e:
            print(f"Fehler beim Abrufen der spezifischen Übungen: {e}")
            return []

def find_exercise_details_by_id(spez_exercise_id: int):
    """Findet die Details einer spezifischen Übung basierend auf ihrer ID."""
    try:
        with SessionLocal() as session:
            exercise = session.query(SpecificExercises).filter(SpecificExercises.id == spez_exercise_id).first()
            print(exercise)
            print(exercise.weight)
            if exercise:
                return {
                    "id": exercise.id,
                    "sets": exercise.sets,
                    "reps": exercise.reps,
                    "weight": exercise.weight,
                    "addedby": exercise.addedby
                }
            else:
                print(f"Keine Übung mit der ID {spez_exercise_id} gefunden.")
                return {}
    except Exception as e:
        print(f"Fehler bei der Abfrage der Übung: {e}")
        return {}

def update_specificexercise(id: int, sets: int, reps: int, weight: int):

    with SessionLocal() as session:
        try:
            specificexercise = session.query(SpecificExercises).filter(SpecificExercises.id == id).first()
            if not specificexercise:
                raise ValueError(f"Übung mit der ID {id} wurde nicht gefunden.")

            if sets is not None:
                specificexercise.sets = sets
            if reps is not None:
                specificexercise.reps = reps
            if weight is not None:
                specificexercise.weight = weight

            session.commit()
            print(f"Übung mit der ID {id} erfolgreich aktualisiert.")
        
        except Exception as e:
            session.rollback()
            raise ValueError(f"Fehler beim Aktualisieren der Übung: {e}")

def delete_specificexercise(exercise_id, user_id):
    try:
        with SessionLocal() as session:
            # Finde die Übung, die gelöscht werden soll
            exercise = session.query(SpecificExercises).filter(
                SpecificExercises.id == exercise_id, 
                SpecificExercises.addedby == user_id
            ).first()

            if exercise:
                session.delete(exercise)
                session.commit()
                return True
            else:
                print(f"Übung mit der ID {exercise_id} wurde nicht gefunden.")
                return False
    except Exception as err:
        print(f"Fehler beim Löschen der Übung: {err}")
        return False


# Workout Funktionen
def add_workout(workoutname: str, specificexercises: list[int], duration: int, calories: int, addedby: int):
    if not all([workoutname, duration, calories]):
        raise ValueError("Nicht alle Parameter ausgefüllt")
    
    with SessionLocal() as session:
        workout = Workouts(
            name = workoutname,
            duration = duration,
            calories = calories,
            addedby = addedby
        )
        try:
            session.add(workout)
            session.commit()
            id = workout.id
        except ValueError as e:
            session.rollback()
            raise ValueError(f"could not create new workout: {e}")
    
    counter = 0
    
    for i in range(len(specificexercises)):
        counter +=1
        createworkoutexercises(id, specificexercises[i], counter)
                
def del_workout(workout_id: int):
    with SessionLocal() as session:
        try:
            workout_exercises = session.query(workout_exercise).filter(workout_exercise.workout_id == workout_id).all()
    
            if workout_exercises:
                for workout_exercise in workout_exercises:
                    session.delete(workout_exercise)
                    session.commit()
                    print(f"Alle Übungen des Workouts mit ID {workout_id} wurden erfolgreich gelöscht.")
            else:
                print(f"Es wurden keine Übungen für das Workout mit ID {workout_id} gefunden.")
    
                workout = session.query(workout).filter(workout.workout_id == workout_id).first()
    
                if workout:
                    session.delete(workout)
                    session.commit()
                    print(f"Workout mit der ID {workout_id} erfolgreich gelöscht.")
                else:
                    print(f"Kein Workout mit der ID {workout_id} gefunden.")
    
        except Exception as err:
                print(f"Fehler beim Löschen des Workouts: {err}")
    session.rollback() 

def createworkoutexercises(workout_id: int, specific_exercises_id: int, workoutexercises_count: int):
    # Check if all required parameters are provided
    if not all([workout_id, specific_exercises_id, workoutexercises_count]):
        raise ValueError("Nicht alle Parameter ausgefüllt")
    
    # Start a session
    with SessionLocal() as session:
        
        # Create the workout exercise entry
        workoutexercises = WorkoutExercises(
            workout_id=workout_id,
            specific_exercise_id=specific_exercises_id,
            workoutexercises_count=workoutexercises_count
        )
        
        try:
            # Add the new record to the session and commit
            session.add(workoutexercises)
            session.commit()
            #return createworkoutexercises.id
        except ValueError as e:
            # Rollback in case of error (e.g., foreign key constraint violation)
            session.rollback()
            raise ValueError(f"Could not create new workout exercise due to integrity error: {e}")

def find_all_workouts_by_user(user_id: int):
    try:
        with SessionLocal() as session:
            print(f"Such nach Workouts für user_id: {user_id}")

            workouts = session.query(Workouts).filter(Workouts.addedby == user_id).all()

            if not workouts:
                print(f"Keine Workouts für Benutzer mit der ID {user_id} gefunden.")
            else:
                print(f"Gefundene Workouts: {len(workouts)}")

            results = []
            for workout in workouts:
                try:
                    workout_dict = {
                        "id": str(workout.id), 
                        "name": workout.name,  
                        "duration": str(workout.duration),  
                        "calories": str(workout.calories), 
                        "addedby": str(workout.addedby)  
                    }
                    results.append(workout_dict)
                except Exception as e:
                    print(f"Fehler beim Verarbeiten des Workouts {workout.id}: {e}")
                    continue

            return results
    except Exception as e:
        print(f"Fehler beim Abrufen der Workouts: {e}")
        return []


def get_workout_by_id(workout_id: int):
    try:
        with SessionLocal() as session:
            print(f"Suche nach Workout mit der ID: {workout_id}")

            workout = session.query(Workouts).filter(Workouts.id == workout_id).first()

            if not workout:
                print(f"Kein Workout mit der ID {workout_id} gefunden.")
                return None
            else:
                print(f"Gefundenes Workout: {workout.name}")

            workout_dict = {
                "id": str(workout.id),
                "name": workout.name,
                "duration": str(workout.duration),
                "calories": str(workout.calories),
                "addedby": str(workout.addedby)
            }

            return workout_dict
    except Exception as e:
        print(f"Fehler beim Abrufen des Workouts mit ID {workout_id}: {e}")
        return None


          
# Exercise Funktionen
def find_exercise_by_id(exercise_id: int):
    print(f"Suche nach Übung mit ID: {exercise_id}")  
    with SessionLocal() as session:
        try:
            exercise = session.query(Exercises).filter(Exercises.id == exercise_id).first()
            print(f"Gefundene Übung: {exercise}")  

            if exercise is None:
                print(f"Keine Übung mit der ID {exercise_id} gefunden.")
                return None
            
            return {
                "id": exercise.id,
                "name": exercise.name
            }

        except Exception as err:
            print(f"Fehler bei der Suche der Übung: {err}")
            return None




def find_exercise_by_name(name: str):
    with SessionLocal as session:
        try:
            exercise = session.query(Exercises).filter(Exercises.name == name).first()
            
            if exercise is None:
                print(f"Keine Übung mit dem Namen '{name} gefunden.")
                return None
            return exercise
        
        except Exception as err:
            print(f"Fehler bei der Suche der Üubung: {err}")
            return None

def find_all_exercises():
    """Gibt alle Übungen aus der Datenbank zurück."""
    with SessionLocal() as session:
        try:
            exercises = session.query(Exercises).all()

            if not exercises:
                print("Es wurden keine Übungen gefunden.")
                return []

            return [{"id": exercise.id, "name": exercise.name} for exercise in exercises]

        except Exception as err:
            print(f"Fehler bei der Suche der Übungen: {err}")
            return []

def del_Exercise(exercise_id: int):
    with SessionLocal() as session:
        try:
            exercise = session.query(Exercises).filter(Exercises.exercise_id == exercise_id).first()
    
            if exercise is None:
                print(f"Keine Übung mit der ID {exercise_id} gefunden.")
                return f"Keine Übung mit der ID {exercise_id} gefunden."
            
            session.delete(exercise)
            session.commit()
    
            print(f"Übung mit der ID {exercise_id} erfolgreich gelöscht.")
            return f"Übung mit der ID {exercise_id} erfolgreich gelöscht."
        
        except Exception as err:
            print(f"Fehler beim Löschen der Übung: {err}")
            session.rollback()
            return f"Fehler beim Löschen der Übung: {err}"

def return_exercise_all_by_input(input: str):
    print("INPUT: " + input)
    with SessionLocal() as session:
        try:
            exercises = session.query(Exercises).filter(Exercises.name.ilike(f"{input}%")).all()

            if exercises:
                all_exercises = [{
                    "id": e.id,  
                    "name": e.name  
                } for e in exercises]
                
                return all_exercises
            else:
                return "..."
        except Exception as e:
            print(f"Fehler beim Abrufen der Übungen: {e}")
            return []


# Login Funktionen
def update_password_in_database(username: str, new_password: str):
    with SessionLocal() as session:
        try:
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), salt).decode('utf-8')
            user = session.query(AllUser).filter(AllUser.username == username).first()

            if user:
                user.password_hash = hashed_password
                session.commit()
                print(f"Passwort für Benutzer '{username}' wurde erfolgreich geändert.")
                return True
            else:
                print(f"Benutzer '{username}' existiert nicht.")
                return False

        except Exception as e:
            print(f"Fehler: {e}")
            session.rollback()
            return False

def login_user(username: str, password: str):
    with SessionLocal() as session:
    
        try:
            user = session.query(AllUser).filter(AllUser.username == username).first()

            if user is None:
                print("Benutzer mit diesem Username existiert nicht.")
                return "Benutzer mit diesem Username existiert nicht."
            
            if bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
                print(f"Login erfolgreich! Willkommen, Username: {username}")
                return True
            else:
                print("Falsches Passwort.")
                return "Falsches Passwort"
        
        except Exception as err:
            print(f"Fehler bei der Datenbankabfrage: {err}")
            return f"Fehler bei der Datenbankabfrage: {err}"
 
 
def compare_users_in_exercise(user1_id: int, user2_id: int, exercise: int):
    with SessionLocal() as session:
        try:
            # Überprüfe, ob Benutzer-IDs Ganzzahlen sind
            if not isinstance(user1_id, int) or not isinstance(user2_id, int):
                return "Benutzer-IDs müssen Ganzzahlen (int) sein."

            # Hole die Übung
            if isinstance(exercise, str):  
                exercise_obj = session.query(Exercises).filter(Exercises.name == exercise).first()
                if exercise_obj:
                    exercise = exercise_obj.id
                else:
                    return f"Übung mit dem Namen {exercise} wurde nicht gefunden."

            # Hole Benutzerobjekte anhand der ID
            user1_obj = session.query(AllUser).filter(AllUser.id == user1_id).first()
            user2_obj = session.query(AllUser).filter(AllUser.id == user2_id).first()

            if not user1_obj or not user2_obj:
                return "Benutzer nicht gefunden."

            user1 = user1_obj.username
            user2 = user2_obj.username

            # Abfrage der spezifischen Übungen
            user1_AllSpezEx = session.query(SpecificExercises).filter(SpecificExercises.addedby == user1_id).filter(SpecificExercises.id_exercise == exercise).all()
            user2_AllSpezEx = session.query(SpecificExercises).filter(SpecificExercises.addedby == user2_id).filter(SpecificExercises.id_exercise == exercise).all() 
            
            if not user1_AllSpezEx or not user2_AllSpezEx:
                return f"Vergleich nicht möglich, da keine Übungen bei beiden Benutzern gefunden wurden."
            
            # Berechnung der höchsten Punktzahl für Benutzer 1
            highest_score_user1 = 0
            for i in user1_AllSpezEx:
                wert = i.weight * i.reps * i.sets
                if wert > highest_score_user1:
                    highest_score_user1 = wert

            highest_score_user2 = 0	
            for i in user2_AllSpezEx:
                wert = i.weight * i.reps * i.sets
                if wert > highest_score_user2:
                    highest_score_user2 = wert

            uebungsname = session.query(Exercises).filter(Exercises.id == exercise).first().name

            if highest_score_user1 > highest_score_user2:
                return f"{uebungsname}\n {user1}: {highest_score_user1} Punkte\n {user2}: {highest_score_user2} Punkte\n {user1} hat die höhere Punktzahl."
            elif highest_score_user1 < highest_score_user2:
                return f"{uebungsname}\n {user1}: {highest_score_user1} Punkte\n {user2}: {highest_score_user2} Punkte\n {user2} hat die höhere Punktzahl."
            else:
                return f"Beide haben {highest_score_user1} Punkte erreicht!!!"
        
        except Exception as e:
            return f"Fehler beim Abrufen der spezifischen Übungen: {str(e)}"

            
 
def find_common_exercises(user_1_id: int, user_2_id: int):
    with SessionLocal() as session:
        try:
            
            print(user_1_id)
            print(user_2_id)
            
            user1_exercises = session.query(SpecificExercises).filter(SpecificExercises.addedby == user_1_id).all()
            user2_exercises = session.query(SpecificExercises).filter(SpecificExercises.addedby == user_2_id).all()
            
            user1_spezexercise_ids = [exercise.id_exercise for exercise in user1_exercises]
            user2_spezexercise_ids = [exercise.id_exercise for exercise in user2_exercises]
            
            common_exercises = []
            
            for exercise in user1_spezexercise_ids:
                for exercise2 in user2_spezexercise_ids:
                    if exercise == exercise2:
                        dic ={
                            "id": exercise,
                            "name": session.query(Exercises).filter(Exercises.id == exercise).first().name
                        }
                        common_exercises.append(dic)
                        
            return common_exercises
        except:
            return "Fehler beim Abrufen der spezifischen Übungen"    
            
            
            
    
    

# Export / Import
def export_users_as_json(path: str = "users.json"):
    with SessionLocal() as sessions:
        users = sessions.query(AllUser).all()
        users_data = [user.__dict__ for user in users]
        for user in users_data:
            user.pop("_sa_instance_state", None)
        with open(path, "w", encoding="utf-8") as users_file:
            json.dump(users_data, users_file, ensure_ascii=False, indent=4)        

def import_user_as_json(path: str = "users.json"):
    try:
        with open(path, "r", encoding="utf-8") as users_file:
            users_data = json.load(users_file)

        with SessionLocal as session:
            for user_data in users_data:
                user_data.pop("_sa_insatnce_state", None)
                user = AllUser(**user_data)
                session.add(user)
            session.commit()
        print(f"Erfolgreich {len(user_data)} Benutzer aus {path} importiert.")
    	
    except Exception as e:
        print(f"Fehler beim Importieren der Bentzer: {e}")
