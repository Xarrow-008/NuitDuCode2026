import pyxel

CAM_W = 400
CAM_H = 300

TILE_SIZE = 16

MARGIN = 5*TILE_SIZE

FPS = 60

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
        pyxel.cls(0)
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

        self.world = World([(0,0),(0,1),(0,2),(1,2),(2,2),(3,2),(4,2),(4,1),(4,0)])
        
        self.enemies = []
        self.enemies.append(Car(self.world.path))

        self.towers = []


        self.lives = 50
        self.money = 0


    def update(self):
        self.world.update()

        self.enemiesUpdate()

        self.towersUpdate()

    def enemiesUpdate(self):
        for enemy in self.enemies:
            enemy.update()



            if enemy.health <= 0:
                self.enemies.remove(enemy)
                enemy.onDeath()
                self.money += enemy.maxHealth

            for enemy in enemy.spawned:
                self.enemies.append(enemy)

            if self.world.map[enemy.coord[1]][enemy.coord[0]].state.place == 'end' and enemy.health > 0:
                self.lives -= enemy.damage
                self.enemies.remove(enemy)

    def draw(self):
        self.world.draw()

        pyxel.text(1, 1, f"Vies restantes : {self.lives}", 8)
        pyxel.text(21*TILE_SIZE,1, f"Argent : {self.money}", 9)

        for enemy in self.enemies:
            enemy.draw()

    def createTower(self,X,Y):
        pass

    def towersUpdate(self):
        pass



class World:
    def __init__(self, path):
        self.width = 15
        self.height = 19

        self.map = [[Case(x,y) for x in range(self.width)] for y in range(self.height)]

        self.path = path

        for coord in path:
            case = self.map[coord[1]][coord[0]]
            case.state = PathCase(case.x,case.y)

        self.map[path[0][1]][path[0][0]].state.place = 'start' #Puts start point
        self.map[path[-1][1]][path[-1][0]].state.place = 'end' #Puts end point

        


    def draw(self):
        pyxel.rect(0,0, MARGIN, CAM_H, col=7)
        pyxel.rect(CAM_W-MARGIN,0, 5*TILE_SIZE, CAM_H, col=7)

        for line in self.map:
            for case in line:
                case.draw()
                

    def update(self):
        for line in self.map:
            for case in line:
                if case.state.name == 'empty' and pyxel.btnp(pyxel.KEY_SPACE) and pointInside(pyxel.mouse_x, pyxel.mouse_y, case.x, case.y, TILE_SIZE, TILE_SIZE):
                    case.state = TowerCase(case.x,case.y)


    
class Enemy:
    def __init__(self, health, cooldown, damage, path):
        self.maxHealth = health
        self.health = health
        self.cooldown = cooldown
        self.damage = damage

        self.width = 8
        self.height = 8
        
        self.indice = 0
        self.path = path
        self.coord = path[0]
        self.movingCoord = [path[0][0],path[0][1]]
        self.travelled = [(self.coord[0], self.coord[1])]

        self.spawned = []

    def update(self):
        if onTick(self.cooldown):
            self.movingCoord = [self.coord[0], self.coord[1]]
            self.indice += 1
            self.coord = self.path[self.indice]

        else:
            self.movingCoord[0] += pyxel.sgn(self.coord[0]-self.movingCoord[0])*1/self.cooldown
            self.movingCoord[1] += pyxel.sgn(self.coord[1]-self.movingCoord[1])*1/self.cooldown


    def draw(self):
        pyxel.rect(5*TILE_SIZE+self.movingCoord[0]*TILE_SIZE+4, self.movingCoord[1]*TILE_SIZE+4, self.width, self.height, col=7)

    def onDeath(self):
        pass

class Spider(Enemy):
    def __init__(self, path):
        super().__init__(health = 10, cooldown=0.4*FPS, damage=3, path=path)

class Soldier(Enemy):
    def __init__(self, path):
        super().__init__(health = 10, cooldown=0.5*FPS, damage=5, path=path)

class General(Enemy):
    def __init__(self, path):
        super().__init__(health = 30, cooldown=1*FPS, damage=20, path=path)

    def onDeath(self):
        for i in range(3):
            self.spawned.append(Soldier())

class Dino(Enemy):
    def __init__(self, path):
        super().__init__(health = 50, cooldown=2*FPS, damage=40, path=path)

class Car(Enemy):
    def __init__(self, path):
        super().__init__(health=5, cooldown=0.2*FPS, damage=10, path=path)


class Button:
    def __init__(self,x,y,w,h,name='',color=1):
        self.name = name
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def pressed(self):
        return pointInside(pyxel.mouse_x, pyxel.mouse_y, self.x,self.y,self.w,self.h) and pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT)

    def draw(self):
        pyxel.rect(self.x,self.y,self.w,self.h,1)
        if self.name != '':
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
        self.name = 'empty'

    def update(self):
        if self.pressed():
            self.selectTower = True
            
    def draw(self):
        pyxel.rect(self.x,self.y,self.w,self.h,1)
    
    def pressed(self):
        return pointInside(pyxel.mouse_x, pyxel.mouse_y, self.x,self.y,self.w,self.h) and pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT)

class PathCase:
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.w = TILE_SIZE
        self.h = TILE_SIZE

        self.place = 'mid'
        self.name = 'path'
            
    def draw(self):
        if self.place == 'start':
            pyxel.rect(self.x,self.y,self.w,self.h,8)
        elif self.place == 'end':
            pyxel.rect(self.x,self.y,self.w,self.h,3)
        else:
            pyxel.rect(self.x,self.y,self.w,self.h,4)

class TowerCase:
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.w = TILE_SIZE
        self.h = TILE_SIZE

        self.name = 'tower'

    def update(self):
        pass

    def draw(self):
        pyxel.rect(self.x,self.y,self.w,self.h,2)

class SlingShot:
    def __init__(self,x,y):
        self.x = x
        self.y = y

    def update(self):
        pass





def pointInside(posX,posY,x,y,w,h):
    return (posX >= x and posX < x + w and
            posY >= y and posY < y + h)

def onTick(x):
    return pyxel.frame_count % x == 0





App()