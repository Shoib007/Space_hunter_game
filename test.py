import pygame
import random
import math

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Fonts for the game
main_font = pygame.font.SysFont("arial", 50)
lost_font = pygame.font.SysFont("arial", 60)

# images 
player_image = pygame.image.load('assets/pixel_ship_yellow.png')
enemy = pygame.image.load('assets/pixel_ship_red_small.png')
bullet_image = pygame.transform.rotate(pygame.image.load('assets/pixel_laser_yellow.png'), 90)
BG = pygame.transform.scale(pygame.image.load("assets/background-black.png"), (SCREEN_WIDTH, SCREEN_HEIGHT))
player_image = pygame.transform.rotate(player_image, -90)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.original_image = player_image
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

    def update(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy
        self.rotate()
    
    def rotate(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        rel_x, rel_y = mouse_x - self.rect.centerx, mouse_y - self.rect.centery
        angle = (180 / math.pi) * -math.atan2(rel_y, rel_x)
        self.image = pygame.transform.rotate(self.original_image, angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        

# Enemy class
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = enemy
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randint(0, SCREEN_HEIGHT - self.rect.width)

    def update(self, player_rect):
        dx = player_rect.x - self.rect.x
        dy = player_rect.y - self.rect.y
        dist = max(abs(dx), abs(dy))
        if dist != 0:
            self.rect.x += dx / dist
            self.rect.y += dy / dist
        

# Bullet class
class Bullet(pygame.sprite.Sprite):
    # rotate the bullet in the direction of mouse position
    
    def __init__(self, x, y, dx, dy):
        super().__init__()
        self.original_image = bullet_image
        self.image = self.original_image
        # self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.dx = dx
        self.dy = dy
        self.speed = 10
        mouse_x, mouse_y = pygame.mouse.get_pos()
        rel_x, rel_y = mouse_x - self.rect.centerx, mouse_y - self.rect.centery
        angle = (180 / math.pi) * -math.atan2(rel_y, rel_x)
        self.image = pygame.transform.rotate(self.original_image, angle)

    def update(self):
        self.rect.x += self.dx * self.speed
        self.rect.y += self.dy * self.speed
        if self.rect.bottom < 0:
            self.kill()
        


# Main function
def main():
    # Game Variables
    lives = 10
    seconds = 0
    minutes = 0
    hours = 0
    pygame.display.set_caption("Enemy Movement")

    # Initialize pygame timer event
    pygame.time.set_timer(pygame.USEREVENT, 1000)

    # Create Sprites
    player = Player()
    enemy = Enemy()
    bullet = Bullet(player.rect.centerx, player.rect.centery, 0, 0)

    # Group for sprites
    player_group = pygame.sprite.Group()
    enemy_group =pygame.sprite.Group()
    bullets_group = pygame.sprite.Group()

    player_group.add(player)
    enemy_group.add(enemy)


    # Clock for controlling fps
    clock = pygame.time.Clock()

    # Main loop
    while True:

        # Clear the screen
        # screen.fill(WHITE)
        screen.blit(BG, (0, 0))
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT or lives <= 0:
                if lives <= 0:
                    pygame.time.delay(2000)
                pygame.quit()
            if event.type == pygame.USEREVENT:
                seconds += 1
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse button
                # Get mouse x and y
                mouse_x, mouse_y = pygame.mouse.get_pos()
                # get horizontal and vertical distance from player and mouse position
                rel_x, rel_y = mouse_x - player.rect.centerx, mouse_y - player.rect.centery
                
                # Calculate the length of the vector and then normalize the vector
                distance = math.hypot(rel_x, rel_y)
                dx, dy = rel_x / distance, rel_y / distance
                
                # Create the bullet using dx, dy
                bullet = Bullet(player.rect.centerx, player.rect.centery, dx, dy)
                bullets_group.add(bullet)

        # Check collition between Bullet and Enemy
        pygame.sprite.groupcollide(bullets_group, enemy_group, True, True)
        
        # Check collition between Player and Enemy
        if pygame.sprite.spritecollide(player, enemy_group, dokill=True, collided=pygame.sprite.collide_mask):
            lives -= 1

        # Handle player movement
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_a] and player.rect.left > 0:
            dx = -5
        if keys[pygame.K_d] and player.rect.right < SCREEN_WIDTH:
            dx = 5
        if keys[pygame.K_w] and player.rect.top > 0:
            dy = -5
        if keys[pygame.K_s] and player.rect.bottom < SCREEN_HEIGHT:
            dy = 5
        player.update(dx, dy)

        # Update enemy
        enemy_group.update(player.rect)
        bullets_group.update()


        # Check is all enemies are dead then add more 5 enemies
        if len(enemy_group) == 0:
            for i in range(5):
                enemy = Enemy()
                enemy_group.add(enemy)


        # Show Labels
        duration_label = main_font.render(f"Timer: {hours}:{minutes}:{seconds}", 1, (255,0,0))
        lives_label = main_font.render(f"Lives: {lives}", 1, (255,0,0))
        lost_label = main_font.render("You Lost", 1, (255,0,0))
        screen.blit(lives_label, (10, 10))
        screen.blit(duration_label, (SCREEN_WIDTH - duration_label.get_width() - 10, 10))

        # Show lost text if lives == 0 then quit but update the screen before that 
        if lives == 0:
            screen.blit(lost_label, (SCREEN_WIDTH/2 - lost_label.get_width()/2, 350))
        

        # Draw sprites
        bullets_group.draw(screen)
        player_group.draw(screen)
        enemy_group.draw(screen)

        if seconds >= 60:
            minutes += 1
            seconds = 0
        if minutes >= 60:
            hours += 1
            minutes = 0

        # Update display
        pygame.display.update()
        
        # Cap the frame rate
        clock.tick(60)


if __name__ == "__main__":
    main()
