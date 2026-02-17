import tkinter as tk
import random
from collections import deque

# Constantes
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 600
GRID_SIZE = 20
GRID_WIDTH = WINDOW_WIDTH // GRID_SIZE
GRID_HEIGHT = WINDOW_HEIGHT // GRID_SIZE
GAME_SPEED = 150  # ms entre chaque mouvement

# Couleurs
BG_COLOR = "#1a1a2e"
BG_COLOR_ALT = "#16213e"
SNAKE_HEAD = "#0f3460"
SNAKE_BODY = "#16a085"
FOOD_COLOR = "#e94560"
TEXT_COLOR = "#eee"
ACCENT_COLOR = "#f39c12"

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)


class SnakeGame:
    def __init__(self, root):
        self.root = root
        self.root.title("🐍 Snake Game")
        self.root.configure(bg=BG_COLOR)
        self.root.resizable(True, True)  # Fenêtre redimensionnable

        # Définir une taille minimale
        self.root.minsize(500, 500)

        # Variables pour le plein écran
        self.is_fullscreen = False

        # Bindings pour le plein écran
        self.root.bind("<F11>", self.toggle_fullscreen)
        self.root.bind("<Escape>", self.exit_fullscreen)

        # Frame principal
        self.main_frame = tk.Frame(root, bg=BG_COLOR)
        self.main_frame.pack(padx=20, pady=20)

        # Score
        self.score_label = tk.Label(
            self.main_frame,
            text="Score: 0",
            font=("Arial", 20, "bold"),
            bg=BG_COLOR,
            fg=TEXT_COLOR
        )
        self.score_label.pack(pady=(0, 10))

        # Canvas
        self.canvas = tk.Canvas(
            self.main_frame,
            width=WINDOW_WIDTH,
            height=WINDOW_HEIGHT,
            bg=BG_COLOR,
            highlightthickness=2,
            highlightbackground=ACCENT_COLOR
        )
        self.canvas.pack()

        # Instructions
        self.instructions = tk.Label(
            self.main_frame,
            text="Flèches pour jouer • ESPACE pour pause • R pour recommencer • F11 pour plein écran",
            font=("Arial", 10),
            bg=BG_COLOR,
            fg=ACCENT_COLOR
        )
        self.instructions.pack(pady=(10, 0))

        # Variables du jeu
        self.snake = deque()
        self.direction = RIGHT
        self.next_direction = RIGHT
        self.food_pos = None
        self.score = 0
        self.game_over = False
        self.paused = False
        self.game_started = False

        # Bindings
        self.root.bind("<Up>", lambda e: self.change_direction(UP))
        self.root.bind("<Down>", lambda e: self.change_direction(DOWN))
        self.root.bind("<Left>", lambda e: self.change_direction(LEFT))
        self.root.bind("<Right>", lambda e: self.change_direction(RIGHT))
        self.root.bind("<space>", lambda e: self.toggle_pause())
        self.root.bind("r", lambda e: self.restart_game())
        self.root.bind("R", lambda e: self.restart_game())

        # Dessiner la grille
        self.draw_grid()

        # Afficher écran d'accueil
        self.show_start_screen()

    def toggle_fullscreen(self, event=None):
        """Active/désactive le mode plein écran"""
        self.is_fullscreen = not self.is_fullscreen
        self.root.attributes("-fullscreen", self.is_fullscreen)
        return "break"

    def exit_fullscreen(self, event=None):
        """Quitte le mode plein écran"""
        if self.is_fullscreen:
            self.is_fullscreen = False
            self.root.attributes("-fullscreen", False)
            return "break"

    def draw_grid(self):
        """Dessine la grille en damier"""
        for row in range(GRID_HEIGHT):
            for col in range(GRID_WIDTH):
                x1 = col * GRID_SIZE
                y1 = row * GRID_SIZE
                x2 = x1 + GRID_SIZE
                y2 = y1 + GRID_SIZE

                color = BG_COLOR_ALT if (row + col) % 2 == 0 else BG_COLOR
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")

    def show_start_screen(self):
        """Affiche l'écran de démarrage"""
        self.canvas.create_text(
            WINDOW_WIDTH // 2,
            WINDOW_HEIGHT // 2 - 40,
            text="🐍 SNAKE GAME 🐍",
            font=("Arial", 32, "bold"),
            fill=ACCENT_COLOR,
            tags="start"
        )
        self.canvas.create_text(
            WINDOW_WIDTH // 2,
            WINDOW_HEIGHT // 2 + 20,
            text="Appuyez sur une flèche pour commencer",
            font=("Arial", 14),
            fill=TEXT_COLOR,
            tags="start"
        )

    def init_game(self):
        """Initialise le jeu"""
        self.snake = deque([(GRID_WIDTH // 2, GRID_HEIGHT // 2)])
        self.direction = RIGHT
        self.next_direction = RIGHT
        self.score = 0
        self.game_over = False
        self.paused = False
        self.game_started = True
        self.update_score()
        self.spawn_food()
        self.canvas.delete("start", "gameover", "pause")
        self.game_loop()

    def restart_game(self):
        """Redémarre le jeu"""
        self.canvas.delete("all")
        self.draw_grid()
        self.init_game()

    def toggle_pause(self):
        """Active/désactive la pause"""
        if self.game_started and not self.game_over:
            self.paused = not self.paused
            if self.paused:
                self.show_pause_screen()
            else:
                self.canvas.delete("pause")
                self.game_loop()

    def show_pause_screen(self):
        """Affiche l'écran de pause"""
        overlay = self.canvas.create_rectangle(
            0, 0, WINDOW_WIDTH, WINDOW_HEIGHT,
            fill=BG_COLOR,
            stipple="gray50",
            tags="pause"
        )
        self.canvas.create_text(
            WINDOW_WIDTH // 2,
            WINDOW_HEIGHT // 2,
            text="⏸ PAUSE",
            font=("Arial", 40, "bold"),
            fill=ACCENT_COLOR,
            tags="pause"
        )

    def change_direction(self, new_direction):
        """Change la direction du serpent"""
        if not self.game_started:
            self.init_game()
            return

        # Empêcher le demi-tour
        if (new_direction[0] * -1, new_direction[1] * -1) != self.direction:
            self.next_direction = new_direction

    def spawn_food(self):
        """Fait apparaître la nourriture"""
        while True:
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(0, GRID_HEIGHT - 1)
            if (x, y) not in self.snake:
                self.food_pos = (x, y)
                break

    def move_snake(self):
        """Déplace le serpent"""
        self.direction = self.next_direction
        head_x, head_y = self.snake[0]
        new_head = (head_x + self.direction[0], head_y + self.direction[1])

        # Vérifier collision avec les murs
        if (new_head[0] < 0 or new_head[0] >= GRID_WIDTH or
            new_head[1] < 0 or new_head[1] >= GRID_HEIGHT):
            return False

        # Vérifier collision avec soi-même
        if new_head in self.snake:
            return False

        self.snake.appendleft(new_head)

        # Vérifier si la nourriture est mangée
        if new_head == self.food_pos:
            self.score += 10
            self.update_score()
            self.spawn_food()
        else:
            self.snake.pop()

        return True

    def update_score(self):
        """Met à jour l'affichage du score"""
        self.score_label.config(text=f"Score: {self.score}")

    def draw_game(self):
        """Dessine le jeu"""
        self.canvas.delete("snake", "food")

        # Dessiner la nourriture avec effet de brillance
        if self.food_pos:
            x, y = self.food_pos
            margin = 3
            self.canvas.create_oval(
                x * GRID_SIZE + margin,
                y * GRID_SIZE + margin,
                (x + 1) * GRID_SIZE - margin,
                (y + 1) * GRID_SIZE - margin,
                fill=FOOD_COLOR,
                outline="",
                tags="food"
            )
            # Reflet
            self.canvas.create_oval(
                x * GRID_SIZE + 6,
                y * GRID_SIZE + 6,
                x * GRID_SIZE + 10,
                y * GRID_SIZE + 10,
                fill="#ff6b81",
                outline="",
                tags="food"
            )

        # Dessiner le serpent
        for i, (x, y) in enumerate(self.snake):
            margin = 2
            color = SNAKE_HEAD if i == 0 else SNAKE_BODY

            self.canvas.create_rectangle(
                x * GRID_SIZE + margin,
                y * GRID_SIZE + margin,
                (x + 1) * GRID_SIZE - margin,
                (y + 1) * GRID_SIZE - margin,
                fill=color,
                outline="",
                tags="snake"
            )

            # Yeux sur la tête
            if i == 0:
                eye_size = 3
                if self.direction == RIGHT:
                    eye1 = (x * GRID_SIZE + 14, y * GRID_SIZE + 7)
                    eye2 = (x * GRID_SIZE + 14, y * GRID_SIZE + 13)
                elif self.direction == LEFT:
                    eye1 = (x * GRID_SIZE + 6, y * GRID_SIZE + 7)
                    eye2 = (x * GRID_SIZE + 6, y * GRID_SIZE + 13)
                elif self.direction == UP:
                    eye1 = (x * GRID_SIZE + 7, y * GRID_SIZE + 6)
                    eye2 = (x * GRID_SIZE + 13, y * GRID_SIZE + 6)
                else:  # DOWN
                    eye1 = (x * GRID_SIZE + 7, y * GRID_SIZE + 14)
                    eye2 = (x * GRID_SIZE + 13, y * GRID_SIZE + 14)

                self.canvas.create_oval(
                    eye1[0] - eye_size, eye1[1] - eye_size,
                    eye1[0] + eye_size, eye1[1] + eye_size,
                    fill="#fff",
                    tags="snake"
                )
                self.canvas.create_oval(
                    eye2[0] - eye_size, eye2[1] - eye_size,
                    eye2[0] + eye_size, eye2[1] + eye_size,
                    fill="#fff",
                    tags="snake"
                )

    def show_game_over(self):
        """Affiche l'écran de game over"""
        overlay = self.canvas.create_rectangle(
            0, 0, WINDOW_WIDTH, WINDOW_HEIGHT,
            fill=BG_COLOR,
            stipple="gray50",
            tags="gameover"
        )
        self.canvas.create_text(
            WINDOW_WIDTH // 2,
            WINDOW_HEIGHT // 2 - 60,
            text="💀 GAME OVER 💀",
            font=("Arial", 36, "bold"),
            fill=FOOD_COLOR,
            tags="gameover"
        )
        self.canvas.create_text(
            WINDOW_WIDTH // 2,
            WINDOW_HEIGHT // 2,
            text=f"Score Final: {self.score}",
            font=("Arial", 24),
            fill=TEXT_COLOR,
            tags="gameover"
        )
        self.canvas.create_text(
            WINDOW_WIDTH // 2,
            WINDOW_HEIGHT // 2 + 50,
            text="Appuyez sur R pour rejouer",
            font=("Arial", 16),
            fill=ACCENT_COLOR,
            tags="gameover"
        )

    def game_loop(self):
        """Boucle principale du jeu"""
        if self.game_over or self.paused:
            return

        if not self.move_snake():
            self.game_over = True
            self.show_game_over()
            return

        self.draw_game()
        self.root.after(GAME_SPEED, self.game_loop)


if __name__ == "__main__":
    root = tk.Tk()
    game = SnakeGame(root)
    root.mainloop()
