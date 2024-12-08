import pygame
import random
import time

# Konfigurasi awal
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 800
CAR_WIDTH = 50
CAR_HEIGHT = 100
WHITE = (255, 255, 255)
ROAD_COLOR = (50, 50, 50)
CENTER_LINE_COLOR = (255, 255, 255)
BORDER_WIDTH = 10

# Koordinat X untuk jalur
LANE_COUNT = 6  # Total 6 jalur (3 kiri, 3 kanan)
LANE_WIDTH = (SCREEN_WIDTH - 2 * BORDER_WIDTH) // LANE_COUNT
LANES = [BORDER_WIDTH + LANE_WIDTH * i + (LANE_WIDTH - CAR_WIDTH) // 2 for i in range(LANE_COUNT)]

# Inisialisasi Pygame
pygame.init()

# Buat layar
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Game Mobil - Hindari Tabrakan")

# Memuat gambar mobil pemain
player_car_image = pygame.image.load('player_car.png')
player_car_image = pygame.transform.scale(player_car_image, (CAR_WIDTH, CAR_HEIGHT))

# Memuat gambar kendaraan musuh
enemy_car_images = [
    pygame.image.load('enemy_car1.png'),
    pygame.image.load('enemy_car2.png'),
    pygame.image.load('enemy_car3.png'),
    pygame.image.load('enemy_car4.png'),
]
enemy_car_images = [pygame.transform.scale(img, (CAR_WIDTH, CAR_HEIGHT)) for img in enemy_car_images]

# Memuat suara mobil berjalan
car_engine_sound = pygame.mixer.Sound('car_engine.mp3')
car_engine_sound.set_volume(2.5)  # Sesuaikan volume suara (0.0 - 1.0)

# Class abstraksi kendaraan
class Vehicle:
    def __init__(self, x, y, width, height, speed, image):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.speed = speed
        self.image = image

    def move(self):
        raise NotImplementedError("Subclass harus mengimplementasikan metode ini.")

    def draw(self):
        raise NotImplementedError("Subclass harus mengimplementasikan metode ini.")

# Class mobil pemain
class PlayerCar(Vehicle):
    def __init__(self, x, y, width, height, speed):
        super().__init__(x, y, width, height, speed, player_car_image)

    def move(self, keys):
        if keys[pygame.K_LEFT] and self.x > BORDER_WIDTH:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < SCREEN_WIDTH - self.width - BORDER_WIDTH:
            self.x += self.speed
        if keys[pygame.K_UP] and self.y > 0:
            self.y -= self.speed
        if keys[pygame.K_DOWN] and self.y < SCREEN_HEIGHT - self.height:
            self.y += self.speed

    def draw(self):
        screen.blit(self.image, (self.x, self.y))

# Class kendaraan musuh
class EnemyCar(Vehicle):
    def __init__(self, x, y, width, height, speed, image):
        super().__init__(x, y, width, height, speed, image)

    def move(self):
        self.y += self.speed

    def draw(self):
        screen.blit(self.image, (self.x, self.y))

# Class Game
class Game:
    def __init__(self):
        self.player = PlayerCar(SCREEN_WIDTH // 2 - CAR_WIDTH // 2, SCREEN_HEIGHT - CAR_HEIGHT - 10, CAR_WIDTH, CAR_HEIGHT, 5)
        self.enemies = []
        self.score = 0
        self.start_time = time.time()
        self.clock = pygame.time.Clock()
        self.level = 1
        self.enemy_speed_increase = 0.5
        self.enemy_spawn_rate = 2
        self.max_enemies = 5
        self.mark_offset = 0  # Offset untuk menggerakkan garis tengah

    def create_enemy(self):
        if len(self.enemies) < self.max_enemies:
            if random.randint(0, 100) < self.enemy_spawn_rate + self.level * 2:
                enemy_lane = random.choice(LANES)  # Pilih jalur acak
                enemy_speed = random.randint(3, 7) + self.level * self.enemy_speed_increase
                enemy_image = random.choice(enemy_car_images if self.level % 2 == 0 else enemy_car_images[2:])  # Pilih gambar musuh sesuai level
                enemy = EnemyCar(enemy_lane, -CAR_HEIGHT, CAR_WIDTH, CAR_HEIGHT, enemy_speed, enemy_image)
                self.enemies.append(enemy)

    def update(self):
        keys = pygame.key.get_pressed()
        self.player.move(keys)

        # Pergerakan musuh
        for enemy in self.enemies:
            enemy.move()
            if enemy.y > SCREEN_HEIGHT:
                self.enemies.remove(enemy)
                self.score += 1

        # Update level setiap kelipatan 50 skor
        if self.score // 50 + 1 > self.level:
            self.level += 1
            self.max_enemies += 1  # Tambahkan jumlah musuh
            self.enemy_speed_increase += 0.5  # Tingkatkan kecepatan musuh

        # Update posisi mark jalan
        self.mark_offset += 5
        if self.mark_offset >= 40:
            self.mark_offset = 0

    def draw_road(self):
        if self.level == 2:
            road_color = (30, 30, 30)  # Gelap untuk mode malam
            line_color = (100, 100, 100)
        elif self.level == 4:
            road_color = (200, 200, 200)  # Terang untuk mode siang
            line_color = (0, 0, 0)
        else:
            road_color = ROAD_COLOR
            line_color = CENTER_LINE_COLOR

        pygame.draw.rect(screen, road_color, (BORDER_WIDTH, 0, SCREEN_WIDTH - 2 * BORDER_WIDTH, SCREEN_HEIGHT))
        for y in range(-40, SCREEN_HEIGHT, 40):
            pygame.draw.line(screen, line_color, 
                             (SCREEN_WIDTH // 2, y + self.mark_offset), 
                             (SCREEN_WIDTH // 2, y + 20 + self.mark_offset), 5)
        pygame.draw.rect(screen, WHITE, (BORDER_WIDTH, 0, BORDER_WIDTH, SCREEN_HEIGHT))
        pygame.draw.rect(screen, WHITE, (SCREEN_WIDTH - BORDER_WIDTH, 0, BORDER_WIDTH, SCREEN_HEIGHT))

    def draw(self):
        screen.fill((0, 0, 0))
        self.draw_road()
        self.player.draw()
        for enemy in self.enemies:
            enemy.draw()
        self.create_enemy()
        font = pygame.font.SysFont("Arial", 30)
        score_text = font.render(f"Skor: {self.score}  Level: {self.level}", True, WHITE)
        screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 20))
        pygame.display.update()

    def display_game_over(self):
        font = pygame.font.SysFont("Arial", 50)
        game_over_text = font.render("GAME OVER", True, WHITE)
        replay_text = pygame.font.SysFont("Arial", 30).render("Press R to Replay or Q to Quit", True, WHITE)
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
        screen.blit(replay_text, (SCREEN_WIDTH // 2 - replay_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))
        pygame.display.update()

    def handle_replay(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:  # Tekan "R" untuk replay
                        car_engine_sound.play(-1)  # Mulai ulang suara
                        self.__init__()  # Reset game dengan menginisialisasi ulang
                        return True
                    if event.key == pygame.K_q:  # Tekan "Q" untuk keluar
                        return False

    def main_menu(self):
        font = pygame.font.SysFont("Arial", 50)
        title_text = font.render("MOBIL HINDARI TABRAKAN", True, WHITE)
        start_text = pygame.font.SysFont("Arial", 30).render("Press ENTER to Start", True, WHITE)
        running = True
        while running:
            screen.fill((0, 0, 0))
            screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 2 - 100))
            screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, SCREEN_HEIGHT // 2))
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:  # Tekan ENTER untuk mulai
                        running = False

    def game_loop(self):
        self.main_menu()
        car_engine_sound.play(-1)  # Memulai suara mesin mobil
        running = True
        while running:
            self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.update()
            self.draw()

            if self.check_collision():
                print(f"Game Over! Skor: {self.score}  Level: {self.level}")
                car_engine_sound.stop()  # Hentikan suara jika kalah
                self.display_game_over()
                running = self.handle_replay()

    def check_collision(self):
        for enemy in self.enemies:
            if (self.player.x < enemy.x + enemy.width and
                self.player.x + self.player.width > enemy.x and
                self.player.y < enemy.y + enemy.height and
                self.player.y + self.player.height > enemy.y):
                return True
        return False

# Jalankan permainan
if __name__ == "__main__":
    game = Game()
    game.game_loop()
    car_engine_sound.stop()  # Hentikan suara saat keluar dari permainan
    pygame.quit()
