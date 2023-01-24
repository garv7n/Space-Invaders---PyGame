import sys, pygame, time

class Game:
    """
    Main game class with all variables relating to mechanics
    """
    def __init__(self, screen_size) -> None:     # constructor that takes in custom screen size from user 
        pygame.init()
        self.size = screen_size
        self.bg = pygame.image.load("bg.png")
        self.enemy_dead = pygame.image.load("invaderkilled.gif")
        self.screen = pygame.display.set_mode(self.size)
        self.enemy_time = time.time() + 10
        self.bullets,self.enemies, self.dead_enemies = [], [], []
        self.enemy_killed, self.hero_dead, self.fire =pygame.mixer.Sound('invaderkilled.wav'), pygame.mixer.Sound('invaderkilled.wav'), pygame.mixer.Sound('shoot.wav')
        self.score = 0
        self.level = 1
        self.font = pygame.font.Font('font.TTF', 16)
        self.bullet_delay = 1000 
        self.next_bullet = 0
        self.refresh = 0

    def playGame(self):
        """
        Main function to play game
        
        """     
        player = PlayerShip()   # create one instance of player
        gen = genAliens()       # create instance of generator
        gen.spawnNew(True)      # trigger the first row of aliens to spawn wih LEFT direction
        pygame.mixer.init()     # load background music
        pygame.mixer.music.load("bg.wav")
        pygame.mixer.music.play(-1)     # set constant loop of music
    

        while True:     # constant loop
            cur_time = pygame.time.get_ticks()  
            events = pygame.event.get()
            self.text =  self.font.render('Score: '+ str(self.score), False, (226,88,34))   # create text surface for score
            for event in events:        # handle events and keypresses
                if event.type == pygame.QUIT: 
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        player.handleLeft()

                    if event.key == pygame.K_RIGHT:
                        player.handleRight()

                    if event.key == pygame.K_SPACE and cur_time > self.next_bullet:
                        self.next_bullet = cur_time+self.bullet_delay   # check that delay is being satisfied 
                        self.fire.play()
                        self.bullets.append(Bullet(player.playerpos, self))

                if event.type == pygame.KEYUP:
                    player.change = 0
            
            player.boundaryCheck()   # constant check for border collsion
     
    
            if self.refresh >= 600:   # every 600 iterations base speed
                self.refresh = 0
                for row in self.enemies:    # iterate over each row and each enemy in row
                    for enemy in row:
                        if not enemy.checkBoundary():   # if any enemy touches boundary (red zone)
                            for row in self.enemies:    # apply following to ALL enemies
                                for enemy in row:
                                    enemy.shiftLevel()      # nudge all enemies lower by one unit of player height
                                    enemy.direction = not enemy.direction   # negate the current direction (acts as a switch)
                                    enemy.traverse(enemy.direction)     # move enemies away from border
                            gen.spawnNew(enemy.direction)   # spawn new row of enemies
                            game.level +=1
                            break   # once any enemy is touching border break from loop
                            
                        if enemy.checkBoundary():   # if enemy is within screen
                            enemy.traverse(enemy.direction)     # nudge enemy based off enemy.direction (True = Left / False = Right)
                            
            self.refresh+=game.level/3     # inc the iteration counter relative to game progress

            player.playerpos+= player.change       
            
            self.screen.blit(self.bg,(0,0))
            self.screen.blit(player.image, (player.playerpos, game.size[1]-60))
            for row in self.enemies:    # iterate of enemies list and check for collisions
                for enemy in row:
                    enemy.checkCollision(game, player)  
                    self.screen.blit(enemy.image, (enemy.xpos, enemy.ypos))
                
            for bullet in self.bullets:     # iterate of over any existing bullets and draw them
                bullet.draw()
            for dead in self.dead_enemies:  # draw image for any recently killed enemies
                self.screen.blit(self.enemy_dead, dead)
               
            
            self.screen.blit(self.text, (10,10))    # keep track of score
          
            pygame.display.flip()

    def gameOver(self):
        """
        finish game once enemy <--> player collision detected\n
        print score to screen
        """
        over =  self.font.render('Game Over!', False, (226,88,34))
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
            self.screen.blit(self.bg,(0,0))     # draw text on screen and prompt Game Over
            self.screen.blit(over, (250,game.size[1]/2))
            self.screen.blit(self.text, (250,game.size[1]/2+50))
            pygame.display.flip()


class PlayerShip:
    """
    main class for Hero\n
    initialises:\n
    - image
    - x-axis starting point
    """
    def __init__(self) -> None: 
        self.image = pygame.image.load("ship2.png")
        self.image = pygame.transform.scale(self.image, (60, 60))
        self.change = 0
        self.playerpos = game.size[0]/2-30 

      
    ################# Getters ###############
    def getchange(self):

        return self.change

    def getxPos(self):
        return self.playerpos
    #############################
    def handleLeft(self):
        """
        takes in player object\n
        decreases player x-axis position
        """
        if self.playerpos + self.change >= 0 and self.playerpos + self.change <= game.size[0] - 60:
            self.change = -.5


    def handleRight(self):
        """
        takes in player object\n
        increases player x-axis position
        """
        if self.playerpos + self.change >= 0 and self.playerpos + self.change <= game.size[0] - 60:
            self.change = .5
    

    def boundaryCheck(self):
        """
        Constant check for boundary breach\n
        independent of events or keypresses\n
        prevents boundary breach while key down is held
        """
        if self.playerpos < 0:
            self.change = 0
            self.playerpos = 0
        if self.playerpos +60 > game.size[0]:
            self.change = 0
            self.playerpos = game.size[0] -60
        
        
