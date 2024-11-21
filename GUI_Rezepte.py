import operations as do
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import time
import gui


def on_hover_in(event, textbox, line_number):
    """Ändert die Hintergrundfarbe, wenn der Mauszeiger über ein Rezept fährt."""
    textbox.tag_add("hover", f"{line_number}.0", f"{line_number}.end")
    textbox.tag_config("hover", background="lightblue")  

def on_hover_out(event, textbox, line_number):
    """Setzt die Hintergrundfarbe zurück, wenn der Mauszeiger das Rezept verlässt."""
    textbox.tag_remove("hover", f"{line_number}.0", f"{line_number}.end")  

def track_mouse_position(event, textbox, recipes):
    """Verfolgt die Mausposition und hebt das entsprechende Rezept hervor."""
    index = textbox.index(f"@{event.x},{event.y}") 
    line_number = int(index.split('.')[0])  

    lines = textbox.get("1.0", "end-1c").split("\n")  
    if line_number <= len(lines):
        textbox.tag_remove("hover", "1.0", "end")
        
        on_hover_in(event, textbox, line_number)

def on_double_click(event, textbox, recipes, user_info):
    """Ereignisbehandlung für Doppelklick auf ein Rezept im Textfeld."""
    index = textbox.index(f"@{event.x},{event.y}")
    line_number = index.split('.')[0]  

    recipe_line = textbox.get(f"{line_number}.0", f"{line_number}.end").strip()
    
    if recipe_line:
        try:
            recipe_id = recipe_line.split("\t")[0].split(":")[1].strip()
            show_recipe_details(recipe_id, user_info) 
        except IndexError:
            pass  


def show_recipe_details(recipe_id,user_info):
    """Zeigt ein Popout-Fenster mit den Details des Rezepts an."""
    recipe = do.find_rezept(recipe_id)  
    
    is_creator = recipe['creator_id'] == user_info["id"]
    
    details_window = ctk.CTkToplevel()
    details_window.title(f"Details für Rezept {recipe_id}")
    details_window.geometry("450x500")  
    details_window.configure(bg="#f1f1f1")  
    
    details_window.wm_attributes("-topmost", 1) 
    
    main_frame = ctk.CTkFrame(details_window, corner_radius=15, fg_color="white", width=400, height=450)
    main_frame.pack(padx=20, pady=20, fill="both", expand=True)

    title_label = ctk.CTkLabel(main_frame, text="Rezept Details", font=("Arial", 16, "bold"), text_color="#333333")
    title_label.pack(pady=10)

    label_name = ctk.CTkLabel(main_frame, text=f"Name: {recipe['name']}", font=("Arial", 12), anchor="w")
    label_name.pack(pady=(5, 10), padx=10, fill="x")

    label_description = ctk.CTkLabel(main_frame, text="Beschreibung:", font=("Arial", 12), anchor="w")
    label_description.pack(pady=(5, 10), padx=10, fill="x")

    description_textbox = ctk.CTkTextbox(main_frame, width=380, height=200, font=("Arial", 12), wrap="word")
    description_textbox.pack(padx=10, pady=(0, 10), fill="both", expand=True)
    description_textbox.insert("1.0", recipe['beschreibung'])  

    if not is_creator:
        description_textbox.configure(state="disabled")  

    def save_changes():
        """Speichert die Änderungen der Beschreibung."""
        updated_description = description_textbox.get("1.0", "end-1c")  
        do.update_rezept(recipe_id, new_description=updated_description)  
        details_window.destroy() 

    if is_creator:
        save_button = ctk.CTkButton(main_frame, text="Speichern", font=("Arial", 12), command=save_changes, fg_color="#4CAF50", hover_color="#45a049", width=200)
        save_button.pack(pady=10)

    close_button = ctk.CTkButton(main_frame, text="Schließen", font=("Arial", 12), command=details_window.destroy, fg_color="#FF4C4C", hover_color="#FF3333", width=200)
    close_button.pack(pady=20)

    details_window.after(100, lambda: details_window.attributes("-topmost", 0)) 

    details_window.grab_set()  
    details_window.mainloop()



def save_recipe(recipe_name, recipe_description,user_info):
    do.add_rezept(str(recipe_name), str(recipe_description), int(user_info["id"]))
    update_textframe(user_info)

