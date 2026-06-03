import pyxel, random

CAM_W = 608
CAM_H = 352

TILE_SIZE = 32

MARGIN = 4*TILE_SIZE

FPS = 60

cost = {'SlingShot':30, 'MouseTrap':20, 'Poison':10, 'GumBall':10}

class App:
    def __init__(self):
        pyxel.init(CAM_W,CAM_H,fps=FPS)
        pyxel.load('theme.pyxres')

        self.game = Game()


        pyxel.mouse(True)
        pyxel.run(self.update,self.draw)

    def update(self):
        self.game.update()

    def draw(self):
        self.game.draw()


class Game:
    def __init__(self):
        self.state = Menu()
    def update(self):
        self.state.update()

        self.checkSwitch()

    def draw(self):
        pyxel.cls(4)
        self.state.draw()

    def checkSwitch(self):
        if self.state.switch.ready:
            destination = self.state.switch.to
            if destination == 'InGame':
                self.state = InGame()

            else:
                self.state.switch.__init__()



class Switch:
    def __init__(self):
        self.ready = False
        self.to = None
        self.arguments = []
        
    def change(self,to,args=[]):
        self.to = to
        self.arguments = args
        self.ready = True



class Menu:
    def __init__(self):
        self.switch = Switch()
        self.buttons = []

        self.buttons.append(Button(30,30,100,50,'play',))
        self.buttons.append(Button(30,90,100,50,'quit'))


    def update(self):
        self.buttonsUpdate()

    def draw(self):
        for button in self.buttons:
            button.draw()
    def buttonsUpdate(self):
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            for button in self.buttons:
                if button.pressed():
                    self.buttonAction(button.name)

    def buttonAction(self,name):
        if name == 'play':
            self.switch.change('InGame')
        if name == 'quit':
            pyxel.quit()

class InGame:
    def __init__(self):
        self.switch = Switch()

        self.world = World([(0,0),(0,1),(0,2),(1,2),(2,2),(3,2),(4,2),(5,2),(6,2),(7,2),(8,2),(9,2),(9,3),(9,4),(9,5),(9,6),(9,7),(9,8),(9,9),(8,9),(7,9),(7,8),(7,7),(8,7),(9,7),(9,8),(9,9),(8,9),(7,9),(7,8),(7,7),(7,6),(7,5),(7,4),(6,4),(5,4),(4,4),(4,5),(4,6),(4,7),(4,8),(4,9)])
        
        self.enemies = []

        self.towers = []

        self.bullets = []


        self.lives = 50
        self.money = 50

        self.selectedCase = None
        self.buttons = []
        self.initButtons()

        self.timeBetweenSpawns = 5*FPS

    def initButtons(self):
        self.buttons.append(Button(10,30,50,50,'SlingShot',11))
        self.buttons.append(Button(68,30,50,50,'GumBall',11))
        self.buttons.append(Button(10,88,50,50,'MouseTrap',11))
        self.buttons.append(Button(68,88,50,50,'Poison',11))


        for button in self.buttons:
            button.showName = False


    def update(self):
        self.world.update()

        self.enemiesUpdate()

        self.towersUpdate()

        self.bulletsUpdate()

        self.checkAddTowers()

        self.buttonsUpdate()

        if onTick(self.timeBetweenSpawns):
            self.enemies.append(random.choice([Spider, Soldier, General, Car, Dino])(self.path))
            self.timeBetweenSpawns *= 0.95

    def buttonsUpdate(self):
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) and self.selectedCase != None:
            for button in self.buttons:
                if button.pressed():
                    self.createTower(self.selectedCase,button.name)

    def enemiesUpdate(self):
        for enemy in self.enemies:
            enemy.update()



            if enemy.health <= 0:
                self.enemies.remove(enemy)
                enemy.onDeath()
                self.money += enemy.maxHealth

            for spawn in enemy.spawned:
                self.enemies.append(spawn)

            if self.world.map[enemy.location[1]][enemy.location[0]].state.place == 'end' and enemy.health > 0:
                self.lives -= enemy.damage
                self.enemies.remove(enemy)

    def bulletsUpdate(self):
        for bullet in self.bullets:
            bullet.update()

            for enemy in self.enemies:
                
                print(enemy.x, enemy.y, bullet.x-bullet.radius, bullet.y-bullet.radius)

                if collision(enemy.x, enemy.y, (enemy.width, enemy.height), bullet.x-bullet.radius, bullet.y-bullet.radius, (2*bullet.radius, 2*bullet.radius)) and bullet.range > 0:
                    print("a")
                    if bullet.pierce == 0:
                        self.bullets.remove(bullet)
                    else:
                        bullet.pierce -= 1
                    
                    enemy.health -= bullet.damage
            
            if bullet.range <= 0:
                self.bullets.remove(bullet)
                    

    def draw(self):
        self.world.draw()

        for button in self.buttons:
            button.draw()
            if button.name in ['SlingShot', 'MouseTrap', 'Poison', 'GumBall']:
                drawTower(button.x + 9, button.y + 9, button.name)
                pyxel.text(button.x + 20, button.y + 51, str(cost[button.name]),0)

        pyxel.text(1, 1, f"Vies restantes : {self.lives}", 8)
        pyxel.text(CAM_W-3*TILE_SIZE,1, f"Argent : {self.money}", 9)

        for enemy in self.enemies:
            enemy.draw()

        for bullet in self.bullets:
            bullet.draw()

        if self.selectedCase != None:
            pyxel.rectb(self.selectedCase.x,self.selectedCase.y, TILE_SIZE, TILE_SIZE, 10)


    def checkAddTowers(self):
        x = (pyxel.mouse_x-MARGIN)//TILE_SIZE
        y = pyxel.mouse_y//TILE_SIZE

        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            if self.inMap(x,y) and not self.world.map[y][x].state.name == 'PathCase':
                self.selectedCase = self.world.map[y][x]




    def inMap(self,x,y):
        return x >= 0 and x < self.world.width and y >= 0 and y < self.world.height 

    def createTower(self,case,tower='SlingShot'):
        if case.state.name == 'EmptyCase':
            if self.money >= cost[tower]:
                case.state = TowerCase(case.x,case.y,tower)
                self.towers.append(case)
                self.money += -cost[tower]
            

    def towersUpdate(self):
        for tower in self.towers:
            tower.update()
            weapon = tower.state.weapon
            if weapon.bullet != None:
                self.bullets.append(weapon.bullet)
                weapon.bullet = None

        if pyxel.btnp(pyxel.KEY_R) and self.selectedCase.state.name == 'TowerCase':
            self.selectedCase.state.weapon.rotate()




