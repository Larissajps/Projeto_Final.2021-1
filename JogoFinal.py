#Equipe: Bruno Marques Li Volsi Falcao e Larissa Jordana de Paula Soares
#Data: 09/06/2021

# JOGO

import pygame
from pygame import mixer
import os
import random
import csv

mixer.init()
pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)


screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Insperex')

#Set Framerate
clock = pygame.time.Clock()
FPS = 60

# definindo variaveis do jogo
GRAVITY = 0.75
SCROLL_THRESH = 200
ROWS = 16
COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS 
TILE_TYPES = 21
MAX_LEVELS = 3
screen_scroll = 0
bg_scroll = 0
level = 1
start_game = False


#define player action variables
moving_left = False
moving_right = False
shoot = False


# musica e sons
pygame.mixer.music.load('MUSIC/musica.mp3')
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1, 0.0, 7000)
jump_fx = pygame.mixer.Sound('MUSIC/pulo.mp3')
jump_fx.set_volume(0.3)
shooting_fx = pygame.mixer.Sound('MUSIC/bomba.mp3')
shooting_fx.set_volume(0.5)
# imagens
# Botões
start_img = pygame.image.load('IMG/Inicio.png').convert_alpha()
exit_img = pygame.image.load('IMG/Saida.png').convert_alpha()
restart_img = pygame.image.load('IMG/Restart.png').convert_alpha()
# Fundo
pine1_img = pygame.image.load('IMG/Background/pine1.png').convert_alpha()
pine2_img = pygame.image.load('IMG/Background/pine2.png').convert_alpha()
mountain_img = pygame.image.load('IMG/Background/mountain.png').convert_alpha()
sky_img = pygame.image.load('IMG/Background/sky_cloud.png').convert_alpha()
# imagens de fundo
img_list = []
for x in range(TILE_TYPES):
    img = pygame.image.load(f'IMG/Mundo/{x}.png')
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)



# carregar imagens bala
bullet_img = pygame.image.load('IMG/bomba/bomba.png').convert_alpha()

# pegando caixas
health_box = pygame.image.load('IMG/vida/vida.png').convert_alpha()
ammo_box = pygame.image.load('IMG/moeda/moeda.png').convert_alpha()
item_boxes = {
    'Health' : health_box,
    'Ammo' : ammo_box,
}


#define colors
BG = (255, 0, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

# definindo fonte
font = pygame.font.SysFont('futura', 30)

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x,y))


def draw_bg():
    screen.fill(BG)
    width = sky_img.get_width()
    for x in range(5):
        screen.blit(sky_img, ((x * width) - bg_scroll * 0.5, 0))
        screen.blit(mountain_img, ((x * width) - bg_scroll * 0.6, SCREEN_HEIGHT - mountain_img.get_height() - 300))
        screen.blit(pine1_img, ((x * width) - bg_scroll * 0.7,  SCREEN_HEIGHT - pine1_img.get_height() - 150))
        screen.blit(pine2_img, ((x * width) - bg_scroll * 0.8, SCREEN_HEIGHT - pine2_img.get_height()))

# refazendo o level
def reset_level():
    enemy_group.empty()
    bullet_group.empty()
    item_box_group.empty()
    decoration_group.empty()
    water_group.empty()
    exit_group.empty()

    # criando lista de tile vazia
    data = []
    for row in range(ROWS):
        r = [-1] * COLS
        data.append(r)

    return data



