import pgzrun
import time
import random
import math
from pygame import Rect

# variaveis globais
game_started = False
show_menu = True
music_on = True
end_time = None
selecting = sounds.select
jumping = sounds.jump_high
damage = sounds.hurt

# Musica de fundo
if music_on:
    sounds.time_for_adventure.play()

# ConfiguraÃ§Ãµes do jogo
WIDTH = 800
HEIGHT = 600
GVT = 0.5
JUMP_STRENGTH = -11
MOVE_SPD = 3
TITLE = "Nebula Jumper"

# Define o chÃ£o e plataformas
GROUND_RECT = Rect((0, 570), (WIDTH, 50))

PLATFORMS = [
    Rect((165, 480), (150, 20)),
    Rect((440, 400), (200, 20)),
    Rect((90, 320), (250, 20)),
    Rect((400, 240), (150, 20)),
    Rect((600, 160), (200, 20))
]

# Vida do jogador
NUM_LIVES = 3
lives = NUM_LIVES
game_over = False
won = False

# Classes do jogo
class Player:
    def __init__(self, idle_images, walk_images, position):
        self.idle_images = idle_images
        self.walk_images = walk_images
        self.actor = Actor(self.idle_images[0], pos=position)
        self.vertical_speed = 0
        self.on_ground = True
        self.facing_right = True
        self.state = "idle"
        self.anim_index = 0
        self.anim_timer = 0

    def apply_gravity(self):
        self.vertical_speed += GVT
        self.actor.y += self.vertical_speed
        player_rect = Rect((self.actor.left, self.actor.top), self.actor.size)

        if self.actor.y >= GROUND_RECT.top:
            self.actor.y = GROUND_RECT.top
            self.vertical_speed = 0
            self.on_ground = True
        else:
            self.on_ground = False

        for platform in PLATFORMS:
            if player_rect.colliderect(platform):
                if self.vertical_speed > 0 and player_rect.bottom - self.vertical_speed <= platform.top:
                    self.actor.y = platform.top - 20
                    self.vertical_speed = 0
                    self.on_ground = True

    def move(self):
        moving = False
        
        # Movimento para direita
        if keyboard.right or keyboard.d:
            self.actor.x += MOVE_SPD
            if not self.facing_right:  # SÃ³ muda se nÃ£o estiver jÃ¡ virado para direita
                self.facing_right = True
                self.actor.flip_x = not self.facing_right
            moving = True
            
        # Movimento para esquerda
        elif keyboard.left or keyboard.a:  # Fixed: was 'd' for both directions
            self.actor.x -= MOVE_SPD
            if self.facing_right:  # SÃ³ muda se nÃ£o estiver jÃ¡ virado para esquerda
                self.facing_right = False
                self.actor.flip_x = not self.facing_right
            moving = True
            
        # Pulo
        if (keyboard.up or keyboard.w) and self.on_ground:
            jumping.play()
            self.vertical_speed = JUMP_STRENGTH
            self.on_ground = False

        self.state = "walk" if moving else "idle"

    def animate(self):
        self.anim_timer += 1
        if self.anim_timer >= 8:
            self.anim_timer = 0
            self.anim_index = (self.anim_index + 1)

            if self.state == "idle":
                self.anim_index %= len(self.idle_images)
                self.actor.image = self.idle_images[self.anim_index]
            elif self.state == "walk":
                self.anim_index %= len(self.walk_images)
                self.actor.image = self.walk_images[self.anim_index]

        # Aplica o flip baseado na direÃ§Ã£o
        self.actor.flip_x = not self.facing_right

    def update(self):
        self.apply_gravity()
        self.move()
        self.animate()

    def draw(self):
        self.actor.draw()