class World:
    def __init__(self, path):
        self.width = 11
        self.height = 11

        self.map = [[Case(x,y) for x in range(self.width)] for y in range(self.height)]

        self.path = path

        for coord in path:
            case = self.map[coord[1]][coord[0]]
            case.state = PathCase(case.x,case.y)

        self.map[path[0][1]][path[0][0]].state.place = 'start' #Puts start point
        self.map[path[-1][1]][path[-1][0]].state.place = 'end' #Puts end point

        


    def draw(self):
        pyxel.rect(0,0, MARGIN, CAM_H, col=7)
        pyxel.rect(CAM_W-MARGIN,0, MARGIN, CAM_H, col=7)

        for line in self.map:
            for case in line:
                case.draw()
                

    def update(self):
        pass


    
class Enemy:
    def __init__(self, health, cooldown, damage, path):
        self.maxHealth = health
        self.health = health

        self.cooldown = cooldown
        self.speed = TILE_SIZE/self.cooldown

        self.damage = damage

        self.width = TILE_SIZE
        self.height = TILE_SIZE
        
        self.indice = 0
        self.path = path

        self.x = MARGIN+path[0][0]*TILE_SIZE
        self.y = path[0][1]*TILE_SIZE

        self.location = path[0]
        self.objective = path[1]

        self.spawned = []

    def update(self):
        if onTick(self.cooldown):
            self.indice += 1

            self.x = MARGIN+self.path[self.indice][0]*TILE_SIZE
            self.y = self.path[self.indice][1]*TILE_SIZE

            self.location = self.path[self.indice]
            if self.indice < len(self.path)-1:
                self.objective = self.path[self.indice+1]    
            
        if self.objective[0] < self.location[0]:
            self.x -= self.speed
        if self.objective[0] > self.location[0]:
            self.x += self.speed
        if self.objective[1] < self.location[1]:
            self.y -= self.speed
        if self.objective[1] > self.location[1]:
            self.y += self.speed



    def draw(self):
        pyxel.rect(self.x, self.y, self.width, self.height, col=7)

    def onDeath(self):
        pass

class Spider(Enemy):
    def __init__(self, path):
        super().__init__(health = 10, cooldown=0.4*FPS, damage=3, path=path)

    def draw(self):
        pyxel.blt(self.x,self.y,0,0,0,32,32,colkey=11)

