#Projeto final - Design de Software
#Equipe: Bruno Marques Li Volsi Falcao e Larissa Jordana de Paula Soares
#Data: 09/06/2021

# JOGO

import pygame
import os

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


#define player action variables
moving_left = False
moving_right = False
shoot = False

# carregar imagens bala
bullet_img = pygame.image.load('IMG/bomba/bomba.png').convert_alpha()

#define colors
BG = (144, 201, 120)
RED = (255, 0, 0)

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
            bullet = Bullet(self.rect.centerx + (0.6 * self.rect.size[0] * self.direction), self.rect.centery, self.direction)
            bullet_group.add(bullet)
            # gastando munição
            self.ammo -= 1

    def update_animation(self):
        # atualizando animacao
        ANIMATIN_COOLDOWN = 100
        # atualizando imagem dependendo da imagem atual
        self.image = self.animation_list[self.action][self.frame_index]
        # verificando se o tempo passou da ultima atualizacao
        if pygame.time.get_ticks() - self.update_time > ANIMATIN_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        # se as imagens acabarem volta do comeco
        if self.frame_index >= len(self.animation_list[self.action]):
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
            self.update_action()


    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)

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
        if pygame.sprite.spritecollide(enemy, bullet_group, False):
            if enemy.alive:
                enemy.health -= 25
                self.kill()


# criando sprite groups
bullet_group = pygame.sprite.Group()



player = Soldier('raposa', 200, 200, 2, 5, 20)
enemy = Soldier('inimigo', 400, 200, 2, 5, 20)



run = True
while run:

    clock.tick(FPS)

    draw_bg()

    player.update()
    player.draw()
    enemy.draw()

    # atualizando e desenhando grupos
    bullet_group.update()
    bullet_group.draw(screen)
    
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