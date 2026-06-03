import pyxel

CAM_W = 400
CAM_H = 300

TILE_SIZE = 16


class App:
    def __init__(self):
        pyxel.init(CAM_W,CAM_H)
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

        self.buttons.append(Button('play',30,30,100,50))
        self.buttons.append(Button('quit',30,90,100,50))


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

        self.world = World((0,0),(4,0),[(0,1),(0,2),(1,2),(2,2),(3,2),(4,2),(4,1)])


    def update(self):
        self.world.update()
    def draw(self):
        self.world.draw()

map = []

class World:
    def __init__(self, startPoint, endPoint, path):
        global map
        self.length = 12
        self.height = 12

        for i in range(self.length):
            tab = []
            for j in range(self.height):
                tab.append(0)
            map.append(tab)

        map[startPoint[1]][startPoint[0]] = 3 #Puts start point
        map[endPoint[1]][endPoint[0]] = 4 #Puts end point

        for coord in path :
            map[coord[1]][coord[0]] = 1


    def draw(self):
        pyxel.rect(0,0, 5*TILE_SIZE, CAM_H, col=7)
        pyxel.rect(CAM_W-5*TILE_SIZE,0, 5*TILE_SIZE, CAM_H, col=7)

        for Y in range(len(map)):
            for X in range(len(map[Y])):
                pyxel.rect(X*TILE_SIZE+5*TILE_SIZE, Y*TILE_SIZE, TILE_SIZE, TILE_SIZE, col=map[Y][X])

    def update(self):
        global map
        for Y in range(len(map)):
            for X in range(len(map[Y])):
                if map[Y][X]==0 and pyxel.btnp(pyxel.KEY_SPACE) and pointInside(pyxel.mouse_x, pyxel.mouse_y, 5*TILE_SIZE+X*TILE_SIZE, Y*TILE_SIZE, TILE_SIZE, TILE_SIZE):
                    map[Y][X]=2



class Player:
    def __init__(self):
        pass
    def update(self):
        pass
    def draw(self):
        pass
    

class Enemy:
    def __init__(self):
        pass
    def update(self):
        pass
    def draw(self):
        pass




class Towers(Button):
    def place(self,X,Y):
        self.x = X*TILE_SIZE
        self.y = Y*TILE_SIZE



class MouseTrap(Towers):
    pass

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
        if name != '':
            pyxel.text(self.x + self.w//2 - len(self.name)*2, self.y + self.h//2-3, self.name, 9)



def pointInside(posX,posY,x,y,w,h):
    return (posX >= x and posX < x + w and
            posY >= y and posY < y + h)






App()