class Soldier(Enemy):
    def __init__(self, path):
        super().__init__(health = 10, cooldown=0.5*FPS, damage=5, path=path)
        
    def draw(self):
        pyxel.blt(self.x,self.y,0,0,64,16,16,colkey=11)

class General(Enemy):
    def __init__(self, path):
        super().__init__(health = 30, cooldown=1*FPS, damage=20, path=path)

    def onDeath(self):
        for i in range(3):
            self.spawned.append(Soldier())
        
    def draw(self):
        pyxel.blt(self.x,self.y,0,0,32,32,32,colkey=11)

class Dino(Enemy):
    def __init__(self, path):
        super().__init__(health = 50, cooldown=2*FPS, damage=40, path=path)
        
    def draw(self):
        pyxel.blt(self.x,self.y,0,0,104,32,32,colkey=11)

class Car(Enemy):
    def __init__(self, path):
        super().__init__(health=5, cooldown=0.2*FPS, damage=10, path=path)
        
    def draw(self):
        pyxel.blt(self.x,self.y,0,0,136,32,32,colkey=11)


class Button:
    def __init__(self,x,y,w,h,name='',color=1):
        self.name = name
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.color = color

        self.showName = True

    def pressed(self):
        return pointInside(pyxel.mouse_x, pyxel.mouse_y, self.x,self.y,self.w,self.h) and pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT)

    def draw(self):
        pyxel.rect(self.x,self.y,self.w,self.h,self.color)
        if self.name != '' and self.showName:
            pyxel.text(self.x + self.w//2 - len(self.name)*2, self.y + self.h//2-3, self.name, 9)


class Case:
    def __init__(self,X,Y):
        self.x = MARGIN + X*TILE_SIZE
        self.y = Y*TILE_SIZE
        self.w = TILE_SIZE
        self.h = TILE_SIZE

        self.state = EmptyCase(self.x,self.y)

    def update(self):
        self.state.update()

    def draw(self):
        self.state.draw()


            
class EmptyCase:
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.w = TILE_SIZE
        self.h = TILE_SIZE
        self.selectTower = False
        self.name = 'EmptyCase'

    def update(self):
        if self.pressed():
            self.selectTower = True
            
    def draw(self):
        pyxel.rect(self.x,self.y,self.w,self.h,4)
    
    def pressed(self):
        return pointInside(pyxel.mouse_x, pyxel.mouse_y, self.x,self.y,self.w,self.h) and pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT)

class PathCase:
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.w = TILE_SIZE
        self.h = TILE_SIZE

        self.place = 'mid'
        self.name = 'PathCase'
            
    def draw(self):
        if self.place == 'start':
            pyxel.rect(self.x,self.y,self.w,self.h,8)
        elif self.place == 'end':
            pyxel.rect(self.x,self.y,self.w,self.h,3)
        else:
            pyxel.rect(self.x,self.y,self.w,self.h,14)

class TowerCase:
    def __init__(self,x,y,type):
        self.x = x
        self.y = y
        self.w = TILE_SIZE
        self.h = TILE_SIZE

        self.name = 'TowerCase'
        self.initType(type)

        self.lvlDamage = 1

    def update(self):
        self.weapon.update()

    def draw(self):
        self.weapon.draw()

    def initType(self,type): #list al the types
        if type == 'SlingShot':
            self.weapon = SlingShot(self.x,self.y)
        elif type == "MouseTrap":
            self.weapon = MouseTrap(self.x,self.y)
        elif type == "GumBall":
            self.weapon = GumBall(self.x,self.y)
        elif type == "Poison":
            self.weapon = Poison(self.x,self.y)
        else:
            self.weapon = SlingShot(self.x,self.y)



class Bullet:
    def __init__(self, x, y, vector, damage, range, pierce, radius):
        self.x = x
        self.y = y
        self.vector = vector

        self.radius = radius

        self.damage = damage
        self.range = range
        self.pierce = pierce

    def update(self):
        self.x += self.vector[0]
        self.y += self.vector[1]
        self.range -= (self.vector[0]**2+self.vector[1]**2)**0.5

    def draw(self):
        pyxel.circ(self.x, self.y, self.radius, 7)

