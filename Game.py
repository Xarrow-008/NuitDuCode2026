import pyxel

CAM_W = 800
CAM_H = 600


class App:
    def __init__(self):
        pyxel.init(CAM_W,CAM_H)
        pyxel.load('theme.pyxres')

        self.game = Game()

        pyxel.run(self.update,self.draw)

    def update(self):
        self.game.update()

    def draw(self):
        self.game.draw()


class Game:
    def __init__(self):
        self.state = Menu()
        self.switch = Switch()
    def update(self):
        self.state.update()

        self.checkSwitch()

    def draw(self):
        pyxel.cls(1)
        self.state.draw()

    def checkSwitch(self):
        if self.switch.ready:
            destination = self.switch.to
            if destination == 'InGame':
                self.state = InGame()

            else:
                self.switch.__init__()



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
        pass
    def update(self):
        pass
    def draw(self):
        pass

class InGame:
    def __init__(self):
        pass
    def update(self):
        pass
    def draw(self):
        pass

class World:
    def __init__(self):
        pass
    def update(self):
        pass
    def draw(self):
        pass

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





App()