class Enemy:
    def __init__(self, idle_images, walk_images, position, velocity=random.uniform(0.5, 3.0)):
        self.idle_images = idle_images
        self.walk_images = walk_images
        self.actor = Actor(self.idle_images[0], pos=position)
        self.velocity = velocity
        self.direction = 1  # 1 para direita, -1 para esquerda
        self.vertical_speed = 0
        self.animation_index = 0
        self.animation_timer = 0
        self.on_ground = False
        self.facing_right = True  # Adiciona controle de direÃ§Ã£o visual

    def apply_gravity(self):
        self.vertical_speed += GVT
        self.actor.y += self.vertical_speed
        self.on_ground = False

        enemy_rect = Rect((self.actor.left, self.actor.top), self.actor.size)

        # ColisÃ£o com o chÃ£o
        if self.actor.y + 20 >= GROUND_RECT.top:
            self.actor.y = GROUND_RECT.top - 20 
            self.vertical_speed = 0
            self.on_ground = True

        # ColisÃ£o com plataformas
        for platform in PLATFORMS:
            if enemy_rect.colliderect(platform):
                if self.vertical_speed > 0 and enemy_rect.bottom - self.vertical_speed <= platform.top:
                    self.actor.y = platform.top - 20
                    self.vertical_speed = 0
                    self.on_ground = True

    def move(self):
        self.actor.x += self.velocity * self.direction
        
        # Atualiza a direÃ§Ã£o visual baseada no movimento
        self.facing_right = self.direction > 0

        # Verifica limites da tela
        if self.actor.left <= 0 or self.actor.right >= WIDTH:
            self.direction *= -1
            self.facing_right = self.direction > 0

        # Verifica se estÃ¡ no limite da plataforma
        below = Rect((self.actor.x, self.actor.y + 21), (1, 1))
        on_platform = False
        
        # Verifica se ainda estÃ¡ sobre uma plataforma ou o chÃ£o
        if self.actor.y + 20 >= GROUND_RECT.top - 5:  # PrÃ³ximo ao chÃ£o
            on_platform = True
        else:
            for platform in PLATFORMS:
                if platform.colliderect(below):
                    on_platform = True
                    break

        # Se nÃ£o estÃ¡ mais sobre uma plataforma, inverte direÃ§Ã£o
        if not on_platform:
            self.direction *= -1
            self.facing_right = self.direction > 0

    def animation(self):
        self.animation_timer += 1
        if self.animation_timer >= 8:
            self.animation_timer = 0
            self.animation_index = (self.animation_index + 1)

            self.animation_index %= len(self.walk_images)
            self.actor.image = self.walk_images[self.animation_index]

        # Aplica o flip baseado na direÃ§Ã£o de movimento
        # facing_right = True significa sprite original, False = flipado
        self.actor.flip_x = not self.facing_right

    def update(self):
        self.apply_gravity()
        self.move()
        self.animation()

    def draw(self):
        self.actor.draw()

class FlyingEnemy:
    def __init__(self, fly_images, position, velocity=1.5, wave_amplitude=50):
        self.fly_images = fly_images
        self.actor = Actor(self.fly_images[0], pos=position)
        self.velocity = velocity
        self.direction = 1  # 1 para direita, -1 para esquerda
        self.animation_index = 0
        self.animation_timer = 0
        self.facing_right = True
        
        # Movimento em onda
        self.base_y = position[1]  # Posição Y base
        self.wave_amplitude = wave_amplitude  # Amplitude da onda
        self.wave_offset = 0  # Offset para calcular a onda
        
    def move(self):
        # Movimento horizontal
        self.actor.x += self.velocity * self.direction
        
        # Atualiza a direção visual baseada no movimento
        self.facing_right = self.direction > 0
        
        # Verifica limites da tela e inverte direção
        if self.actor.left <= 0 or self.actor.right >= WIDTH:
            self.direction *= -1
            self.facing_right = self.direction > 0
        
        # Movimento vertical em onda (senoidal)
        self.wave_offset += 0.1
        self.actor.y = self.base_y + math.sin(self.wave_offset) * self.wave_amplitude
        
    def animation(self):
        self.animation_timer += 1
        if self.animation_timer >= 6:  # Animação mais rápida para dar sensação de voo
            self.animation_timer = 0
            self.animation_index = (self.animation_index + 1) % len(self.fly_images)
            self.actor.image = self.fly_images[self.animation_index]
            
        # Aplica o flip baseado na direção de movimento
        self.actor.flip_x = not self.facing_right
        
    def update(self):
        self.move()
        self.animation()
        
    def draw(self):
        self.actor.draw()