def add_recipe(user_info, root):
    recipe_popup = ctk.CTkToplevel(root)
    recipe_popup.title("Neues Rezept hinzufügen")
    recipe_popup.geometry("600x600")  
    recipe_popup.configure(bg_color="#F0F0F0")

    label_title = ctk.CTkLabel(recipe_popup, text="Rezept hinzufügen", font=("Arial", 18, "bold"))
    label_title.pack(pady=20)

    label_name = ctk.CTkLabel(recipe_popup, text="Rezept Name:", font=("Arial", 12))
    label_name.pack(pady=10)
    
    recipe_name_entry = ctk.CTkEntry(recipe_popup, placeholder_text="Geben Sie den Namen des Rezepts ein", width=500)
    recipe_name_entry.pack(pady=10)

    label_description = ctk.CTkLabel(recipe_popup, text="Rezept Beschreibung:", font=("Arial", 12))
    label_description.pack(pady=10)

    recipe_description_box = ctk.CTkTextbox(recipe_popup, height=250, width=500, corner_radius=10, font=("Arial", 12))
    recipe_description_box.pack(pady=10)
    
    template = (
        "Zubereitungszeit: (z.B. 30 Minuten)\n"
        "Portionen: (z.B. 4 Portionen)\n"
        "Schwierigkeitsgrad: (z.B. Einfach)\n\n"
        "Zutaten:\n"
        "- (Zutat 1)\n"
        "- (Zutat 2)\n"
        "- (Zutat 3)\n"
        "- ...\n\n"
        "Anleitung:\n"
        "1. (Schritt 1)\n"
        "2. (Schritt 2)\n"
        "3. (Schritt 3)\n"
        "4. ...\n\n"
        "Tipps:\n"
        "- (Tipp 1)\n"
        "- (Tipp 2)\n"
        "- ..."
    )
    recipe_description_box.insert("1.0", template)

    def save_recipe_button():
        recipe_name = recipe_name_entry.get()
        recipe_description = recipe_description_box.get("1.0", ctk.END)
        
        if recipe_name and recipe_description:
            save_recipe(recipe_name, recipe_description, user_info)
            recipe_popup.destroy()  
            messagebox.showinfo("Erfolg", "Rezept wurde erfolgreich gespeichert!")
        else:
            messagebox.showwarning("Warnung", "Bitte alle Felder ausfüllen.")
    
    save_button = ctk.CTkButton(recipe_popup, text="Rezept speichern", font=("Arial", 14), command=save_recipe_button, fg_color="#4CAF50", hover_color="#45a049")
    save_button.pack(pady=20)

    recipe_popup.grab_set()  
    

def update_textframe(user_info):
    textbox_rezepte.configure(state="normal")
    textbox_rezepte.delete("1.0", ctk.END)
    recipe_text = "Rezepte:\n"
    recipe_text += "-" * 30 + "\n"
    
    recipes = do.find_all_recipes()  
    for recipe in recipes:
        recipe_text += f"ID: {recipe['id']}\t | Name: {recipe['name']}\n"  
    
    textbox_rezepte.insert("1.0", recipe_text)
    textbox_rezepte.configure(state="disabled")

    textbox_rezepte.bind("<Motion>", lambda event: track_mouse_position(event, textbox_rezepte, recipes))
    textbox_rezepte.bind("<Double-1>", lambda event: on_double_click(event, textbox_rezepte, recipes, user_info))

    


def rezepte_window(frame, user_info,root):

    user_info = do.find_user_by_username(user_info["username"])

    """Zeigt den Inhalt von Rezpten."""
    label = ctk.CTkLabel(frame, text="Rezpte", font=("Arial", 20))
    label.grid(row=0, column=0, pady=20, padx=20, sticky="n")
    
    gui.setting_menu(frame, user_info)  

    button_frame = ctk.CTkFrame(frame)
    button_frame.grid(row=1, column=0, pady=20, padx=20, sticky="ns") 

    button_frame.grid_rowconfigure(0, weight=1)
    button_frame.grid_rowconfigure(1, weight=1)
    button_frame.grid_rowconfigure(2, weight=1)
 
    button_add = ctk.CTkButton(
        button_frame, 
        text="Rezpte hinzufügen", 
        font=("Arial", 12), 
        command=lambda: add_recipe(user_info,root)  
    )
    button_add.grid(row=0, column=0, pady=10, padx=20, sticky="ew")

    button_edit = ctk.CTkButton(
        button_frame, 
        text="Rezpte bearbeiten", 
        font=("Arial", 12), 
        command=lambda: edit_recipe(user_info, root)
    )
    button_edit.grid(row=1, column=0, pady=10, padx=20, sticky="ew")

    

    textbox_frame = ctk.CTkFrame(frame)
    textbox_frame.grid(row=0, column=0, padx=20, pady=70, sticky="nsew")

    textbox_frame.grid_rowconfigure(0, weight=1)
    textbox_frame.grid_columnconfigure(0, weight=1)
    textbox_frame.grid_columnconfigure(1, weight=1)

    global textbox_rezepte
    textbox_rezepte = ctk.CTkTextbox(textbox_frame, width=125, height=200)  
    textbox_rezepte.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
    

    update_textframe(user_info)


    


def  edit_recipe(user_info, root):
    pass
