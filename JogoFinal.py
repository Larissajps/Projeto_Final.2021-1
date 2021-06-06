#Projeto final - Design de Software
#Equipe: Bruno Marques Li Volsi Falcao e Larissa Jordana de Paula Soares
#Data: 09/06/2021

# JOGO

import pygame
import os
import random

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
TILE_SIZE = 40


#define player action variables
moving_left = False
moving_right = False
shoot = False

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
BG = (144, 201, 120)
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
    pygame.draw.line( screen, RED, (0, 300), (SCREEN_WIDTH, 300))




class Soldier(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed, ammo):
        pygame.sprite.Sprite.__init__(self)
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
    

    def update(self):
        self.update_animation()
        self.check_alive()
        # atualizando o cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def move(self,moving_left,moving_right):
        #reset moviement variables
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

        # checando colisão com o chão
        if self.rect.bottom + dy > 300:
            dy = 300 - self.rect.bottom 
            self.in_air = False
        
        #update rectangle position
        self.rect.x += dx
        self.rect.y += dy

    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 20
            bullet = Bullet(self.rect.centerx + (0.80 * self.rect.size[0] * self.direction), self.rect.centery, self.direction)
            bullet_group.add(bullet)
            # gastando munição
            self.ammo -= 1
    
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

class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + TILE_SIZE - self.image.get_height())
    
    def update(self):
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
    def __init__(self, x, y, health, max_health):
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
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.direction = direction

    def update(self):
        # mexendo a bullet
        self.rect.x += (self.direction * self.speed)
        #vendo se a bullet saiu da tela
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
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


# criando sprite groups
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()

# criando temporiariamente item boxes
item_box = ItemBox('Health', 100, 260)
item_box_group.add(item_box)
item_box = ItemBox('Ammo', 400, 260)
item_box_group.add(item_box)



player = Soldier('raposa', 200, 200, 1.25, 5, 20)
health_bar = HealthBar(10, 10, player.health, player.health)
enemy = Soldier('inimigo', 500, 279, 1.25, 2, 20)
enemy2 = Soldier('inimigo', 300, 279, 1.25, 2, 20)
enemy_group.add(enemy)
enemy_group.add(enemy2)



run = True
while run:

    clock.tick(FPS)

    draw_bg()
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
    bullet_group.draw(screen)
    item_box_group.draw(screen)
    
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
        player.move(moving_left, moving_right)

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