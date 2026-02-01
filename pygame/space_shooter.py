import pygame
import os
import time
import random

def draw_play_button(window,mouse_pos):
    font = pygame.font.SysFont("comicsans",40)

    button_rect = pygame.Rect(WIDTH//2 -100,HEIGHT//2-40,200,80)


    if button_rect.collidepoint(mouse_pos):
        pygame.draw.rect(window,(0,255,0), button_rect)
    else:
        pygame.draw.rect(window,(0,200,0), button_rect)

    text = font.render("Play", True, (0,0,0))
    window.blit(text,(button_rect.x + button_rect.width // 2 - text.get_width() //2, button_rect.y + button_rect.height//2 - text.get_height() // 2))

    return button_rect

def draw_highscore_button(window,mouse_pos):
    font = pygame.font.SysFont("comicsans", 32 )

    button_rect = pygame.Rect(WIDTH//2 -100, HEIGHT//2 +60,200,70)

    if button_rect.collidepoint(mouse_pos):
        pygame.draw.rect(window, (0,150,255), button_rect)

    else:
        pygame.draw.rect(window,(0,120,200), button_rect)

    text = font.render("HIGHSCORE", True,(0,0,0))
    window.blit(
        text,(button_rect.x + button_rect.width//2 - text.get_width()//2,button_rect.y + button_rect.height//2 - text.get_height()//2)
    )

    return button_rect


def load_highscore():
    if not os.path.exists("highscores.txt"):
        return 0
    with open("highscores.txt", "r") as f:
        return int(f.read())


def save_highscore(score):
    with open("highscores.txt", "w") as f:
        f.write(str(score))

pygame.init()
score = 0
pygame.font.init()

WIDTH, HEIGHT = 1280, 720
WINDOW = pygame.display.set_mode((WIDTH , HEIGHT))
pygame.display.set_caption("Space mein Dhoom Dhadaka")

# Loading spaceShip images

GREEN_SPACE_SHIP = pygame.image.load(os.path.join("assets","images","pixel_ship_green_small.png"))
ENEMY_1_SPACE_SHIP = pygame.image.load(os.path.join("assets","images","enemy-1.png"))
ENEMY_2_SPACE_SHIP = pygame.image.load(os.path.join("assets","images","enemy 2.jpg"))

# Player ship
CHARACTER_MAIN_SPACE_SHIP = pygame.image.load(os.path.join("assets","images","character main.jpg"))

# Lasers
RED_LASERS = pygame.image.load(os.path.join("assets","images", "pixel_laser_red.png"))
GREEN_LASERS = pygame.image.load(os.path.join("assets","images", "pixel_laser_green.png"))
BLUE_LASERS = pygame.image.load(os.path.join("assets","images", "pixel_laser_blue.png"))
MAIN_LASERS = pygame.image.load(os.path.join("assets","images", "pixel_laser_yellow.png"))

# BACKGROUND
BG = pygame.transform.scale(
    pygame.image.load(os.path.join("assets", "images", "background-black.png")),
    (WIDTH, HEIGHT))

class Laser:
    def __init__(self,x,y,img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self,window):
        window.blit(self.img,(self.x,self.y))

    def move(self,vel):
        self.y += vel

    def off_screen(self,height):
        return not (self.y <= height and self.y >= 0)

    def collsion(self,obj):
        return collide(self, obj)


class Ship:
    COOLDOWN = 20

    def __init__(self,x,y,health =100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self,window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self,vel,obj):
        self.cooldown()
        for laser in self.lasers[:]:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collsion(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(
                self.x + self.get_width() // 2 - self.laser_img.get_width()//2,
                self.y,
                self.laser_img
            )
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()

class Player(Ship):
    def __init__(self,x,y,health = 150):
        super().__init__(x,y,health)

        self.ship_img = pygame.transform.scale(CHARACTER_MAIN_SPACE_SHIP,(60,80))
        self.laser_img = MAIN_LASERS
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health
        self.fire_rate = 10    #ISSE KUCH CONTROL NAi hora confuse mt hona
        self.fire_speed = 7


    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x + self.get_width()//2 - self.laser_img.get_width()//2,self.y,self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1


    def move_lasers(self,vel,objs):
        global score
        self.cooldown()
        for laser in self.lasers[:]:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collsion(obj):
                        objs.remove(obj)
                        self.lasers.remove(laser)
                        score += 1


    def draw(self,window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self,window):
        pygame.draw.rect(WINDOW, (255,0,0),
            (self.x,self.y + self.ship_img.get_height() + 10,
             self.ship_img.get_width() ,10))
        pygame.draw.rect(WINDOW, (0,255,0),
            (self.x, self.y + self.ship_img.get_height() + 10,
             self.ship_img.get_width() *
             (1-((self.max_health - self.health)/self.max_health )), 10))

class Enemy(Ship):
    COLOR_MAP = {
        "red": (ENEMY_2_SPACE_SHIP, RED_LASERS),
        "green": (GREEN_SPACE_SHIP, GREEN_LASERS),
        "blue": (ENEMY_1_SPACE_SHIP, BLUE_LASERS)
    }

    def __init__(self,x,y,color, health = 150):
        super().__init__(x,y,health)
        ship_img, laser_img = self.COLOR_MAP[color]
        self.ship_img,self.laser_img = self.COLOR_MAP[color]
        self.ship_img = pygame.transform.scale(ship_img, (50, 50))
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self,vel):
        self.y += vel

def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask,(offset_x,offset_y)) != None

def main():
    global score
    score = 0
    highscore = load_highscore()
    running = True
    FPS = 90
    level = 0
    lives = 5
    main_font = pygame.font.SysFont("timesnewroman", 40)
    lost_font = pygame.font.SysFont("comicsans", 70)
    enemies = []
    wave_length = 2

    player_vel = 5
    enemy_vel = 1
    laser_vel = 10

    ship = Player(600,600)

    clock = pygame.time.Clock()
    lost = False
    lost_count = 0

    def redraw_window():
        WINDOW.blit(BG, (0, 0))

        high_label = main_font.render(f"High: {highscore}", 1,(255,255,255))
        WINDOW.blit(high_label, (10,50))

        lives_label = main_font.render(f"Lives: {lives}", 1, (255,0,0))
        level_label = main_font.render(f"Level: {level}", 1, (255,255,255))
        WINDOW.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))
        WINDOW.blit(lives_label, (WIDTH - lives_label.get_width() - 10, 60))
        score_label = main_font.render(f"score: {score}", 1,(255,255,0))
        WINDOW.blit(score_label, (10,10))

        for enemy in enemies:
            enemy.draw(WINDOW)

        ship.draw(WINDOW)

        if lost:
            lost_label = lost_font.render("HAAR GYA BOT!!", 9,(255,255,255))
            WINDOW.blit(lost_label,(WIDTH/2 - lost_label.get_width()/2,350))

        pygame.display.update()

    while running:
        clock.tick(FPS)
        redraw_window()

        if lives <= 0 or ship.health <= 0:
            if score > highscore:
                highscore = score
                save_highscore(highscore)
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                running = False
            else:
                continue

        if len(enemies) == 0:
            level += 1
            wave_length += 7
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50,WIDTH-100),
                              random.randrange(-1600, -100),
                              random.choice(["red","green","blue"]))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        if (keys[pygame.K_d] or keys[pygame.K_RIGHT]) and ship.x + ship.get_width() +5< WIDTH:
            ship.x += player_vel

        if (keys[pygame.K_a] or keys[pygame.K_LEFT]) and ship.x > 0 +5:
            ship.x -= player_vel

        if (keys[pygame.K_w] or keys[pygame.K_UP]) and ship.y > 0 + 5:
            ship.y -= player_vel

        if (keys[pygame.K_s] or keys[pygame.K_DOWN]) and ship.y + ship.get_height() +25 < HEIGHT:
            ship.y += player_vel

        if keys[pygame.K_SPACE] and ship.cool_down_counter == 0:
            ship.shoot()

        for enemy in enemies:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel,ship)

            if random.randrange(0, 4*60) == 1:
                enemy.shoot()

            if collide(enemy, ship):
                ship.health -= 10
                enemies.remove(enemy)

            if enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)




        ship.move_lasers(-ship.fire_speed ,enemies)

    return

