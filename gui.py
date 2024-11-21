import customtkinter as ctk
from tkinter import messagebox
import time
#import Python_Skript.ConnectDatenbankold as ConnectDatenbankold
import operations as do
import GUI_Gruppen as uig
import GUI_Workout as wkt
import sendEmail 
import GUI_Rezepte



ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")
#connection = ConnectDatenbankold.connect_to_database()


def clear_frame(frame):
    """Löscht alle Widgets im Frame"""
    for widget in frame.winfo_children():
        widget.destroy()

def show_text_animated(frame, text, row, column, delay=100, callback=None):
    """Zeigt den Text animiert an."""
    label = ctk.CTkLabel(frame, text="", font=("Arial", 20))  
    label.grid(row=row, column=column, sticky="w", pady=5)

    def update_text(i=0):
        if i < len(text):
            label.configure(text=text[:i + 1]) 
            frame.after(delay, update_text, i + 1)
        elif callback:
            time.sleep(1)
            callback()

    update_text()

def ask_user_questions(frame, user_data, root):
    """Fragen an den Benutzer stellen."""
    questions = [
        ("Wie alt bist du?", "int"),
        ("Welchem Geschlecht gehörst du an?", "gender"),
        ("Wie viel wiegst du? (in kg)", "int")
    ]

    user_answers = {}
    
    def ask_question(index=0):
        if index < len(questions):
            question, q_type = questions[index]

            question_label = ctk.CTkLabel(frame, text=question, font=("Arial", 14))  
            question_label.grid(row=2, column=0, sticky="w", pady=10)

            if q_type == "int":
                answer_entry = ctk.CTkEntry(frame, font=("Arial", 12), width=250)
                answer_entry.grid(row=3, column=0, pady=5)
            elif q_type == "gender":
                gender_var = ctk.StringVar()
                gender_var.set("Bitte wählen")  

                gender_menu = ctk.CTkOptionMenu(frame, variable=gender_var, values=["Männlich", "Weiblich", "Divers"])
                gender_menu.set("Bitte wählen")
                gender_menu.grid(row=3, column=0, pady=5)
                answer_entry = gender_menu  

            def next_question():
                if q_type == "int":
                    try:
                        answer = int(answer_entry.get())
                        user_answers[question] = answer
                    except ValueError:
                        messagebox.showwarning("Fehler", f"Ungültige Eingabe für {question}. Bitte geben Sie eine gültige Zahl ein.")
                        return
                elif q_type == "gender":
                    answer = gender_var.get()
                    if answer == "Bitte wählen":
                        messagebox.showwarning("Fehler", f"Ungültige Eingabe für {question}. Bitte wählen Sie eine Option.")
                        return
                    user_answers[question] = answer

                question_label.destroy()
                answer_entry.grid_forget()

                ask_question(index + 1)

            next_button = ctk.CTkButton(frame, text="Weiter", font=("Arial", 12), command=next_question)
            next_button.grid(row=4, column=0, pady=10)

        else:
            clear_frame(frame)
            finish_button = ctk.CTkButton(frame, text="Fertig", font=("Arial", 12), command=lambda: finish(user_answers, frame, user_data, root))
            finish_button.grid(row=5, column=0, pady=10)

    ask_question()

def finish(user_answers, frame, user_data, root):
    """Druckt die Antworten des Benutzers und zeigt die Startseite."""
    print("\nFertig mit der Anpassung!")
    counter = 0

    for question, answer in user_answers.items():
        print(f"{question}: {answer}")
        if counter == 0:
            age = answer
            counter += 1
        elif counter == 1:
            gender = answer
            counter += 1
        elif counter == 2:
            wieght = answer

    try:       
        do.add_user(user_data["username"], user_data["email"], user_data["password_hash"], int(age), int(wieght), str(gender))  
    except ValueError as e:
        messagebox.showwarning("Fehler", e)

    window_home(frame, user_data, root)  
            

def window_user_info(frame, user_data, root):
    """Zeigt die Benutzerinfo und fordert den Benutzer auf, Fragen zu beantworten."""
    clear_frame(frame)
    welcome_text = f"Herzlich Willkommen {user_data['username']}!"
    show_text_animated(frame, welcome_text, row=1, column=0, delay=100, callback=lambda: ask_user_questions(frame, user_data, root))