class SlingShot:
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.w = TILE_SIZE
        self.h = TILE_SIZE

        self.orient = [-1,0]

        self.bullet = None

    def update(self):
        if self.seeEnemy() and onTick(1*FPS):
            self.shoot()

    def shoot(self):
        self.bullet = Bullet(self.x+self.w/2, self.y+self.h/2, self.orient, 5, MARGIN, 0, 2)

    def seeEnemy(self):
        return True


    def draw(self):
        drawTower(self.x,self.y,'SlingShot')
        pyxel.line(self.x+self.w//2,self.y+self.h//2,self.x+self.w//2 + self.orient[0]*20,self.y+self.h//2 + self.orient[1]*20, 7)

    def rotate(self):
        if self.orient == [-1,0]:
            self.orient = [0,1]
            
        elif self.orient == [0,1]:
            self.orient = [1,0]

        elif self.orient == [1,0]:
            self.orient = [0,-1]

        elif self.orient == [0,-1]:
            self.orient = [-1,0]

class MouseTrap:
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.w = TILE_SIZE
        self.h = TILE_SIZE

        self.orient = [-1,0]

        self.bullet = None

    def update(self):
        if self.seeEnemy() and onTick(1.25*FPS):
            self.shoot()

    def shoot(self):
        self.bullet = Bullet(self.x+self.w/2, self.y+self.h/2, self.orient, 15, 1*TILE_SIZE, 3, 1)

    def seeEnemy(self):
        return True


    def draw(self):
        drawTower(self.x,self.y,'MouseTrap')
        pyxel.line(self.x+self.w//2,self.y+self.h//2,self.x+self.w//2 + self.orient[0]*20,self.y+self.h//2 + self.orient[1]*20, 7)

        
    def rotate(self):
        if self.orient == [-1,0]:
            self.orient = [0,1]
            
        elif self.orient == [0,1]:
            self.orient = [1,0]

        elif self.orient == [1,0]:
            self.orient = [0,-1]

        elif self.orient == [0,-1]:
            self.orient = [-1,0]
    
class GumBall:
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.w = TILE_SIZE
        self.h = TILE_SIZE

        self.orient = [-1,0]

        self.bullet = None

    def update(self):
        if self.seeEnemy() and onTick(2*FPS):
            self.shoot()

    def shoot(self):
        self.bullet = Bullet(self.x+self.w/2, self.y+self.h/2, self.orient, 5, 1*TILE_SIZE, 0, 7)

    def seeEnemy(self):
        return True


    def draw(self):
        drawTower(self.x,self.y,'GumBall')
        pyxel.line(self.x+self.w//2,self.y+self.h//2,self.x+self.w//2 + self.orient[0]*20,self.y+self.h//2 + self.orient[1]*20, 7)


    def rotate(self):
        if self.orient == [-1,0]:
            self.orient = [0,1]
            
        elif self.orient == [0,1]:
            self.orient = [1,0]

        elif self.orient == [1,0]:
            self.orient = [0,-1]

        elif self.orient == [0,-1]:
            self.orient = [-1,0]


class Poison:
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.w = TILE_SIZE
        self.h = TILE_SIZE

        self.orient = [-1,0]

        self.bullet = None

    def update(self):
        if self.seeEnemy() and onTick(2.25*FPS):
            self.shoot()

    def shoot(self):
        self.bullet = Bullet(self.x+self.w/2, self.y+self.h/2, self.orient, 10, 1*TILE_SIZE, 3, 3)

    def seeEnemy(self):
        return True


    def draw(self):
        drawTower(self.x,self.y,'Poison')
        pyxel.line(self.x+self.w//2,self.y+self.h//2,self.x+self.w//2 + self.orient[0]*20,self.y+self.h//2 + self.orient[1]*20, 7)
       

    def rotate(self):
        if self.orient == [-1,0]:
            self.orient = [0,1]
            
        if self.orient == [0,1]:
            self.orient = [1,0]

        if self.orient == [1,0]:
            self.orient = [0,-1]

        if self.orient == [0,-1]:
            self.orient = [-1,0]


def drawTower(x,y,name):
    if name == 'SlingShot':
        pyxel.blt(x,y,0,64,0,32,32,colkey=11)
    if name == 'GumBall':
        pyxel.blt(x,y,0,64,32,32,32,colkey=11)
    if name == 'MouseTrap':
        pyxel.blt(x,y,0,64,96,32,32,colkey=11)
    if name == 'Poison':
        pyxel.blt(x,y,0,64,64,32,32,colkey=11)
    


def collision(x1,y1,s1,x2,y2,s2):
    return (x1+s1[0]>=x2 and x2+s2[0]>=x1) and (y1+s1[1]>=y2 and y2+s2[1]>=y1)

def pointInside(posX,posY,x,y,w,h):
    return (posX >= x and posX < x + w and
            posY >= y and posY < y + h)

def onTick(x):
    return pyxel.frame_count % x == 0





App()