hero = Player(
    idle_images=["player_idle_0", "player_idle_1", "player_idle_2"],
    walk_images=["player_walk0", "player_walk1", "player_walk2", "player_walk3"],
    position=(100, 550)
)

# CriaÃ§Ã£o dos inimigos terrestres
enemies = []

for platform in PLATFORMS:
    x = platform.centerx
    y = platform.top - 20  # Considerando altura da imagem do inimigo
    new_enemy = Enemy(
        idle_images=["enemy_idle0", "enemy_idle1", "enemy_idle2", "enemy_idle3", "enemy_idle4"],
        walk_images=["enemy_walk0", "enemy_walk1", "enemy_walk2", "enemy_walk3", "enemy_walk4", "enemy_walk5", "enemy_walk6"],
        position=(x, y),
        velocity=random.uniform(0.5, 2.0)
    )
    enemies.append(new_enemy)

# Criação dos inimigos voadores
flying_enemies = []

# Adiciona 2-3 inimigos voadores em alturas diferentes
flying_positions = [
    (200, 150),  # Entre as primeiras plataformas
    (500, 300),  # No meio do mapa
    (650, 100),  # Perto da última plataforma
]

for pos in flying_positions:
    flying_enemy = FlyingEnemy(
        fly_images=["enemy_fly0", "enemy_fly1", "enemy_fly2", "enemy_fly3"],  # Usando sprites dos inimigos terrestres como exemplo
        position=pos,
        velocity=random.uniform(1.0, 3.0),
        wave_amplitude=random.uniform(30, 0)
    )
    flying_enemies.append(flying_enemy)

# Portal na Ãºltima plataforma
last_platform = PLATFORMS[-1]
portal = Actor("bandeira", pos=(last_platform.centerx + 80, last_platform.top - 60))

def draw_hearts():
    for i in range(lives):
        screen.blit("heart", (10 + i * 45, 10))

# BotÃµes clicÃ¡veis do menu
button_start = Rect(300, 210, 200, 50)
button_music = Rect(300, 340, 200, 50)
button_quit = Rect(300, 460, 200, 50)