class Soldier(pygame.sprite.Sprite):
    def _init_(self, char_type, x, y, scale, speed, ammo):
        pygame.sprite.Sprite._init_(self)
        self.alive = True
        self.char_type = char_type
        self.speed = speed
        self.ammo = ammo
        self.start_ammo = ammo
        self.shoot_cooldown = 0
        self.health = 100
        self.max_health = self.health
        self.direction = 1
        self.vel_y = 0
        self.jump = False
        self.in_air = True
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        # variaveis especificas para ai
        self.move_counter = 0
        self.vision = pygame.Rect(0, 0, 150, 20)
        self.idling = False
        self.idling_counter = 0

        #carregando as imagens 
        animation_types = ['parado', 'andando', 'pulando', 'morrendo']
        for animation in animation_types:
            # refazendo lista de imagens temporariamente
            temp_list = []
            # contando numero de imagens em uma pasta
            num_of_frames = len(os.listdir(f'IMG/{self.char_type}/{animation}'))
            for i in range(num_of_frames):
                img = pygame.image.load(f'IMG/{self.char_type}/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height()* scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)
            
        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
    

    def update(self):
        self.update_animation()
        self.check_alive()
        # atualizando o cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def move(self,moving_left,moving_right):
        #reset moviement variables
        screen_scroll = 0
        dx = 0
        dy = 0

        #assingn movement variables if moving left or right 
        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1 
        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1

        # Pulo
        if self.jump == True and self.in_air == False:
            self.vel_y = -11
            self.jump = False
            self.in_air = True

        # aplicando gravidade
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y
        dy += self.vel_y   

        # verificando colisão
        for tile in world.obstacle_list:
            # verificando colião na direção x
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
                # Se o inimigo atingir a parede ele vira pro outro lado
                if self.char_type == 'inimigo':
                    self.direction *= -1
                    self.move_counter = 0
            # verificando colisão na direção y
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                # verificando se estou abaixo do chão, pular
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                # verificando se esta acima do chão, caindo
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom

        # verificando colisão com a agua
        if pygame.sprite.spritecollide(self, water_group, False):
            self.health = 0

        # verificando colisão com saida
        level_complete = False
        if pygame.sprite.spritecollide(self, exit_group, False):
            level_complete = True

        # verificando se o jogador caiu do mapa
        if self.rect.bottom > SCREEN_HEIGHT:
            self.health = 0
        
        # verificando se ta indo pra fora do extremo da tela
        if self.char_type == 'raposa':
            if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
                dx = 0

        #update rectangle position
        self.rect.x += dx
        self.rect.y += dy

        # atualizando rolamento de tela conforme posição do jogador
        if self.char_type == 'raposa':
            if (self.rect.right > SCREEN_WIDTH - SCROLL_THRESH and bg_scroll < (world.level_lenght * TILE_SIZE) - SCREEN_WIDTH) or (self.rect.left < SCROLL_THRESH and bg_scroll > abs(dx)):
                self.rect.x -= dx
                screen_scroll = -dx

        return screen_scroll, level_complete
                

    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 20
            bullet = Bullet(self.rect.centerx + (0.80 * self.rect.size[0] * self.direction), self.rect.centery, self.direction)
            bullet_group.add(bullet)
            # gastando munição
            self.ammo -= 1
            shooting_fx.play()
    
    def ai(self):
        if self.alive and player.alive:
            if self.idling == False and random.randint(1, 200) == 1:
                self.update_action(0)#0: parado
                self.idling = True
                self.idling_counter = 50
            # vendo se o ai esta perto do jogador
            if self.vision.colliderect(player.rect):
                # parar de andar ao ver jogador
                self.update_action(0)#0: parado
                # atirar
                self.shoot()
            else:
                if self.idling == False:
                    if self.direction == 1:
                        ai_moving_right = True
                    else:
                        ai_moving_right = False
                    ai_moving_left = not ai_moving_right
                    self.move(ai_moving_left, ai_moving_right)
                    self.update_action(1)# 1: andando
                    self.move_counter += 1
                    # atualizando a visão para que acompanhe o inimigo
                    self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)
                    
                    if self.move_counter > TILE_SIZE:
                        self.direction *= -1
                        self.move_counter *= -1
                else:
                    self.idling_counter -= 1
                    if self.idling_counter <= 0:
                        self.idling = False
        # rolamento
        self.rect.x += screen_scroll     


    def update_animation(self):
        # atualizando animacao
        ANIMATION_COOLDOWN = 100
        # atualizando imagem dependendo da imagem atual
        self.image = self.animation_list[self.action][self.frame_index]
        # verificando se o tempo passou da ultima atualizacao
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        # se as imagens acabarem volta do comeco
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) -1
            else:
                self.frame_index = 0


    def update_action(self, new_action):
        # ver se a nova ação é diferente da antiga
        if new_action != self.action:
            self.action = new_action
            #atualizando ajustes de animação
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()


    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(3)


    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)