def register_user(frame, username_entry, email_entry, password_entry, confirm_password_entry, root):
    """Registriert einen neuen Benutzer."""
    username = username_entry.get()
    email = email_entry.get()
    password = password_entry.get()
    confirm = confirm_password_entry.get()

    if not username or not email or not password or not confirm:
        messagebox.showwarning("Fehler", "Alle Felder müssen ausgefüllt sein!")
        return
    if "@" not in email:
        messagebox.showwarning("Fehler", "Keine gültige Email!")
        return
    if len(password) < 5:
        messagebox.showwarning("Fehler", "Das Passwort muss mindestens 5 Zeichen lang sein!")
        return
    if password != confirm:
        messagebox.showwarning("Fehler", "Passwort und Bestätigung stimmen nicht überein!")
        return

    user_data = {
        "username": username,
        "password_hash": password,
        "email": email
    }

    print("User registered:", user_data)
    sendEmail.send_email(user_data["email"], user_data["username"])
    window_user_info(frame, user_data, root)

def login_user(frame, username_entry, password_entry, root):
    """Meldet den Benutzer an und überprüft die Eingabedaten."""
    username = username_entry.get()
    password = password_entry.get()

    login_result = do.login_user(username, password)

    if login_result != True:
        messagebox.showwarning("Fehler", login_result)
        username_entry.delete(0, ctk.END)
        password_entry.delete(0, ctk.END)
        return  

    user_info = do.find_user_by_username(username)
    print("User logged in:", user_info)

    clear_frame(frame)
    welcome_text = f"Willkommen zurück, {user_info['username']}!"
    show_text_animated(frame, welcome_text, row=1, column=0, delay=100, callback=lambda: window_home(frame, user_info, root))