class Bullet:
    """
    Bullet class for drawing the players fired bullets
    """
    def __init__(self, xPos, game) -> None:
        self.xpos = xPos+30
        self.ypos = game.size[1]-40
        self.colour = (252, 127, 3)
        self.game = game
      
        
        
    def draw(self):
        """
        takes in bullet object\n
        draws rect object to screen starting at xpos of player\n
        """
        self.bulletRect = pygame.Rect(self.xpos, self.ypos, 3,9)
        pygame.draw.rect(self.game.screen, self.colour, self.bulletRect)
        self.ypos -= 1
    

class genAliens:
    """
    generator class for spawning in new aliens
    """
    def __init__(self) -> None:
        self.margin = 100
        self.width = 50
       

    def spawnNew(self, direct):
        """
        takes in enemy and direction of movement\n
        - if enemy list is empty --> spawn in from center of screen\n
        - if enemy list not empty --> spawn in from the left/right of screen
        """
        if game.enemies:    # if game is already running
            game.enemies.append([])     # append empty list to create new row in matrix
            if not direct:  # if the current direction of movement is right:
                for x in range(1, game.size[0]-self.margin*2 , self.width):   # start drawing from the left of screen  
                    game.enemies[-1].append(Enemy(x, 40, direct))
        
            if direct:     # if the current direction of movement is left:
                for x in range(200, game.size[0]-1, self.width):        # start drawing from the right of screen  
                    game.enemies[-1].append(Enemy(x, 40, direct))
              
        else:   # if game started draw in center
            game.enemies.append([])
            for x in range(self.margin, game.size[0] - self.margin, self.width):
                    game.enemies[-1].append(Enemy(x, 40, direct))
                        
  
                    
        

class Enemy:
    """
    class for enemies\n
    takes 3 arguments:\n
    - x-axis position\n
    - y-axis position\n
    - current direction of movement\n
    """
    def __init__(self, xPos, yPos, direct) -> None:
        self.image = pygame.image.load("invader.svg")
        self.image = pygame.transform.scale(self.image, (40,40))
        self.change = 0
        self.xpos, self.ypos = xPos, yPos
        self.direction = direct 

    def getPos(self):
        return self.ypos

    def shiftLevel(self):
        """
        Takes in enemy\n
        - moves y-axis position down by 1 unit of player height
        """
        self.ypos+=40


    def traverse(self, direct):
        """
        takes in enemy object and current direction\n
        - moves enemy based off value of direct
        """
        if game.dead_enemies:       # if any dead enemy traces remain remove them from screen
            game.dead_enemies.clear()
        if direct:
            self.xpos -=10
        if not direct:
            self.xpos+=10

    def __str__(self) -> str:
        """
        Used in testing stages to get position of Enemy by printing object instance
        """
        return "X:" + str(self.xpos) +" " + "Y" + str(self.ypos)

    def checkBoundary(self):
        """
        takes in enemy object and compares x-axis position to border\n
        - True --> within border\n
        - False --> touch border
        """
        if self.xpos + self.change> 0 and self.xpos + self.change < game.size[0]-40:
            return True
        return False
    
    def checkCollision(self, game, player):
        """
        - compares each enemy position to bullet\n
        - compares enemy position to player

        """
        for bullet in game.bullets:     # check enemy on bullet collisions
            if (bullet.xpos < self.xpos + 40 and 
                    bullet.xpos > self.xpos - 40 and
                    bullet.ypos < self.ypos + 40 and
                    bullet.ypos > self.ypos - 40): 
                game.bullets.remove(bullet)

                rect = game.enemy_dead.get_rect(x=self.xpos, y=self.ypos)   # create rect of dead enemy
                game.dead_enemies.append(rect)  # add rect to dead enemies list to be drawn later
                game.score+=5   # inc the score
                game.enemy_killed.play()
                for row in game.enemies:    # iterate over each row and find the enemy that triggered collision
                    if self in row:
                        game.enemies[game.enemies.index(row)].remove(self) # remove the enemy from the list in the nth row
       
        if  (self.xpos < player.playerpos +60 and 
                self.xpos > player.playerpos - 60 and
                self.ypos < game.size[1] +80 and 
                self.ypos > game.size[1] - 80):
            game.gameOver()     # kill game once player collides with enemy
        
        

######### Main funtion ran ########### 
if __name__ == "__main__":      
    game = Game((600,820))  
    game.playGame()