def show_highscore():
    running = True
    font = pygame.font.SysFont("comicsans", 50)
    small_font = pygame.font.SysFont("comicsans", 30)
    clock = pygame.time.Clock()

    highscore = load_highscore()

    while running:
        clock.tick(60)
        WINDOW.blit(BG, (0, 0))

        title = font.render("HIGHSCORE", True, (255,255,0))
        score_text = font.render(str(highscore), True, (0,255,255))
        back_text = small_font.render("Press ESC to go back", True, (255,255,255))

        WINDOW.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//3))
        WINDOW.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2))
        WINDOW.blit(back_text, (WIDTH//2 - back_text.get_width()//2, HEIGHT//2 + 80))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return


def main_menu():
    title_font = pygame.font.SysFont("comicsans", 50)
    running = True
    clock = pygame.time.Clock()

    while running:
        clock.tick(60)
        WINDOW.blit(BG, (0,0))

        mouse_pos = pygame.mouse.get_pos()
        play_button = draw_play_button(WINDOW, mouse_pos)

        mouse_pos = pygame.mouse.get_pos()
        play_button = draw_play_button(WINDOW, mouse_pos)
        highscore_button = draw_highscore_button(WINDOW, mouse_pos)


        title_label = title_font.render("PLAY DABA", True, (255,255,0))
        WINDOW.blit(
            title_label,
            (WIDTH//2 - title_label.get_width()//2, HEIGHT//4)
        )

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_button.collidepoint(mouse_pos):
                    main()
                    running = False

                if highscore_button.collidepoint(mouse_pos):
                    show_highscore()

    pygame.quit()


main_menu()
