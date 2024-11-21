import operations as do
import customtkinter as ctk
import tkinter as tk

def base(frame, user_data, root):

    selected_group_id = None

    def clear_frame(inner_frame):
        for widget in inner_frame.winfo_children():
            widget.destroy()

    def add_user(group):
        def close_popup(event=None):
            id = do.find_user_by_username(entry.get())
            if id != None:
                do.add_group_user(group[1], id["id"])
                popup.destroy()
                gruppen_info(group)
            else:
                entry.delete(0, "end")
                label.configure(text="Benutzer nicht registriert!")


        popup = ctk.CTkToplevel(root)
        popup.title("Benutzername eingeben")
        popup.geometry("300x150")

        label = ctk.CTkLabel(popup, text="Bitte Benutzername eingeben:")
        label.pack(pady=10)
        entry = ctk.CTkEntry(popup)
        entry.pack(pady=5)
        entry.bind("<Return>", lambda event: close_popup())

        entry.focus()

        popup.transient()
        popup.grab_set()
        popup.wait_window()

    def add_group():
        def close_popup(event=None):
            group_id = do.add_group(entry.get(), "Filler")
            do.add_group_user(group_id, user_data["id"])
            gruppen_liste()
            popup.destroy()

        popup = ctk.CTkToplevel(root)
        popup.title("Neue Gruppe")
        popup.geometry("300x150")

        ctk.CTkLabel(popup, text="Bitte Namen der Gruppe eingeben:").pack(pady=10)
        entry = ctk.CTkEntry(popup)
        entry.pack(pady=5)
        entry.bind("<Return>", lambda event: close_popup())

        entry.focus()

        popup.transient()
        popup.grab_set()
        popup.wait_window()
        
    def del_group():
        def close_popup(event=None):
            if entry.get() != "y":
                popup.destroy()
            else:
                global selected_group_id
                do.del_group(selected_group_id)
                gruppen_info()
                gruppen_liste()
                popup.destroy()

        popup = ctk.CTkToplevel(root)
        popup.title("Lösche Gruppe")
        popup.geometry("300x150")

        ctk.CTkLabel(popup, text="Wenn sie fortfahren möchten geben sie \"y\" ein:").pack(pady=10)
        entry = ctk.CTkEntry(popup)
        entry.pack(pady=5)
        entry.bind("<Return>", lambda event: close_popup())

        entry.focus()

        popup.transient()
        popup.grab_set()
        popup.wait_window()

    def compare_users(user_2: int):
        compare_window = ctk.CTkToplevel(root)
        compare_window.title("Vergleiche Users")
        compare_window.geometry("600x400")

        header_label = ctk.CTkLabel(compare_window, text="Vergleiche Users", font=("Arial", 16, "bold"))
        header_label.pack(pady=20)

        exercise_label = ctk.CTkLabel(compare_window, text="Übung auswählen", font=("Arial", 12))
        exercise_label.pack(pady=10)

        #exercises = do.find_all_exercises()
        exercises = do.find_common_exercises(user_data["id"], user_2)  
        print(exercises)
        exercise_options = {f"{int(exercise['id'])} - {exercise['name']}": exercise["id"] for exercise in exercises}

        selected_exercise_name = ctk.StringVar(value="ID - Name auswählen")
        exercise_dropdown = ctk.CTkOptionMenu(
            compare_window, 
            values=list(exercise_options.keys()),  
            variable=selected_exercise_name
        )
        exercise_dropdown.pack(pady=10)

        compare_button = ctk.CTkButton(
            compare_window, 
            text="Vergleichen", 
            command=lambda: safe()
        )
        compare_button.pack(pady=20)

        compare_field = ctk.CTkEntry(compare_window, font=("Arial", 12), 
                                    width=500,height= 200, state="disabled")
        compare_field.pack(pady=20)

        def safe():
            user_1 = user_data["id"]
            exercise_name = selected_exercise_name.get()

            exercise_id = exercise_options.get(exercise_name, None)

            if not exercise_id:
                compare_field.configure(state="normal")
                compare_field.delete(0, ctk.END)
                compare_field.insert(0, "Bitte eine gültige Übung auswählen!")
                compare_field.configure(state="disabled")
                return

            text = do.compare_users_in_exercise(user_data["id"], user_2, exercise_id)  
            compare_field.configure(state="normal")
            compare_field.delete(0, ctk.END)
            compare_field.insert(0, text)
            compare_field.configure(state="disabled")

        compare_window.attributes("-topmost", True)

    def gruppen_info(group=None):
        if group == None:
            clear_frame(cframe)
            return
        global selected_group_id
        selected_group_id = group[1]

        clear_frame(cframe)
        group_label = ctk.CTkLabel(cframe, text=group[0], font=("Arial", 20))
        group_label.grid(row=0, column=0, pady=10, padx=20, sticky="ew")
        
        add = ctk.CTkButton(cframe, text="ADD", command=lambda: add_user(group), font=("Arial", 20))
        add.grid(row=0, column=1)
        
        mitglieder = do.find_users_of_group(group[1])
        namen = [(do.find_user_by_userid(m)["username"], m) for m in mitglieder]
        
        for i, name in enumerate(namen):
            label = ctk.CTkLabel(cframe, text=name[0], font=("Arial", 14))
            label.grid(row=i+1, column=0)
            if name[0] != user_data["username"]:
                b_del = ctk.CTkButton(cframe, text="X", command=lambda n=name[0]: mitglied_entfernen(n, group), width=40)
                b_del.grid(row=i+1, column=2, pady=5, padx=(5,20))
                b_com = ctk.CTkButton(cframe, text="Vergleiche", command=lambda n=name[1]: compare_users(n), width=40)
                b_com.grid(row=i+1, column=1, pady=5, padx=(20,5))

    def gruppen_config():
        add_g = ctk.CTkButton(aframe, text="Gruppe erstellen", command=lambda: add_group())
        add_g.grid(row=0, column=0, pady=20, padx=20)

        del_g = ctk.CTkButton(aframe, text="Gruppe löschen", command=lambda: del_group())
        del_g.grid(row=1, column=0, pady=20, padx=20)

            

    def gruppen_liste():
        clear_frame(bframe)
        user_id = user_data["id"]
        groups = [(do.find_group(id)["name"], id) for id in do.find_groups_from_user(user_id)]

        group_label = ctk.CTkLabel(bframe, text="Deine Gruppen:", font=("Arial", 20))
        group_label.grid(row=0, column=0, pady=10, padx=20, sticky="ew")

        for i, group in enumerate(groups):
            group_button = ctk.CTkButton(
                bframe, 
                text=group[0], 
                command=lambda g=group: gruppen_info(g)
            )
            group_button.grid(row=i + 1, column=0, pady=5, padx=20, sticky="n")

    def mitglied_entfernen(n, group):
        data = do.find_user_by_username(n)
        do.del_group_user(group[1], data["id"])
        gruppen_info(group)


    gframe = ctk.CTkFrame(frame)
    gframe.grid(row=0, column=0, pady=60, padx=30, sticky="nsew")
    gframe.grid_columnconfigure(0, weight=2)
    gframe.grid_columnconfigure(1, weight=3)
    gframe.grid_columnconfigure(2, weight=1)
    gframe.grid_rowconfigure(0, weight=1)

    aframe = ctk.CTkFrame(gframe)
    aframe.grid(row=0, column=2, pady=20, padx=20, sticky="nsew")
    aframe.grid_columnconfigure(0, weight=1)
    #aframe.grid_forget()

    bframe = ctk.CTkFrame(gframe)
    bframe.grid(row=0, column=0, pady=20, padx=20, sticky="nsew")
    bframe.grid_columnconfigure(0, weight=1)
    bframe.grid_columnconfigure(1, weight=1)

    cframe = ctk.CTkFrame(gframe)
    cframe.grid(row=0, column=1, pady=20, padx=20, sticky="nsew")
    cframe.grid_columnconfigure(0, weight=4)
    cframe.grid_columnconfigure(1, weight=1)
    cframe.grid_columnconfigure(2, weight=1)

    gruppen_liste()
    gruppen_config()