class World():
    def _init_(self):
        self.obstacle_list = []

    def process_data(self, data):
        self.level_lenght = len(data[0])
        # significando cada valor no csv
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >=0:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    tile_data = (img, img_rect)
                    if tile >= 0 and tile <= 8:
                        self.obstacle_list.append(tile_data)
                    elif tile >= 9 and tile <= 10:
                        water = Water(img, x * TILE_SIZE, y * TILE_SIZE)
                        water_group.add(water)
                    elif tile >= 11 and tile <= 14:
                        decoration = Decoration(img, x * TILE_SIZE, y * TILE_SIZE)
                        decoration_group.add(decoration)
                    elif tile == 15: # criando jogador
                        player = Soldier('raposa', x * TILE_SIZE, y * TILE_SIZE, 1.25, 5, 20)
                        health_bar = HealthBar(10, 10, player.health, player.health)
                    elif tile == 16: # criando inimigo
                        enemy = Soldier('inimigo',x * TILE_SIZE, y * TILE_SIZE, 1.25, 2, 20)
                        enemy_group.add(enemy)
                    elif tile == 17: # criando munição
                        item_box = ItemBox('Ammo', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 18:
                        pass
                    elif tile == 19: # criando vida
                        item_box = ItemBox('Health', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 20: # criando a saida
                        exit = Exit(img, x * TILE_SIZE, y * TILE_SIZE)
                        exit_group.add(exit)
        return player, health_bar

    def draw(self):
        for tile in self.obstacle_list:
            tile[1][0] += screen_scroll
            screen.blit(tile[0], tile[1])

class Decoration(pygame.sprite.Sprite):
    def _init_(self, img, x, y):
        pygame.sprite.Sprite._init_(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll    

class Water(pygame.sprite.Sprite):
    def _init_(self, img, x, y):
        pygame.sprite.Sprite._init_(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll

class Exit(pygame.sprite.Sprite):
    def _init_(self, img, x, y):
        pygame.sprite.Sprite._init_(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll

class ItemBox(pygame.sprite.Sprite):
    def _init_(self, item_type, x, y):
        pygame.sprite.Sprite._init_(self)
        self.item_type = item_type
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + TILE_SIZE - self.image.get_height())
    
    def update(self):
        # rolamento
        self.rect.x += screen_scroll
        # verificando se o jogador pegou a caixa
        if pygame.sprite.collide_rect(self, player):
            # verificando qual foi o item
            if self.item_type == 'Health':
                player.health += 15
                if player.health > player.max_health:
                    player.health   = player.max_health
            elif self.item_type == 'Ammo':
                player.ammo += 5
            # apagando a caixa após pega-lá
            self.kill()

class HealthBar():
    def _init_(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health
    
    def draw(self, health):
        # atualizando para nova vida
        self.health = health
        # calculando o ratio da vida
        ratio = self.health / self.max_health
        pygame.draw.rect(screen, BLACK, (self.x -2, self.y - 2, 154, 24))
        pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 20))
        

class Bullet(pygame.sprite.Sprite):
    def _init_(self, x, y, direction):
        pygame.sprite.Sprite._init_(self)
        self.speed = 10
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.direction = direction

    def update(self):
        # mexendo a bullet
        self.rect.x += (self.direction * self.speed) + screen_scroll
        #vendo se a bullet saiu da tela
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()
        # verificando colisão com o mapa
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()

        # Verificando a colisão com jogador
        if pygame.sprite.spritecollide(player, bullet_group, False):
            if player.alive:
                player.health -= 5
                self.kill()
        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, bullet_group, False):
                if enemy.alive:
                    enemy.health -= 25
                    self.kill()

class Button():
	def _init_(self,x, y, image, scale):
		width = image.get_width()
		height = image.get_height()
		self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
		self.rect = self.image.get_rect()
		self.rect.topleft = (x, y)
		self.clicked = False

	def draw(self, surface):
		action = False

		# posição do mouse
		pos = pygame.mouse.get_pos()

		# verificando mouse em cima e clicks
		if self.rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
				action = True
				self.clicked = True

		if pygame.mouse.get_pressed()[0] == 0:
			self.clicked = False

		# desenhando botão
		surface.blit(self.image, (self.rect.x, self.rect.y))

		return action

# Criando Botões
start_button = Button(SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT // 2 - 150, start_img, 1)
exit_button = Button(SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT // 2 + 50, exit_img, 1)
restart_button = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50, restart_img, 2)
# criando sprite groups
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()



# Criando uma lista de tile vazia
world_data = []
for row in range(ROWS):
    r = [-1] * COLS
    world_data.append(r)
# carregando o arquivo de nivel e criando mundo
with open(f'level{level}_data.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile)
world = World()
player, health_bar = world.process_data(world_data)




run = True
while run:

    clock.tick(FPS)

    if start_game == False:
        # desenhando menu
        screen.fill(BG)
        # add button
        if start_button.draw(screen):
            start_game = True
        if exit_button.draw(screen):
            run = False
    else:
        # atualizando bg
        draw_bg()
        # desenhando mundo
        world.draw()
        # mostrando vida
        health_bar.draw(player.health)
        # mostrando munição
        draw_text('Munição: ', font, WHITE, 10, 35)
        for x in range(player.ammo):
            screen.blit(bullet_img, (90 + (x * 10), 40))
        

        
        player.update()
        player.draw()

        for enemy in enemy_group:
            enemy.ai()
            enemy.update()
            enemy.draw()

        # atualizando e desenhando grupos
        bullet_group.update()
        item_box_group.update()
        decoration_group.update()
        water_group.update()
        exit_group.update()
        bullet_group.draw(screen)
        item_box_group.draw(screen)
        decoration_group.draw(screen)
        water_group.draw(screen)
        exit_group.draw(screen)
        
        # atualizando ação do jogador
        if player.alive:
            if shoot:
                player.shoot()
            if player.in_air:
                player.update_action(2)# pulo
            elif moving_left or moving_right:
                player.update_action(1)# andando
            else:
                player.update_action(0)# parado
            screen_scroll, level_complete = player.move(moving_left, moving_right)
            bg_scroll -= screen_scroll
            # verificando se jogador completou a fase
            if level_complete:
                level += 1
                bg_scroll = 0
                world_data = reset_level()
                if level <= MAX_LEVELS:
                    with open(f'level{level}_data.csv', newline='') as csvfile:
                        reader = csv.reader(csvfile, delimiter=',')
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)
                    world = World()
                    player, health_bar = world.process_data(world_data)

        else:
            screen_scroll = 0
            if restart_button.draw(screen):
                bg_scroll = 0
                world_data = reset_level()
                with open(f'level{level}_data.csv', newline='') as csvfile:
                    reader = csv.reader(csvfile, delimiter=',')
                    for x, row in enumerate(reader):
                        for y, tile in enumerate(row):
                            world_data[x][y] = int(tile)
                world = World()
                player, health_bar = world.process_data(world_data)

        

    for event in pygame.event.get():
        #quitgame
        if event.type == pygame.QUIT:
            run = False
        #Keyboard Presses
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_SPACE:
                shoot = True
            if event.key == pygame.K_w and player.alive:
                player.jump = True
                jump_fx.play()   
            if event.key == pygame.K_ESCAPE:
                run = False
            

        #Keyboard button realease
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_SPACE:
                shoot = False
            

    
    pygame.display.update()

pygame.quit()