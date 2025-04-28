import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from PIL import Image
import random
import os
import sys

# === Citations stylées pour MapEquilibre ===
citations = [
    "🎨 Propulsé par MapEquilibre • Respect du style, équilibre des formes.",
    "🌍 Par MapEquilibre • Où l'esthétique rencontre la fonctionnalité.",
    "🧠 Codé avec grâce par MapEquilibre • Pensée visuelle et éthique.",
    "✨ Design harmonieux signé MapEquilibre • Moins de chaos, plus de clarté.",
    "📐 MapEquilibre • L'équilibre entre art, code et intention."
]

# === Thèmes ===
themes = {
    "clair": {
        "bg": "#ffffff",
        "fg": "#000000",
        "button_bg": "#f0f0f0",
        "button_fg": "#000000"
    },
    "sombre": {
        "bg": "#1e1e1e",
        "fg": "#ffffff",
        "button_bg": "#2d2d2d",
        "button_fg": "#ffffff"
    }
}
mode_courant = "clair"

def valider_entree_numerique(P):
    if P == "":
        return True
    try:
        val = int(P)
        return 0 <= val <= 255
    except ValueError:
        return False

def appliquer_theme():
    theme = themes[mode_courant]
    racine.configure(bg=theme["bg"])
    for widget in racine.winfo_children():
        if isinstance(widget, tk.Button):
            widget.configure(bg=theme["button_bg"], fg=theme["button_fg"])
        elif isinstance(widget, tk.Label):
            widget.configure(bg=theme["bg"], fg=theme["fg"])
        elif isinstance(widget, tk.Entry):
            widget.configure(bg=theme["bg"], fg=theme["fg"], insertbackground=theme["fg"])

def basculer_theme():
    global mode_courant
    mode_courant = "sombre" if mode_courant == "clair" else "clair"
    appliquer_theme()

def convertir_image(filepath, seuil_blanc=200, facteur_upscale=3, format_sortie='PNG'):
    try:
        # Vérification de l'existence du fichier
        if not os.path.exists(filepath):
            raise FileNotFoundError("Le fichier source n'existe pas.")

        # Vérification de l'espace disque disponible
        image_size = os.path.getsize(filepath)
        if image_size > 100 * 1024 * 1024:  # 100 MB
            raise ValueError("L'image est trop volumineuse (max 100 MB).")

        # Ouverture et conversion de l'image
        with Image.open(filepath) as image:
            image = image.convert('RGBA')
            largeur, hauteur = image.size
            
            # Vérification des dimensions après upscale
            new_width = largeur * facteur_upscale
            new_height = hauteur * facteur_upscale
            if new_width > 10000 or new_height > 10000:
                raise ValueError("Les dimensions après agrandissement sont trop importantes.")

            # Création d'une nouvelle image pour le résultat
            nouvelle_image = Image.new('RGBA', (largeur, hauteur), (0, 0, 0, 0))
            pixels_source = image.load()
            pixels_dest = nouvelle_image.load()

            # Traitement des pixels
            for y in range(hauteur):
                for x in range(largeur):
                    r, g, b, a = pixels_source[x, y]
                    if r > seuil_blanc and g > seuil_blanc and b > seuil_blanc:
                        pixels_dest[x, y] = (0, 0, 0, 0)
                    else:
                        pixels_dest[x, y] = (0, 0, 0, 255)

            # Redimensionnement
            image_upscale = nouvelle_image.resize(
                (new_width, new_height),
                resample=Image.NEAREST
            )

            # Sauvegarde
            ext = format_sortie.lower()
            nom_sortie = filepath.rsplit('.', 1)[0] + f'_noir.{ext}'
            image_upscale.save(nom_sortie, format_sortie.upper())
            return nom_sortie

    except Exception as e:
        raise Exception(f"Erreur lors de la conversion : {str(e)}")

