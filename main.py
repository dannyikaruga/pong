import pygame
import random

# Inicializar Pygame
pygame.init()

# Definir colores
WHITE = (255, 255, 255)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)

# Tamaño de la pantalla
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong Geometry Wars Style")

# Fuente para el texto
font = pygame.font.SysFont('Arial', 36)

# Cargar sonidos
bounce_sound = pygame.mixer.Sound('bounce.wav')  # Rebote
score_sound = pygame.mixer.Sound('score.wav')    # Anotación

# Partículas de fondo
particles = [{"x": random.randint(0, WIDTH), "y": random.randint(0, HEIGHT), "size": random.randint(2, 5)} for _ in range(50)]

# Clase Paddle (Raqueta)
class Paddle(pygame.sprite.Sprite):
    def __init__(self, color, x, y):
        super().__init__()
        self.image = pygame.Surface((15, 100))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self, up_key=None, down_key=None, ball=None, difficulty=1):
        if ball:
            if ball.rect.centery > self.rect.centery:
                self.rect.y += 4 * difficulty
            elif ball.rect.centery < self.rect.centery:
                self.rect.y -= 4 * difficulty
        else:
            keys = pygame.key.get_pressed()
            if keys[up_key]:
                self.rect.y -= 5
            if keys[down_key]:
                self.rect.y += 5
        self.rect.y = max(0, min(self.rect.y, HEIGHT - self.rect.height))

# Clase Ball (Pelota)
class Ball(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((15, 15))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        self.velocity = [random.choice([-4, 4]), random.choice([-4, 4])]

    def update(self, paddle1, paddle2):
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]

        # Rebote en la parte superior e inferior
        if self.rect.top <= 0 or self.rect.bottom >= HEIGHT:
            self.velocity[1] = -self.velocity[1]
            bounce_sound.play()

        # Rebote en las raquetas
        if self.rect.colliderect(paddle1.rect) or self.rect.colliderect(paddle2.rect):
            self.velocity[0] = -self.velocity[0]
            bounce_sound.play()

        if self.rect.left <= 0 or self.rect.right >= WIDTH:
            score_sound.play()
            return True
        return False

# Menú de selección de dificultad
def difficulty_menu():
    while True:
        draw_background()
        draw_text("Select Difficulty", YELLOW, WIDTH // 4, HEIGHT // 4)
        draw_text("Press 1 for Easy", CYAN, WIDTH // 4, HEIGHT // 2)
        draw_text("Press 2 for Medium", MAGENTA, WIDTH // 4, HEIGHT // 2 + 50)
        draw_text("Press 3 for Hard", WHITE, WIDTH // 4, HEIGHT // 2 + 100)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return 1  # Fácil
                if event.key == pygame.K_2:
                    return 2  # Medio
                if event.key == pygame.K_3:
                    return 3  # Difícil


# Dibujar fondo dinámico
def draw_background():
    screen.fill(BLACK)
    for particle in particles:
        pygame.draw.circle(screen, WHITE, (particle["x"], particle["y"]), particle["size"])
        particle["y"] += random.randint(1, 3)
        if particle["y"] > HEIGHT:
            particle["y"] = 0
            particle["x"] = random.randint(0, WIDTH)

# Mostrar texto
def draw_text(text, color, x, y):
    label = font.render(text, True, color)
    screen.blit(label, (x, y))

# Menú de pausa
def pause_menu():
    while True:
        draw_background()
        draw_text("Paused", YELLOW, WIDTH // 3, HEIGHT // 4)
        draw_text("Press C to Continue", CYAN, WIDTH // 4, HEIGHT // 2)
        draw_text("Press M for Main Menu", MAGENTA, WIDTH // 4, HEIGHT // 2 + 50)
        draw_text("Press Q to Quit", WHITE, WIDTH // 4, HEIGHT // 2 + 100)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    return  # Continuar el juego
                if event.key == pygame.K_m:
                    main_menu()  # Volver al menú principal
                if event.key == pygame.K_q:
                    pygame.quit()
                    exit()

# Función del juego
def game(selected_players, difficulty):
    paddle1 = Paddle(CYAN, 50, HEIGHT // 2 - 50)
    paddle2 = Paddle(MAGENTA, WIDTH - 65, HEIGHT // 2 - 50)
    ball = Ball()

    all_sprites = pygame.sprite.Group()
    all_sprites.add(paddle1, paddle2, ball)

    score1, score2 = 0, 0
    clock = pygame.time.Clock()

    while True:
        draw_background()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pause_menu()

        paddle1.update(pygame.K_w, pygame.K_s)
        if selected_players == 1:
            paddle2.update(ball=ball, difficulty=difficulty)
        else:
            paddle2.update(pygame.K_UP, pygame.K_DOWN)

        if ball.update(paddle1, paddle2):
            if ball.rect.left <= 0:
                score2 += 1
            elif ball.rect.right >= WIDTH:
                score1 += 1
            ball.rect.center = (WIDTH // 2, HEIGHT // 2)
            ball.velocity = [random.choice([-4, 4]), random.choice([-4, 4])]

        # Comprobar si alguien ha llegado a 10 puntos
        if score1 == 10 or score2 == 10:
            draw_text("Game Over!", WHITE, WIDTH // 2, HEIGHT // 4)
            draw_text(f"Final Score: {score1} - {score2}", WHITE, WIDTH // 2, HEIGHT // 2)
            pygame.display.flip()
            pygame.time.wait(2000)  # Esperar 2 segundos para mostrar el resultado
            return  # Regresar al menú principal

        draw_text(f"Player 1: {score1}", CYAN, 20, 20)
        draw_text(f"Player 2: {score2}", MAGENTA, WIDTH - 200, 20)

        all_sprites.draw(screen)
        pygame.display.flip()
        clock.tick(60)

# Menú principal
def main_menu():
    while True:
        draw_background()
        draw_text("Hyper Pong", YELLOW, WIDTH // 4, HEIGHT // 4)
        draw_text("Press 1 for 1 Player", CYAN, WIDTH // 4, HEIGHT // 2)
        draw_text("Press 2 for 2 Players", MAGENTA, WIDTH // 4, HEIGHT // 2 + 50)
        draw_text("Press ESC to Quit", WHITE, WIDTH // 4, HEIGHT // 2 + 100)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    difficulty = difficulty_menu()
                    game(1, difficulty)
                if event.key == pygame.K_2:
                    game(2, 1)
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()

if __name__ == "__main__":
    main_menu()
