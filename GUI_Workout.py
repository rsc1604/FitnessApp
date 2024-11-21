import operations as do
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import time
import gui




def on_hover_in(event, textbox, line_number):
    """Ändert die Hintergrundfarbe, wenn der Mauszeiger über ein Workout fährt."""
    textbox.tag_add("hover", f"{line_number}.0", f"{line_number}.end")
    textbox.tag_config("hover", background="lightblue")  

def on_hover_out(event, textbox, line_number):
    """Setzt die Hintergrundfarbe zurück, wenn der Mauszeiger das Workout verlässt."""
    textbox.tag_remove("hover", f"{line_number}.0", f"{line_number}.end")  

def track_mouse_position(event, textbox, workouts):
    """Verfolgt die Mausposition und hebt das entsprechende Workout hervor."""
    index = textbox.index(f"@{event.x},{event.y}") 
    line_number = int(index.split('.')[0])  

    lines = textbox.get("1.0", "end-1c").split("\n")  
    if line_number <= len(lines):
        textbox.tag_remove("hover", "1.0", "end")
        
        on_hover_in(event, textbox, line_number)



def on_double_click(event, textbox, workouts):
    """Ereignisbehandlung für Doppelklick auf ein Workout im Textfeld."""
    index = textbox.index(f"@{event.x},{event.y}")
    line_number = index.split('.')[0]  

    workout_line = textbox.get(f"{line_number}.0", f"{line_number}.end").strip()
    
    if workout_line:
        try:
            workout_id = workout_line.split("\t")[0].split(":")[1].strip()
            show_workout_details(workout_id) 
        except IndexError:
            pass  


import customtkinter as ctk

def show_workout_details(workout_id):
    """Zeigt ein Popout-Fenster mit den Details des Workouts an."""
    workout = do.get_workout_by_id(workout_id)
    
    details_window = ctk.CTkToplevel()
    details_window.title(f"Details für Workout {workout_id}")
    details_window.geometry("350x400") 
    details_window.configure(bg="#f1f1f1") 
    
    details_window.wm_attributes("-topmost", 1) 
    
    main_frame = ctk.CTkFrame(details_window, corner_radius=15, fg_color="white", width=300, height=350)
    main_frame.pack(padx=20, pady=20, fill="both", expand=True)

    title_label = ctk.CTkLabel(main_frame, text="Workout Details", font=("Arial", 16, "bold"), text_color="#333333")
    title_label.pack(pady=10)

    label_name = ctk.CTkLabel(main_frame, text=f"Name: {workout['name']}", font=("Arial", 12), anchor="w")
    label_name.pack(pady=(5, 10), padx=10, fill="x")

    label_duration = ctk.CTkLabel(main_frame, text=f"Dauer: {workout['duration']} Minuten", font=("Arial", 12), anchor="w")
    label_duration.pack(pady=(5, 10), padx=10, fill="x")

    label_calories = ctk.CTkLabel(main_frame, text=f"Kalorien: {workout['calories']} kcal", font=("Arial", 12), anchor="w")
    label_calories.pack(pady=(5, 10), padx=10, fill="x")

    close_button = ctk.CTkButton(main_frame, text="Schließen", font=("Arial", 12), command=details_window.destroy, fg_color="#FF4C4C", hover_color="#FF3333", width=200)
    close_button.pack(pady=20)

    details_window.lift()  #
    details_window.after(100, lambda: details_window.attributes("-topmost", 0)) 

    details_window.grab_set()  
    details_window.mainloop()



def update_textframe(user_info):
    textbox_uebung.configure(state="normal")
    textbox_uebung.delete("1.0", ctk.END)
    user_info = do.find_user_by_username(user_info["username"])
    
    uebung_text = "Spezifische Übungen:\n" 
    uebung_text += "-" * 30 + "\n"
    
    specific_exercises = do.find_all_specific_exercises(user_info["id"])
    for exercise in specific_exercises:
        name_uebung = do.find_exercise_by_id(int(exercise['id_exercise']))
        if name_uebung is None:
            uebung_text += f"ID: {exercise['id']}\t | Name: Übung nicht gefunden\t | "
        else:
            uebung_text += f"ID: {exercise['id']}\t | Name: {name_uebung['name']}\t | "
        uebung_text += f"Wiederholungen: {exercise['reps']}\t | Sätze: {exercise['sets']}\t | Gewicht: {exercise['weight']} kg\n"
    
    textbox_uebung.insert("1.0", uebung_text)
    textbox_uebung.configure(state="disabled")

    textbox_rechts.configure(state="normal")
    textbox_rechts.delete("1.0", ctk.END)
    workout_text = "Workouts:\n"
    workout_text += "-" * 30 + "\n"

    workouts = do.find_all_workouts_by_user(int(user_info["id"]))  
    for workout in workouts:
        workout_text += f"ID: {workout['id']}\t | Name: {workout['name']}\n"
        
    textbox_rechts.insert("1.0", workout_text)
    textbox_rechts.configure(state="disabled")

    textbox_rechts.bind("<Double-1>", lambda event: on_double_click(event, textbox_rechts, workouts))
    
    textbox_rechts.bind("<Motion>", lambda event, textbox=textbox_rechts, workouts=workouts: track_mouse_position(event, textbox, workouts))