def valider_parametres():
    try:
        seuil = int(entry_seuil.get())
        if not 0 <= seuil <= 255:
            raise ValueError("Le seuil doit être entre 0 et 255")
        
        upscale = int(entry_upscale.get())
        if not 1 <= upscale <= 10:
            raise ValueError("L'agrandissement doit être entre 1 et 10")
        
        return True
    except ValueError as e:
        messagebox.showerror("Erreur de paramètres", str(e))
        return False

def choisir_fichier():
    if not valider_parametres():
        return

    fichier = filedialog.askopenfilename(
        title="Choisir un visuel",
        filetypes=[("Images", "*.png *.jpg *.jpeg *.webp")]
    )
    
    if fichier:
        try:
            racine.config(cursor="watch")
            barre_progression.start()
            
            seuil = int(entry_seuil.get())
            upscale = int(entry_upscale.get())
            format_sortie = var_format.get()
            
            resultat = convertir_image(fichier, seuil, upscale, format_sortie)
            messagebox.showinfo(
                "Succès",
                f"Image convertie avec succès !\nFichier : {os.path.basename(resultat)}"
            )
            
        except Exception as e:
            messagebox.showerror("Erreur", str(e))
        finally:
            racine.config(cursor="")
            barre_progression.stop()

# === Interface ===
racine = tk.Tk()
racine.title("Convertisseur Visuel • Par MapEquilibre")
racine.geometry("460x460")
racine.resizable(False, False)

# Validation pour les entrées numériques
validation = racine.register(valider_entree_numerique)

# Création des widgets avec style amélioré
style = ttk.Style()
style.configure("Custom.TLabel", padding=5)

tk.Label(racine, text="1. Seuil de blanc (0-255) :", font=("Helvetica", 10)).pack(fill='x', padx=20, pady=(10, 0))
entry_seuil = tk.Entry(racine, validate='key', validatecommand=(validation, '%P'))
entry_seuil.insert(0, "200")
entry_seuil.pack(fill='x', padx=20)

tk.Label(racine, text="2. Facteur d'agrandissement (1-10) :", font=("Helvetica", 10)).pack(fill='x', padx=20, pady=(10, 0))
entry_upscale = tk.Entry(racine, validate='key', validatecommand=(validation, '%P'))
entry_upscale.insert(0, "3")
entry_upscale.pack(fill='x', padx=20)

tk.Label(racine, text="3. Format de sortie :", font=("Helvetica", 10)).pack(fill='x', padx=20, pady=(10, 0))
var_format = tk.StringVar(racine)
var_format.set("PNG")
formats = ttk.OptionMenu(racine, var_format, "PNG", "PNG", "WEBP")
formats.pack(fill='x', padx=20)

convert_button = tk.Button(
    racine,
    text="4. Choisir un fichier et convertir",
    command=choisir_fichier,
    relief="groove",
    font=("Helvetica", 10, "bold")
)
convert_button.pack(pady=(15, 10))

barre_progression = ttk.Progressbar(racine, mode='indeterminate')
barre_progression.pack(fill='x', padx=20, pady=(0, 20))

# === Boutons fun ===
tk.Button(
    racine,
    text="🎛 Mode clair/sombre",
    command=basculer_theme,
    relief="groove"
).pack(pady=(0, 5))

# === Crédit dynamique avec easter egg ===
compteur_clicks = [0]
def easter_egg(event):
    compteur_clicks[0] += 1
    if compteur_clicks[0] >= 3:
        messagebox.showinfo(
            "🐣 Bonus Wikimedia",
            "Saviez-vous ? Le premier logo Wikimedia a été dessiné en 2001 par Bjørn Smestad 🌐"
        )
        compteur_clicks[0] = 0

footer = tk.Label(
    racine,
    text=random.choice(citations),
    font=("Helvetica", 9, "italic"),
    fg="#666666",
    cursor="hand2"
)
footer.bind("<Button-1>", easter_egg)
footer.pack(side="bottom", pady=5)

# Initialisation du thème
appliquer_theme()

# Lancement de l'application
racine.mainloop()
