#Projeto final - Design de Software
#Equipe: Bruno Marques Li Volsi Falcao e Larissa Jordana de Paula Soares
#Data: 09/06/2021

# JOGO

import pygame

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)


screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Insperex')




#define player action variables
moving_left = False
moving_right = False





class Soldier(pygame.sprite.Sprite):
    def _init_(self, x, y, scale, speed):
        pygame.sprite.Sprite._init_(self)
        self.speed = speed
        self.direction = 1
        self.flip = False
        img = pygame.image.load('pounce.png')
        self.image = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height()* scale)))
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
    

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
            dy = self.speed
            self.flip = False
            self.direction = 1
        
        #update rectangle position
        self.rect.x += dx
        self.rect.y += dy


    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)


player = Soldier( 200, 200, 3, 5)






run = True
while run:


    player.draw()
    
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
            

        #Keyboard button realease
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_ESCAPE:
                run = False

    
    pygame.display.update()

pygame.quit()