def workout_window(frame, user_info,root):

    user_info = do.find_user_by_username(user_info["username"])

    """Zeigt den Inhalt von Übungen und Workouts."""
    label = ctk.CTkLabel(frame, text="Workouts", font=("Arial", 20))
    label.grid(row=0, column=0, pady=20, padx=20, sticky="n")
    
    gui.setting_menu(frame, user_info)  

    button_frame = ctk.CTkFrame(frame)
    button_frame.grid(row=1, column=0, pady=20, padx=20, sticky="ns") 

    button_frame.grid_rowconfigure(0, weight=1)
    button_frame.grid_rowconfigure(1, weight=1)
    button_frame.grid_rowconfigure(2, weight=1)
 
    button_add = ctk.CTkButton(
        button_frame, 
        text="Workout hinzufügen", 
        font=("Arial", 12), 
        command=lambda: add_workout(user_info,root)  
    )
    button_add.grid(row=0, column=0, pady=10, padx=20, sticky="ew")

    button_edit = ctk.CTkButton(
        button_frame, 
        text="Workout bearbeiten", 
        font=("Arial", 12), 
        command=lambda: show_workout(user_info)
    )
    button_edit.grid(row=1, column=0, pady=10, padx=20, sticky="ew")

    

    textbox_frame = ctk.CTkFrame(frame)
    textbox_frame.grid(row=0, column=0, padx=20, pady=70, sticky="nsew")

    textbox_frame.grid_rowconfigure(0, weight=1)
    textbox_frame.grid_columnconfigure(0, weight=1)
    textbox_frame.grid_columnconfigure(1, weight=1)

    global textbox_uebung
    global textbox_rechts
    textbox_uebung = ctk.CTkTextbox(textbox_frame, width=125, height=200)  
    textbox_uebung.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
    textbox_rechts = ctk.CTkTextbox(textbox_frame, width=125, height=200)  
    textbox_rechts.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

    update_textframe(user_info)


    

def add_workout(user_info,root):
    add_window = ctk.CTkToplevel(root)
    add_window.title("Workout hinzufügen")
    add_window.geometry("400x500")
    
    header_label = ctk.CTkLabel(add_window, text="Workout hinzufügen", font=("Arial", 16, "bold"))
    header_label.pack(pady=20)

    workout_name_label = ctk.CTkLabel(add_window, text="Name", font=("Arial", 12))
    workout_name_label.pack()
    
    workout_name_entry = ctk.CTkEntry(add_window, font=("Arial", 12), width=200)
    workout_name_entry.pack(pady=10)

    duration_label = ctk.CTkLabel(add_window, text="Länge  (min)", font=("Arial", 12))
    duration_label.pack()
    
    duration_entry = ctk.CTkEntry(add_window, font=("Arial", 12), width=200)
    duration_entry.pack(pady=10)

    calories_label = ctk.CTkLabel(add_window, text="Kalorien  (kcal)", font=("Arial", 12))
    calories_label.pack()
    
    calories_entry = ctk.CTkEntry(add_window, font=("Arial", 12), width=200)
    calories_entry.pack(pady=10)

    specific_exercises_data = do.find_all_specific_exercises(user_info["id"])

    exercise_checkboxes = {}
    for exercise in specific_exercises_data:
        var = tk.BooleanVar()
        checkbox = ctk.CTkCheckBox(add_window, text=exercise["id"], variable=var)
        checkbox.pack(anchor="w", padx=20)
        exercise_checkboxes[exercise["id"]] = var

    def save_workout():
        workout_name = workout_name_entry.get()
        try:
            duration = int(duration_entry.get())
            calories = int(calories_entry.get())
        except ValueError:
            messagebox.showerror("Ungültige Eingabe", "Bitte geben Sie gültige Zahlen für Dauer und Kalorien ein.")
            return
        
        selected_exercises = [exercise_id for exercise_id, var in exercise_checkboxes.items() if var.get()]

        if not workout_name:
            messagebox.showwarning("Fehlender Name", "Bitte geben Sie einen Namen für das Workout ein.")
            return

        if not selected_exercises:
            messagebox.showwarning("Keine Übung ausgewählt", "Bitte wählen Sie mindestens eine Übung aus.")
            return

        print(f"Workout '{workout_name}' erstellt mit den Übungen: {selected_exercises}, Dauer: {duration} min, Kalorien: {calories} kcal")
        do.add_workout(workout_name,selected_exercises, duration, calories, user_info["id"])
        update_textframe(user_info)
        messagebox.showinfo("Erfolg", f"Workout '{workout_name}' wurde erfolgreich erstellt!")

        add_window.destroy()

    save_button = ctk.CTkButton(add_window, text="Speichern", command=save_workout)
    save_button.pack(pady=20)
    add_window.attributes("-topmost", True)


def show_workout(user_info):
    pass

def delete_workout(user_info):
    print(f"Workout löschen für: {user_info['username']}")