# Menu
def draw_menu(screen):
    screen.blit("bg_menu", (0, 0))
    screen.draw.text(TITLE, center=(WIDTH//2, 100), fontsize=78, color="white")
    screen.draw.filled_rect(button_start, (45, 247, 75))
    screen.draw.filled_rect(button_music, (181, 181, 181))
    screen.draw.filled_rect(button_quit, (171, 0, 0))

    screen.draw.text("Play", center=button_start.center, fontsize=36, color="white")
    screen.draw.text(f"Music: {'ON' if music_on else 'OFF'}", center=button_music.center, fontsize=36, color="white")
    screen.draw.text("Close App", center=button_quit.center, fontsize=36, color="white")

def on_mouse_down(pos):
    global show_menu, game_started, music_on

    if show_menu:
        if button_start.collidepoint(pos): #Start
            selecting.play()
            show_menu = False
            game_started = True

        elif button_music.collidepoint(pos): # Music
            selecting.play()
            music_on = not music_on
            if music_on:
                sounds.time_for_adventure.play()  # Som tocando 
            else:
                sounds.time_for_adventure.stop() # Para de tocar o som

        elif button_quit.collidepoint(pos): # Exit
            selecting.play()
            quit()

def update():
    global lives, game_over, won, end_time, show_menu, game_started

    # Se for hora de voltar ao menu
    if end_time and time.time() >= end_time:
        show_menu = True
        game_started = False
        game_over = False
        won = False
        end_time = None
        reset_game()
        return

    if show_menu or game_over or won:
        return

    hero.update()
    
    # Atualiza inimigos terrestres
    for enemy in enemies:
        enemy.update()

        # Checar colisÃ£o com inimigo terrestre
        hero_rect = Rect((hero.actor.left, hero.actor.top), hero.actor.size)
        enemy_rect = Rect((enemy.actor.left, enemy.actor.top), enemy.actor.size)

        if hero_rect.colliderect(enemy_rect):
            damage.play()
            lives -= 1
            hero.actor.pos = (100, 500)
            if lives <= 0:
                game_over = True
                end_time = time.time() + 3  # 3 segundos para mostrar a tela de fim
            break
    
    # Atualiza inimigos voadores
    for flying_enemy in flying_enemies:
        flying_enemy.update()
        
        # Checar colisão com inimigo voador
        hero_rect = Rect((hero.actor.left, hero.actor.top), hero.actor.size)
        flying_enemy_rect = Rect((flying_enemy.actor.left, flying_enemy.actor.top), flying_enemy.actor.size)
        
        if hero_rect.colliderect(flying_enemy_rect):
            damage.play()
            lives -= 1
            hero.actor.pos = (100, 500)
            if lives <= 0:
                game_over = True
                end_time = time.time() + 3  # 3 segundos para mostrar a tela de fim
            break

    # Verifica colisÃ£o com o portal
    hero_rect = Rect((hero.actor.left, hero.actor.top), hero.actor.size)
    portal_rect = Rect((portal.left, portal.top), portal.size)
    if hero_rect.colliderect(portal_rect):
        won = True
        end_time = time.time() + 3  # 3 segundos para mostrar a tela de vitÃ³ria

def draw():
    screen.clear()

    if show_menu:
        draw_menu(screen)
        return  # NÃ£o desenha o jogo se no menu

    screen.blit("background",(0, 0))  # fundo do jogo

    for platform in PLATFORMS:
        screen.draw.filled_rect(platform, (120, 120, 120))

    portal.draw()
    hero.draw()

    # Desenha inimigos terrestres
    for enemy in enemies:
        enemy.draw()
    
    # Desenha inimigos voadores
    for flying_enemy in flying_enemies:
        flying_enemy.draw()

    draw_hearts()

    screen.draw.text("Get to the flag and avoid the enemies!", center=(WIDTH//2, 30), fontsize=24, color="black")

    if game_over:
        screen.fill((25, 25, 112)) 
        screen.draw.text("GAME OVER", center=(WIDTH//2, HEIGHT//2), fontsize=64, color="black")

    if won:
        screen.fill((135, 206, 235)) 
        screen.draw.text("YOU WIN!", center=(WIDTH//2, HEIGHT//2), fontsize=64, color="green")

def reset_game():
    global lives, hero, enemies, flying_enemies
    lives = NUM_LIVES
    hero.actor.pos = (100, 500)
    hero.facing_right = True  # Reset da direÃ§Ã£o do player

    # Recria inimigos terrestres para resetar posiÃ§Ã£o e estado
    enemies.clear()
    for platform in PLATFORMS:
        x = platform.centerx
        y = platform.top - 20
        new_enemy = Enemy(
            idle_images=["enemy_idle0", "enemy_idle1", "enemy_idle2", "enemy_idle3", "enemy_idle4"],
            walk_images=["enemy_walk0", "enemy_walk1", "enemy_walk2", "enemy_walk3", "enemy_walk4", "enemy_walk5", "enemy_walk6"],
            position=(x, y),
            velocity=1.2
        )
        enemies.append(new_enemy)
    
    # Recria inimigos voadores
    flying_enemies.clear()
    flying_positions = [
        (200, 150),
        (500, 300),
        (650, 100),
    ]
    
    for pos in flying_positions:
        flying_enemy = FlyingEnemy(
            fly_images=["enemy_walk0", "enemy_walk1", "enemy_walk2"],
            position=pos,
            velocity=random.uniform(1.0, 2.5),
            wave_amplitude=random.uniform(30, 60)
        )
        flying_enemies.append(flying_enemy)

pgzrun.go()