def window_login(frame, root):
    """Zeigt das Login-Fenster."""
    clear_frame(frame)

    ctk.CTkLabel(frame, text="Login", font=("Arial", 20, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

    username_label = ctk.CTkLabel(frame, text="Username", font=("Arial", 12))
    username_label.grid(row=1, column=0, sticky="w", pady=5)
    username_entry = ctk.CTkEntry(frame, font=("Arial", 12), width=250)
    username_entry.grid(row=1, column=1, pady=5)

    password_label = ctk.CTkLabel(frame, text="Password", font=("Arial", 12))
    password_label.grid(row=2, column=0, sticky="w", pady=5)
    password_entry = ctk.CTkEntry(frame, show="*", font=("Arial", 12), width=250)
    password_entry.grid(row=2, column=1, pady=5)

    login_button = ctk.CTkButton(frame, text="Login", font=("Arial", 12), command=lambda: login_user(frame, username_entry, password_entry, root))
    login_button.grid(row=3, column=0, columnspan=2, pady=15)

    root.bind("<Return>", lambda event: login_user(frame, username_entry, password_entry, root))

    register_button = ctk.CTkButton(frame, text="Don't have an account? Register here", font=("Arial", 10), command=lambda: window_register(frame, root))
    register_button.grid(row=4, column=0, columnspan=2, pady=5)

def window_register(frame, root):
    """Zeigt das Registrierungs-Fenster."""
    clear_frame(frame)

    ctk.CTkLabel(frame, text="Register", font=("Arial", 20, "bold"), text_color="#333").grid(row=0, column=0, columnspan=2, pady=10)

    username_label = ctk.CTkLabel(frame, text="Username", font=("Arial", 12))
    username_label.grid(row=1, column=0, sticky="w", pady=5)
    username_entry = ctk.CTkEntry(frame, font=("Arial", 12), width=250)
    username_entry.grid(row=1, column=1, pady=5)

    email_label = ctk.CTkLabel(frame, text="E-Mail", font=("Arial", 12))
    email_label.grid(row=2, column=0, sticky="w", pady=5)
    email_entry = ctk.CTkEntry(frame, font=("Arial", 12), width=250)
    email_entry.grid(row=2, column=1, pady=5)

    password_label = ctk.CTkLabel(frame, text="Password", font=("Arial", 12))
    password_label.grid(row=3, column=0, sticky="w", pady=5)
    password_entry = ctk.CTkEntry(frame, show="*", font=("Arial", 12), width=250)
    password_entry.grid(row=3, column=1, pady=5)

    confirm_password_label = ctk.CTkLabel(frame, text="Confirm Password", font=("Arial", 12))
    confirm_password_label.grid(row=4, column=0, sticky="w", pady=5)
    confirm_password_entry = ctk.CTkEntry(frame, show="*", font=("Arial", 12), width=250)
    confirm_password_entry.grid(row=4, column=1, pady=5)

    register_button = ctk.CTkButton(frame, text="Register", font=("Arial", 12), command=lambda: register_user(frame, username_entry, email_entry, password_entry, confirm_password_entry, root))
    register_button.grid(row=5, column=0, columnspan=2, pady=15)

    root.bind("<Return>", lambda event: register_user(frame, username_entry, email_entry, password_entry, confirm_password_entry, root))

def setting_menu(full_screen_frame, user_info):
    settings_options = ["Erscheinungsbild", "Account", "LogOut"]
    appearance_var = ctk.StringVar(value="Settings")

    settings_menu = ctk.CTkOptionMenu(
        full_screen_frame,
        variable=appearance_var,
        values=settings_options,
        command=lambda selected_option: on_appearance_option_selected(selected_option, user_info)
    )
    settings_menu.grid(row=0, column=0, pady=10, padx=20, sticky="nw")
    
def window_home(frame, user_data, root):
    """Zeigt die Startseite des Programms."""
    clear_frame(frame)  

    user_info = do.find_user_by_username(user_data["username"])

    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    full_screen_frame = ctk.CTkFrame(root)
    full_screen_frame.grid(row=0, column=0, sticky="nsew")

    full_screen_frame.grid_rowconfigure(0, weight=1)
    full_screen_frame.grid_columnconfigure(0, weight=1)

    welcome_label = ctk.CTkLabel(full_screen_frame, text=f"Willkommen, {user_info['username']}!", font=("Arial", 20))
    welcome_label.grid(row=0, column=0, pady=20)

    setting_menu(full_screen_frame, user_info)    
    
    sidebar_frame = ctk.CTkFrame(root, width=200, fg_color="#202020")
    sidebar_frame.grid(row=0, column=1, sticky="ns")

    sidebar_frame.grid_rowconfigure(0, weight=1)
    sidebar_frame.grid_rowconfigure(1, weight=1)
    sidebar_frame.grid_rowconfigure(2, weight=1)
    sidebar_frame.grid_rowconfigure(3, weight=1)

    button1 = ctk.CTkButton(sidebar_frame, text="Freunde & Gruppen", command=lambda: change_frame(0,full_screen_frame, user_info))
    button1.grid(row=0, column=0, pady=10, padx=20, sticky="ew")

    button2 = ctk.CTkButton(sidebar_frame, text="Rezepte & Ernährung", command=lambda: change_frame(1,full_screen_frame, user_info))
    button2.grid(row=1, column=0, pady=10, padx=20, sticky="ew")

    button3 = ctk.CTkButton(sidebar_frame, text="Übungen", command=lambda: change_frame(2,full_screen_frame, user_info))
    button3.grid(row=2, column=0, pady=10, padx=20, sticky="ew")

    button4 = ctk.CTkButton(sidebar_frame, text="Workouts", command=lambda: change_frame(3,full_screen_frame, user_info))
    button4.grid(row=3, column=0, pady=10, padx=20, sticky="ew")
    
    
    
def change_frame(reiter,frame, user_info):
        """Ändert den Inhalt des Frames je nach dem ausgewählten Reiter."""
        clear_frame(frame)

        if reiter == 0:
            gruppen(frame, user_info)
        elif reiter == 1:
            display_reiter_2(frame, user_info)
        elif reiter == 2:
            display_reiter_3(frame, user_info)
        elif reiter == 3:
            display_reiter_4(frame, user_info)
            


 


def display_reiter_2(frame, user_info):
    """Zeigt den Inhalt von Rezepte / Ernährung."""
    GUI_Rezepte.rezepte_window(frame, user_info, root)    

def update_textframe(user_info):
        textbox_uebung.configure(state="normal")
        textbox_uebung.delete("1.0", ctk.END)
        user_info = do.find_user_by_username(user_info["username"])
        uebung_text = "Übungen:\n" 
        uebung_text += "-" * 30 + "\n"  

        exercises = do.find_all_exercises()
        for exercise in exercises:
            uebung_text += f"ID: {exercise['id']}\t | Name: {exercise['name']}\n"
            
        textbox_uebung.insert("1.0", uebung_text)
        textbox_uebung.configure(state="disabled")


        textbox_rechts.configure(state="normal")
        textbox_rechts.delete("1.0", ctk.END)
        specific_exercise_text = "Spezifische Übungen:\n"
        specific_exercise_text += "-" * 50 + "\n"

        specific_exercises = do.find_all_specific_exercises(user_info["id"])
        
        for exercise in specific_exercises:
            print(int(exercise["id_exercise"]))
            name_uebung = do.find_exercise_by_id(int(exercise['id_exercise']))
            
            if name_uebung is None:
                specific_exercise_text += (f"ID: {exercise['id']}\t | "
                                        f"Name: Übung nicht gefunden\t\t | "
                                        f"Wiederholungen: {exercise['reps']}\t | "
                                        f"Sätze: {exercise['sets']}\t | "
                                        f"Gewicht: {exercise['weight']} kg\n")
            else:
                specific_exercise_text += (f"ID: {exercise['id']}\t | "
                                        f"Name: {name_uebung['name']}\t\t | "
                                        f"Wiederholungen: {exercise['reps']}\t | "
                                        f"Sätze: {exercise['sets']}\t | "
                                        f"Gewicht: {exercise['weight']} kg\n")

                    

        textbox_rechts.insert("1.0", specific_exercise_text)
        textbox_rechts.configure(state="disabled")

def search_in_textframe(event, input_field, user_info):
    uebung_text_1 = "Übungen:\n" 
    uebung_text_1 += "-" * 30 + "\n"  
    user_input = input_field.get()
    print(user_input + "!!!!!")
    exercises = do.return_exercise_all_by_input(str(user_input))
    
    if exercises is None:
        exercises = []
    textbox_uebung.configure(state="normal")
    textbox_uebung.delete("1.0", ctk.END)

    for exercise in exercises:
        uebung_text_1 += f"ID: {int(exercise['id'])}\t | Name: {exercise['name']}\n"

    textbox_uebung.insert("1.0", uebung_text_1)
    textbox_uebung.configure(state="disabled")

def display_reiter_3(frame,user_info):
    """Zeigt den Inhalt von Übungen."""
    label = ctk.CTkLabel(frame, text="Übungen", font=("Arial", 20))
    label.grid(row=0, column=0, pady=20, padx=20, sticky= "n")
    setting_menu(frame, user_info) 
    
    button_frame = ctk.CTkFrame(frame)
    button_frame.grid(row=1, column=0, pady=20, padx=20, sticky="ns") 

    button_frame.grid_rowconfigure(0, weight=1)
    button_frame.grid_rowconfigure(1, weight=1)
 
    button_add = ctk.CTkButton(
        button_frame, 
        text="spezifische Übung hinzufügen", 
        font=("Arial", 12), 
        command=lambda: add_specificexercise(user_info)  
    )
    button_add.grid(row=0, column=0, pady=10, padx=20, sticky="ew")

    button_edit = ctk.CTkButton(
        button_frame, 
        text="spezifische Übung bearbeiten", 
        font=("Arial", 12), 
        command=lambda: edit_specificexercise(user_info)
    )
    button_edit.grid(row=1, column=0, pady=10, padx=20, sticky="ew")


    button_delete = ctk.CTkButton(
        button_frame, 
        text="spezifische Übung löschen", 
        font=("Arial", 12), 
        command=lambda: delete_specificexercise(user_info) 
    )
    button_delete.grid(row=2, column=0, pady=10, padx=20, sticky="ew")

   

    button_exercise_add = ctk.CTkButton(
        frame, 
        text="Exercise hinzufügen", 
        font=("Arial", 12), 
        command=lambda: add_exercise(user_info)  
    )
    button_exercise_add.grid(row=1, column=0, pady=10, padx=20, sticky="sw")

    

    textbox_frame = ctk.CTkFrame(frame)
    textbox_frame.grid(row=0, column=0, columnspan=2, padx=20, pady=70, sticky="nsew")

    textbox_frame.grid_rowconfigure(0, weight=1)
    textbox_frame.grid_columnconfigure(0, weight=1)
    textbox_frame.grid_columnconfigure(1, weight=1)


    global textbox_uebung
    global  textbox_rechts
    textbox_uebung = ctk.CTkTextbox(textbox_frame, width=125, height=200)  
    textbox_uebung.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
    textbox_rechts = ctk.CTkTextbox(textbox_frame, width=125, height=200)  
    textbox_rechts.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")


    

    update_textframe(user_info)

    input_field = ctk.CTkEntry(textbox_frame, placeholder_text="Übung suchen")
    input_field.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

    input_field.bind("<KeyRelease>", lambda event: search_in_textframe(event, input_field, user_info))
    
    input_field.bind("<Return>", lambda event: input_field.delete(0, ctk.END))

#def compare_users(user_info):
#    compare_window = ctk.CTkToplevel(root)
#    compare_window.title("Vergleiche Users")
#    compare_window.geometry("600x600")
#
#    header_label = ctk.CTkLabel(compare_window, text="Vergleiche Users", font=("Arial", 16, "bold"))
#    header_label.pack(pady=20)
#
#    input_field_1 = ctk.CTkEntry(compare_window, placeholder_text="User 1:")
#    input_field_1.pack(pady=10)
#
#    input_field_2 = ctk.CTkEntry(compare_window, placeholder_text="User 2:")
#    input_field_2.pack(pady=10)
#
#    exercise_label = ctk.CTkLabel(compare_window, text="Übung auswählen", font=("Arial", 12))
#    exercise_label.pack(pady=10)
#
#    exercises = do.find_all_exercises() 
#    exercise_options = {f"{exercise['id']} - {exercise['name']}": exercise["id"] for exercise in exercises}
#
#    selected_exercise_name = ctk.StringVar(value="ID - Name auswählen")
#    exercise_dropdown = ctk.CTkOptionMenu(
#        compare_window, 
#        values=list(exercise_options.keys()),  
#        variable=selected_exercise_name
#    )
#    exercise_dropdown.pack(pady=10)
#
#    compare_button = ctk.CTkButton(
#        compare_window, 
#        text="Vergleichen", 
#        command=lambda: safe()
#    )
#    compare_button.pack(pady=20)
#
#    compare_field = ctk.CTkEntry(compare_window, font=("Arial", 12), 
#                                 width=500,height= 200, state="disabled")
#    compare_field.pack(pady=20)
#
#    def safe():
#        user_1 = input_field_1.get()
#        user_2 = input_field_2.get()
#        exercise_name = selected_exercise_name.get()
#
#        exercise_id = exercise_options.get(exercise_name, None)
#
#        if not exercise_id:
#            compare_field.configure(state="normal")
#            compare_field.delete(0, ctk.END)
#            compare_field.insert(0, "Bitte eine gültige Übung auswählen!")
#            compare_field.configure(state="disabled")
#            return
#
#        text = do.compare_users_in_exercise(user_1, user_2, exercise_id)  
#        compare_field.configure(state="normal")
#        compare_field.delete(0, ctk.END)
#        compare_field.insert(0, text)
#        compare_field.configure(state="disabled")
#
#    compare_window.attributes("-topmost", True)


def add_specificexercise(user_info):
    add_window = ctk.CTkToplevel(root)
    add_window.title("Übung hinzufügen")
    add_window.geometry("400x500")
    
    header_label = ctk.CTkLabel(add_window, text="Übung hinzufügen", font=("Arial", 16, "bold"))
    header_label.pack(pady=20)
    
    exercise_id_label = ctk.CTkLabel(add_window, text="Übungs-ID", font=("Arial", 12))
    exercise_id_label.pack()
    
    exercise_id_entry = ctk.CTkEntry(add_window, font=("Arial", 12), width=200)
    exercise_id_entry.pack(pady=10)
    
    weight_label = ctk.CTkLabel(add_window, text="Gewicht (kg)", font=("Arial", 12))
    weight_label.pack()
    
    weight_entry = ctk.CTkEntry(add_window, font=("Arial", 12), width=200)
    weight_entry.pack(pady=10)
    
    reps_label = ctk.CTkLabel(add_window, text="Wiederholungen", font=("Arial", 12))
    reps_label.pack()
    
    reps_slider = ctk.CTkSlider(add_window, from_=1, to=20, number_of_steps=19, width=200)
    reps_slider.set(10)
    reps_slider.pack(pady=10)
    
    reps_value_label = ctk.CTkLabel(add_window, text=f"Wiederholungen: {reps_slider.get()}", font=("Arial", 10))
    reps_value_label.pack()
    
    sets_label = ctk.CTkLabel(add_window, text="Sätze", font=("Arial", 12))
    sets_label.pack()
    
    sets_slider = ctk.CTkSlider(add_window, from_=1, to=10, number_of_steps=9, width=200)
    sets_slider.set(3)
    sets_slider.pack(pady=10)
    
    sets_value_label = ctk.CTkLabel(add_window, text=f"Sätze: {sets_slider.get()}", font=("Arial", 10))
    sets_value_label.pack()
    
    def update_sets_label(val):
        sets_value_label.configure(text=f"Sätze: {int(val)}")
    
    def update_reps_label(val):
        reps_value_label.configure(text=f"Wiederholungen: {int(val)}")
    
    sets_slider.configure(command=update_sets_label)
    reps_slider.configure(command=update_reps_label)
    
    def save_exercise():
        exercise_id = exercise_id_entry.get()
        weight = int(weight_entry.get())
        sets = int(sets_slider.get())
        reps = int(reps_slider.get())
        
        do.add_specificexercise(exercise_id, sets, reps, weight, user_info["id"])
        update_textframe(user_info)
        print(f"Übung gespeichert: ID={exercise_id}, Gewicht={weight}kg, Sätze={sets}, Wiederholungen={reps}")

        add_window.destroy()

    save_button = ctk.CTkButton(add_window, text="Speichern", command=save_exercise)
    save_button.pack(pady=20)

    add_window.grab_set()
    add_window.wait_window()

def edit_specificexercise(user_info):
    """Bearbeitet eine spezifische Übung."""

    
    def update_reps_label(value):
        reps_value_label.configure(text=f"Wiederholungen: {int(value)}")

    def update_sets_label(value):
        sets_value_label.configure(text=f"Sätze: {int(value)}")


    edit_window = ctk.CTkToplevel(root)
    edit_window.title("Übung bearbeiten")
    edit_window.geometry("400x600")

    header_label = ctk.CTkLabel(edit_window, text="Übung bearbeiten", font=("Arial", 16, "bold"))
    header_label.pack(pady=20)

    exercise_id_label = ctk.CTkLabel(edit_window, text="Übungs-ID", font=("Arial", 12))
    exercise_id_label.pack()

    exercise_id_entry = ctk.CTkEntry(edit_window, font=("Arial", 12), width=200)
    exercise_id_entry.pack(pady=10)

    dropdown_var = ctk.StringVar(value="Wähle eine Übung")

    def populate_dropdown():
        """Füllt das Dropdown-Menü mit Übungsdaten basierend auf der ID."""
        exercise_id = exercise_id_entry.get()

        if exercise_id == "":
            messagebox.showwarning("Fehler", "Bitte eine Übungs-ID eingeben.")
            return

        try:
            exercise_data_list = do.find_specificexercisebyuseridandexerciseid(user_info["id"], int(exercise_id))
            print(exercise_data_list)
            if not exercise_data_list:
                messagebox.showwarning("Fehler", "Keine Übungen für diese ID gefunden.")
                return

            dropdown_menu.configure(values=[str(data.id) for data in exercise_data_list])
            dropdown_var.set("Wähle eine Übung")
            print(f"Übungen gefunden: {[data.id for data in exercise_data_list]}")

        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Abrufen der Übungsdaten: {e}")
            print(e)

    exercise_id_entry.bind("<Return>", lambda event: populate_dropdown())

    dropdown_menu = ctk.CTkOptionMenu(edit_window, variable=dropdown_var, values=[])
    dropdown_menu.pack(pady=10)

    weight_label = ctk.CTkLabel(edit_window, text="Gewicht (kg)", font=("Arial", 12))
    weight_label.pack()

    weight_entry = ctk.CTkEntry(edit_window, font=("Arial", 12), width=200)
    weight_entry.pack(pady=10)

    reps_label = ctk.CTkLabel(edit_window, text="Wiederholungen", font=("Arial", 12))
    reps_label.pack()

    reps_slider = ctk.CTkSlider(edit_window, from_=1, to=20, number_of_steps=19, width=200, command=update_reps_label)
    reps_slider.pack(pady=10)

    reps_value_label = ctk.CTkLabel(edit_window, text=f"Wiederholungen: {int(reps_slider.get())}", font=("Arial", 10))
    reps_value_label.pack()

    sets_label = ctk.CTkLabel(edit_window, text="Sätze", font=("Arial", 12))
    sets_label.pack()

    sets_slider = ctk.CTkSlider(edit_window, from_=1, to=10, number_of_steps=9, width=200, command=update_sets_label)
    sets_slider.pack(pady=10)

    sets_value_label = ctk.CTkLabel(edit_window, text=f"Sätze: {int(sets_slider.get())}", font=("Arial", 10))
    sets_value_label.pack()

    def on_dropdown_select():
        """Aktualisiert die Eingabefelder basierend auf der ausgewählten Übung."""
        selected_id = dropdown_var.get()
        print("ID" + selected_id)
        if selected_id == "Wähle eine Übung":
            messagebox.showwarning("Fehler", "Bitte eine gültige Übung auswählen.")
            return

        try:
            selected_data = do.find_exercise_details_by_id(int(selected_id))
            print("-"*50)
            #print(selected_data+"!!")

            if not selected_data:
                messagebox.showwarning("Fehler", "Details zur Übung konnten nicht gefunden werden!!")
                return

            weight = selected_data["weight"]
            reps = selected_data["reps"]
            sets = selected_data["sets"]

            if weight is not None:
                weight_entry.delete(0, ctk.END)
                weight_entry.insert(0, weight)

            if reps is not None:
                reps_slider.set(reps)
                update_reps_label(reps)

            if sets is not None:
                sets_slider.set(sets)
                update_sets_label(sets)


        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Laden der Übung: {e}")
            print(e)

    dropdown_menu.configure(command=lambda _: on_dropdown_select())

    def save_exercise():
        """Speichert die Änderungen der spezifischen Übung."""
        selected_id = dropdown_var.get()
        if selected_id == "Wähle eine Übung":
            messagebox.showwarning("Fehler", "Bitte eine gültige Übung auswählen.")
            return

        try:
            weight = int(weight_entry.get())
            sets = int(sets_slider.get())
            reps = int(reps_slider.get())

            do.update_specificexercise(id=int(selected_id), weight=weight, sets=sets, reps=reps)
            update_textframe(user_info)
            #display_reiter_3(frame,user_info)
            print(f"Übung gespeichert: ID={selected_id}, Gewicht={weight}, Sätze={sets}, Wiederholungen={reps}")
            messagebox.showinfo("Erfolg", "Übung erfolgreich aktualisiert.")
            edit_window.destroy()
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Speichern der Übung: {e}")

    save_button = ctk.CTkButton(edit_window, text="Speichern", command=save_exercise)
    save_button.pack(pady=20)

    edit_window.grab_set()
    edit_window.wait_window()


def delete_specificexercise(user_info):
    delete_window = ctk.CTkToplevel(root)
    delete_window.title("Übung löschen")
    delete_window.geometry("400x300")
    
    header_label = ctk.CTkLabel(delete_window, text="Spezifische Übung löschen", font=("Arial", 16, "bold"))
    header_label.pack(pady=20)
    
    specificexercise_id_label = ctk.CTkLabel(delete_window, text="Spezifische Übungs-ID", font=("Arial", 12))
    specificexercise_id_label.pack()
    
    exercise_id_entry = ctk.CTkEntry(delete_window, font=("Arial", 12), width=200)
    exercise_id_entry.pack(pady=10)
    
    def delete_exercise():
        exercise_id = exercise_id_entry.get()
        
        if not exercise_id.isdigit():
            print("Bitte eine gültige Übungs-ID eingeben.")
            return

        exercise_id = int(exercise_id)
        
        success = do.delete_specificexercise(exercise_id, user_info["id"])
        
        if success:
            print(f"Übung mit der ID {exercise_id} wurde gelöscht.")
            update_textframe(user_info)
            
        else:
            print(f"Fehler: Übung mit der ID {exercise_id} konnte nicht gelöscht werden.")

        delete_window.destroy()

    delete_button = ctk.CTkButton(delete_window, text="Löschen", command=delete_exercise)
    delete_button.pack(pady=20)

    delete_window.grab_set()
    delete_window.wait_window()


def add_exercise(user_info):
    """Öffnet ein Pop-up-Fenster, um eine Übung hinzuzufügen."""
    def save_exercise():
        exercise_name = exercise_name_entry.get()
        if exercise_name:
            print(f"Übung '{exercise_name}' wurde hinzugefügt.")
            do.add_exercise(str(exercise_name))
            
            popup.destroy()  
        else:
            error_label.config(text="Bitte gib einen Namen für die Übung ein.", fg="red")

    popup = ctk.CTkToplevel()
    popup.title("Übung hinzufügen")
    popup.geometry("300x300")

    ctk.CTkLabel(popup, text="Name der Übung:", font=("Arial", 12)).pack(pady=10)

    exercise_name_entry = ctk.CTkEntry(popup, font=("Arial", 12), width=200)
    exercise_name_entry.pack(pady=10)

    error_label = ctk.CTkLabel(popup, text="", font=("Arial", 10))
    error_label.pack(pady=5)

    save_button = ctk.CTkButton(popup, text="Übung speichern", font=("Arial", 12), command=save_exercise)
    save_button.pack(pady=10)

    cancel_button = ctk.CTkButton(popup, text="Abbrechen", font=("Arial", 12), command=popup.destroy)
    cancel_button.pack(pady=5)

    popup.grab_set()
    popup.wait_window()
    


def display_reiter_4(frame,user_info):
    """Zeigt den Inhalt von Workouts."""
    wkt.workout_window(frame, user_info, root)   


def on_appearance_option_selected(selected_option,user_info):
    """Reagiert auf die Auswahl im Einstellungsmenü."""
    if selected_option == "Erscheinungsbild":
        open_appearance_popup_and_apply_changes(user_info)
    if selected_option == "LogOut":
        quit()
    if selected_option == "Account":
        edit_user_data(user_info)


def open_appearance_popup_and_apply_changes(user_info):
    """Öffnet ein Pop-up-Fenster zur Auswahl des Erscheinungsbildes und des Farbschemas und wendet die Änderungen an."""
    popup = ctk.CTkToplevel()
    popup.title("Erscheinungsbild ändern")
    popup.geometry("300x250")  

    appearance_var = ctk.StringVar(value="Light")
    ctk.CTkLabel(popup, text="Erscheinungsmodus wählen:").pack(pady=10)
    ctk.CTkOptionMenu(popup, variable=appearance_var, values=["Light", "Dark", "System"]).pack(pady=5)

    #color_scheme_var = ctk.StringVar(value="Blue")  
    #ctk.CTkLabel(popup, text="Farbschema wählen:").pack(pady=10)
    #ctk.CTkOptionMenu(popup, variable=color_scheme_var, values=["blue", "green", "red", "purple", "orange"]).pack(pady=5)

    ctk.CTkButton(popup, text="Bestätigen", command=lambda: apply_and_close(popup, appearance_var)).pack(pady=10)
    
    popup.grab_set()  
    popup.mainloop()

def apply_and_close(popup, appearance_var):
    """Anwenden der Änderungen für Erscheinungsmodus und Farbschema und Schließen des Popups."""
    ctk.set_appearance_mode(appearance_var.get()) 
    #ctk.set_default_color_theme(color_scheme_var.get())
    #set_color_theme(color_scheme_var.get())  
    
    popup.destroy() 




def edit_user_data(user_info):
    edit_window = ctk.CTkToplevel(root)
    edit_window.title("Benutzerdaten bearbeiten")
    edit_window.geometry("400x300")
    print(user_info)

    header_label = ctk.CTkLabel(edit_window, text="Benutzerdaten bearbeiten", font=("Arial", 16, "bold"))
    header_label.grid(row=0, column=0, columnspan=2, pady=20)

    username_label = ctk.CTkLabel(edit_window, text="Username:", font=("Arial", 12))
    username_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
    username_value = ctk.CTkLabel(edit_window, text=user_info.get("username", ""), font=("Arial", 12))
    username_value.grid(row=1, column=1, padx=10, pady=5, sticky="w")

    email_label = ctk.CTkLabel(edit_window, text="E-Mail:", font=("Arial", 12))
    email_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
    email_value = ctk.CTkLabel(edit_window, text=user_info.get("email", ""), font=("Arial", 12))
    email_value.grid(row=2, column=1, padx=10, pady=5, sticky="w")

    password_label = ctk.CTkLabel(edit_window, text="Passwort", font=("Arial", 12))
    password_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")

    password_visible = ctk.StringVar(value="*")
    password_entry = ctk.CTkEntry(edit_window, font=("Arial", 12), width=200, show=password_visible.get())
    password_entry.grid(row=3, column=1, padx=10, pady=5, sticky="w")

    def toggle_password_visibility(button):
        if password_visible.get() == "*":
            password_visible.set("")  
            button.configure(text="👁️")  
        else:
            password_visible.set("*") 
            button.configure(text="🔒")  
        password_entry.configure(show=password_visible.get())

    eye_button = ctk.CTkButton(
        edit_window,
        text="🔒",
        width=30,
        command=lambda: toggle_password_visibility(eye_button)
    )
    eye_button.grid(row=3, column=2, padx=5, pady=5)

    save_button = ctk.CTkButton(
        edit_window, 
        text="Speichern", 
        font=("Arial", 12), 
        command=lambda: save_user_data(password_entry, user_info, frame, root, edit_window)
    )
    save_button.grid(row=4, column=0, columnspan=3, pady=20)

    edit_window.grab_set()  
    edit_window.wait_window()
    

def save_user_data(password_entry, user_info, frame, root, edit_window):
    new_password = password_entry.get()
    if new_password:
        user_info["password_hash"] = new_password

    do.update_password_in_database(user_info["username"], new_password)

    print("Benutzerdaten gespeichert:", user_info)

    edit_window.destroy()
    window_home(frame, user_info, root)



def gruppen(frame, user_data):
    label = ctk.CTkLabel(frame, text="Freunde & Gruppen", font=("Arial", 16))
    label.grid(row=0, column=0, pady=20)
    setting_menu(frame, user_data) 
    uig.base(frame, user_data, root)

    
    

def window():
    global root 
    root = ctk.CTk()
    root.geometry("600x400")
    root.title("MoveMate")

    global frame
    frame = ctk.CTkFrame(root)
    frame.place(relx=0.5, rely=0.5, anchor="center")

    


    window_login(frame, root)

    root.mainloop()


