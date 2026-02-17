import tkinter as tk
import random
from math import sin, cos, radians

# Constantes
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
GAME_SPEED = 30  # ms entre chaque frame
FRITE_SPAWN_RATE = 40  # frames entre chaque frite
FRITE_SPEED = 3

# Couleurs
BG_COLOR = "#87CEEB"  # Bleu ciel
GROUND_COLOR = "#90EE90"  # Vert clair
RED = "#E31837"  # Rouge McDonald's
YELLOW = "#FFC72C"  # Jaune McDonald's
FRITE_COLOR = "#FFD700"
FRITE_SHADOW = "#DAA520"
TEXT_COLOR = "#333"


class Frite:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 8
        self.height = 40
        self.speed = FRITE_SPEED + random.uniform(-1, 1)
        self.rotation = random.randint(-30, 30)
        self.wobble = random.uniform(0, 360)

    def update(self):
        self.y += self.speed
        self.wobble += 5
        self.x += sin(radians(self.wobble)) * 0.5

    def is_off_screen(self):
        return self.y > WINDOW_HEIGHT


class PaquetFrites:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 80
        self.height = 100
        self.target_x = x
        self.speed = 15

    def move_to(self, target_x):
        self.target_x = max(self.width // 2, min(WINDOW_WIDTH - self.width // 2, target_x))

    def update(self):
        if abs(self.x - self.target_x) > 2:
            if self.x < self.target_x:
                self.x = min(self.x + self.speed, self.target_x)
            else:
                self.x = max(self.x - self.speed, self.target_x)

    def get_catch_rect(self):
        # Zone de capture (haut du paquet)
        return (
            self.x - self.width // 2,
            self.y - self.height // 2,
            self.x + self.width // 2,
            self.y - self.height // 2 + 20
        )


class FritesGame:
    def __init__(self, root):
        self.root = root
        self.root.title("🍟 McDonald's Frites Catcher")
        self.root.configure(bg=BG_COLOR)
        self.root.resizable(False, False)

        # Variables pour le plein écran
        self.is_fullscreen = False
        self.root.bind("<F11>", self.toggle_fullscreen)
        self.root.bind("<Escape>", self.exit_fullscreen)

        # Frame principal
        self.main_frame = tk.Frame(root, bg=BG_COLOR)
        self.main_frame.pack(padx=20, pady=20)

        # Score et vies
        self.info_frame = tk.Frame(self.main_frame, bg=BG_COLOR)
        self.info_frame.pack(fill=tk.X, pady=(0, 10))

        self.score_label = tk.Label(
            self.info_frame,
            text="Score: 0",
            font=("Arial", 20, "bold"),
            bg=BG_COLOR,
            fg=RED
        )
        self.score_label.pack(side=tk.LEFT, padx=10)

        self.lives_label = tk.Label(
            self.info_frame,
            text="❤️ ❤️ ❤️",
            font=("Arial", 20),
            bg=BG_COLOR
        )
        self.lives_label.pack(side=tk.RIGHT, padx=10)

        # Canvas
        self.canvas = tk.Canvas(
            self.main_frame,
            width=WINDOW_WIDTH,
            height=WINDOW_HEIGHT,
            bg=BG_COLOR,
            highlightthickness=3,
            highlightbackground=RED
        )
        self.canvas.pack()

        # Instructions
        self.instructions = tk.Label(
            self.main_frame,
            text="Souris pour bouger • F11 plein écran • R pour recommencer",
            font=("Arial", 10),
            bg=BG_COLOR,
            fg=TEXT_COLOR
        )
        self.instructions.pack(pady=(10, 0))

        # Variables du jeu
        self.paquet = PaquetFrites(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 80)
        self.frites = []
        self.score = 0
        self.lives = 3
        self.game_over = False
        self.game_started = False
        self.frame_count = 0
        self.combo = 0
        self.max_combo = 0

        # Binding souris
        self.canvas.bind("<Motion>", self.on_mouse_move)
        self.canvas.bind("<Button-1>", self.on_click)
        self.root.bind("r", lambda e: self.restart_game())
        self.root.bind("R", lambda e: self.restart_game())

        # Dessiner le fond
        self.draw_background()

        # Afficher écran d'accueil
        self.show_start_screen()

    def toggle_fullscreen(self, event=None):
        self.is_fullscreen = not self.is_fullscreen
        self.root.attributes("-fullscreen", self.is_fullscreen)
        return "break"

    def exit_fullscreen(self, event=None):
        if self.is_fullscreen:
            self.is_fullscreen = False
            self.root.attributes("-fullscreen", False)
            return "break"

    def draw_background(self):
        # Ciel avec nuages
        self.canvas.create_rectangle(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT, fill=BG_COLOR, outline="")

        # Nuages décoratifs
        clouds = [(150, 80), (400, 120), (650, 60), (250, 180)]
        for cx, cy in clouds:
            self.draw_cloud(cx, cy)

        # Sol
        self.canvas.create_rectangle(
            0, WINDOW_HEIGHT - 50, WINDOW_WIDTH, WINDOW_HEIGHT,
            fill=GROUND_COLOR, outline=""
        )

    def draw_cloud(self, x, y):
        # Nuage simple
        self.canvas.create_oval(x, y, x + 40, y + 30, fill="white", outline="")
        self.canvas.create_oval(x + 20, y - 10, x + 60, y + 25, fill="white", outline="")
        self.canvas.create_oval(x + 40, y, x + 80, y + 30, fill="white", outline="")

    def show_start_screen(self):
        # Titre
        self.canvas.create_text(
            WINDOW_WIDTH // 2,
            WINDOW_HEIGHT // 2 - 100,
            text="🍟 McDONALD'S",
            font=("Arial", 48, "bold"),
            fill=RED,
            tags="start"
        )
        self.canvas.create_text(
            WINDOW_WIDTH // 2,
            WINDOW_HEIGHT // 2 - 40,
            text="FRITES CATCHER",
            font=("Arial", 36, "bold"),
            fill=YELLOW,
            tags="start"
        )
        self.canvas.create_text(
            WINDOW_WIDTH // 2,
            WINDOW_HEIGHT // 2 + 40,
            text="Clique pour commencer !",
            font=("Arial", 20),
            fill=TEXT_COLOR,
            tags="start"
        )
        self.canvas.create_text(
            WINDOW_WIDTH // 2,
            WINDOW_HEIGHT // 2 + 80,
            text="Attrape les frites avec le paquet 🍟",
            font=("Arial", 14),
            fill=TEXT_COLOR,
            tags="start"
        )

    def on_click(self, event):
        if not self.game_started:
            self.start_game()

    def start_game(self):
        self.game_started = True
        self.canvas.delete("start", "gameover")
        self.game_loop()

    def restart_game(self):
        self.frites.clear()
        self.score = 0
        self.lives = 3
        self.combo = 0
        self.max_combo = 0
        self.game_over = False
        self.game_started = False
        self.frame_count = 0
        self.paquet.x = WINDOW_WIDTH // 2
        self.paquet.target_x = WINDOW_WIDTH // 2
        self.update_score()
        self.update_lives()
        self.canvas.delete("all")
        self.draw_background()
        self.show_start_screen()

    def on_mouse_move(self, event):
        if self.game_started and not self.game_over:
            self.paquet.move_to(event.x)

    def spawn_frite(self):
        x = random.randint(50, WINDOW_WIDTH - 50)
        y = -50
        self.frites.append(Frite(x, y))

    def update_score(self):
        self.score_label.config(text=f"Score: {self.score}")

    def update_lives(self):
        hearts = "❤️ " * self.lives
        self.lives_label.config(text=hearts.strip())

    def draw_paquet(self):
        x, y = self.paquet.x, self.paquet.y
        w, h = self.paquet.width, self.paquet.height

        # Ombre
        self.canvas.create_oval(
            x - w // 2 + 5, y + h // 2 - 5,
            x + w // 2 + 5, y + h // 2 + 10,
            fill="gray", outline="", stipple="gray50", tags="paquet"
        )

        # Corps du paquet (rouge)
        points = [
            x - w // 2, y - h // 2 + 20,  # Haut gauche
            x + w // 2, y - h // 2 + 20,  # Haut droit
            x + w // 2 - 5, y + h // 2,   # Bas droit
            x - w // 2 + 5, y + h // 2    # Bas gauche
        ]
        self.canvas.create_polygon(points, fill=RED, outline="#B71C1C", width=2, tags="paquet")

        # Partie supérieure (ouverture)
        self.canvas.create_rectangle(
            x - w // 2, y - h // 2,
            x + w // 2, y - h // 2 + 25,
            fill="#C41E3A", outline="#B71C1C", width=2, tags="paquet"
        )

        # Logo M de McDonald's
        self.canvas.create_text(
            x, y,
            text="M",
            font=("Arial", 40, "bold"),
            fill=YELLOW,
            tags="paquet"
        )

        # Frites qui dépassent du paquet
        frite_positions = [
            (x - 20, y - h // 2 + 10),
            (x - 5, y - h // 2 + 5),
            (x + 10, y - h // 2 + 12),
            (x + 25, y - h // 2 + 8)
        ]

        for fx, fy in frite_positions:
            # Frite
            self.canvas.create_rectangle(
                fx - 3, fy, fx + 3, fy + 25,
                fill=FRITE_COLOR, outline=FRITE_SHADOW, width=1, tags="paquet"
            )
            # Bout de la frite plus foncé
            self.canvas.create_rectangle(
                fx - 3, fy, fx + 3, fy + 5,
                fill="#DAA520", outline="", tags="paquet"
            )

    def draw_frite(self, frite):
        # Frite qui tombe
        x, y = frite.x, frite.y

        # Corps de la frite
        points = [
            x - frite.width // 2, y,
            x + frite.width // 2, y,
            x + frite.width // 2 - 2, y + frite.height,
            x - frite.width // 2 + 2, y + frite.height
        ]

        self.canvas.create_polygon(
            points, fill=FRITE_COLOR, outline=FRITE_SHADOW, width=1, tags="frite"
        )

        # Bout foncé
        self.canvas.create_rectangle(
            x - frite.width // 2, y,
            x + frite.width // 2, y + 8,
            fill=FRITE_SHADOW, outline="", tags="frite"
        )

    def check_collision(self, frite):
        catch_rect = self.paquet.get_catch_rect()

        # Vérifier si la frite touche la zone de capture
        if (catch_rect[0] <= frite.x <= catch_rect[2] and
            catch_rect[1] <= frite.y <= catch_rect[3] + 30):
            return True
        return False

    def show_game_over(self):
        # Overlay semi-transparent
        self.canvas.create_rectangle(
            0, 0, WINDOW_WIDTH, WINDOW_HEIGHT,
            fill="black", stipple="gray50", tags="gameover"
        )

        self.canvas.create_text(
            WINDOW_WIDTH // 2,
            WINDOW_HEIGHT // 2 - 80,
            text="GAME OVER",
            font=("Arial", 50, "bold"),
            fill=RED,
            tags="gameover"
        )

        self.canvas.create_text(
            WINDOW_WIDTH // 2,
            WINDOW_HEIGHT // 2 - 10,
            text=f"Score Final: {self.score}",
            font=("Arial", 30),
            fill=YELLOW,
            tags="gameover"
        )

        if self.max_combo > 1:
            self.canvas.create_text(
                WINDOW_WIDTH // 2,
                WINDOW_HEIGHT // 2 + 30,
                text=f"Meilleur Combo: {self.max_combo}x",
                font=("Arial", 20),
                fill="white",
                tags="gameover"
            )

        self.canvas.create_text(
            WINDOW_WIDTH // 2,
            WINDOW_HEIGHT // 2 + 70,
            text="Appuyez sur R pour rejouer",
            font=("Arial", 18),
            fill="white",
            tags="gameover"
        )

    def show_combo(self):
        if self.combo > 1:
            self.canvas.delete("combo")
            self.canvas.create_text(
                WINDOW_WIDTH // 2,
                100,
                text=f"COMBO x{self.combo}!",
                font=("Arial", 30, "bold"),
                fill=YELLOW,
                tags="combo"
            )
            self.root.after(1000, lambda: self.canvas.delete("combo"))

    def game_loop(self):
        if not self.game_started or self.game_over:
            return

        self.frame_count += 1

        # Spawner des frites
        if self.frame_count % FRITE_SPAWN_RATE == 0:
            self.spawn_frite()

        # Augmenter la difficulté progressivement
        if self.frame_count % 500 == 0 and FRITE_SPAWN_RATE > 20:
            globals()['FRITE_SPAWN_RATE'] -= 2

        # Mettre à jour le paquet
        self.paquet.update()

        # Mettre à jour les frites
        frites_to_remove = []
        for frite in self.frites:
            frite.update()

            # Vérifier collision
            if self.check_collision(frite):
                frites_to_remove.append(frite)
                points = 10 + (self.combo * 5)
                self.score += points
                self.combo += 1
                self.max_combo = max(self.max_combo, self.combo)
                self.update_score()
                self.show_combo()

            # Frite tombée au sol
            elif frite.is_off_screen():
                frites_to_remove.append(frite)
                self.lives -= 1
                self.combo = 0
                self.update_lives()

                if self.lives <= 0:
                    self.game_over = True
                    self.show_game_over()
                    return

        # Retirer les frites capturées ou tombées
        for frite in frites_to_remove:
            self.frites.remove(frite)

        # Redessiner
        self.canvas.delete("paquet", "frite")
        self.draw_paquet()
        for frite in self.frites:
            self.draw_frite(frite)

        # Continuer la boucle
        self.root.after(GAME_SPEED, self.game_loop)


if __name__ == "__main__":
    root = tk.Tk()
    game = FritesGame(root)
    root.mainloop()
