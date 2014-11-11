import pygame,sys
from pygame.locals import *
#
# Settings
#
SCREEN_W = 240
SCREEN_H = 320
FPS = 60
LINE_W=2
CODE = '2341'
VALUE = ''
MAX_CHARS = 6

#
# Palette
#
BLACK = 0x000000
WHITE = Color(0xFFFFFFFF)
RED = Color(0xCC333FFF)
BLUE = 0x00A0B0
ORANGE = Color(0xEC833EFF)
YELLOW = Color(0xEDC951FF)
BROWN = 0x6A4A3C

#
# State
#
class State:
    def __init__(self):
        self._display_list = None

    def on_init(self):
        pass

    def on_event(self,event):
        pass

    def on_loop(self):
        pass

    def on_render(self,surface):
        if self._display_list != None:
            self._display_list.draw(surface)
            self._display_list.update()

    def on_cleanup(self):
        pass

    def add(self,obj):
        if self._display_list == None:
            self._display_list = pygame.sprite.Group()

        self._display_list.add(obj)
        return obj

#
# State Manager
#
class StateManager(object):

    _currentState = None

    class __metaclass__(type):

        @property
        def currentState(cls):
            return cls._currentState

        @currentState.setter
        def currentState(cls,value):
            
            if value != cls._currentState:
                if cls._currentState != None:
                    cls._currentState.on_cleanup()
                    
                cls._currentState = value
                cls._currentState.on_init()

#
# Lock Controller
#
class LockController(object):
    def __init__(self,openCode,maxChars):
        self.openCode = openCode
        self.maxChars = maxChars
        self.currentCode = ''

    def input(self,symbol):
        if symbol=='#':
            self.clear()
        else:
            self.currentCode+=symbol
            if self.currentCode == self.openCode:
                print 'open'
                self.clear()
                StateManager.currentState = openState

            if len(self.currentCode) > self.maxChars:
                self.clear()
                
    def clear(self):
        self.currentCode=''
#
# GUI
#
class Button(pygame.sprite.Sprite):
    def __init__(self,label="", x=0,y=0,size=[64,48]):

        pygame.sprite.Sprite.__init__(self)

        self.is_down = False
        self.rect = pygame.Rect(0,0,size[0],size[1])

        self.label = label
        normalLabel = font.render(self.label,1,ORANGE);
        downLabel = font.render(self.label,1,WHITE);

        self.surfaceNormal = pygame.Surface(size)
        pygame.draw.rect(self.surfaceNormal, BLACK,self.rect )
        self.surfaceNormal.blit(normalLabel,(8,8))
        
        self.surfaceDown = pygame.Surface(size)
        pygame.draw.rect(self.surfaceDown, RED,self.rect )
        self.surfaceDown.blit(downLabel,(8,8))
        
        self.image = self.surfaceNormal

        self.rect.x = x
        self.rect.y = y   

    def update(self):
        if self.is_down:
            if not pygame.mouse.get_pressed()[0]:
                self.is_down =  False
                self.image = self.surfaceNormal
        else:
            if pygame.mouse.get_pressed()[0] and self.rect.collidepoint(pygame.mouse.get_pos()):
                self.is_down = True
                self.image = self.surfaceDown
                controller.input(self.label)
                
    def move(self,x,y):
        self.rect.x = x
        self.rect.y = y   

#
# Applicaton States
#
class OpenState(State):
    def on_init(self):
        self.initTime = pygame.time.get_ticks()
##        self.timer = 0
        pass

    def on_render(self,surface):
        surface.fill(BLACK)
        text = font.render('OPEN',1,ORANGE);
        position = text.get_rect()
        position.centerx = SCREEN_W/2
        position.centery = 48
        surface.blit(text,position)
        

        if(pygame.time.get_ticks() - self.initTime) >=3000:
            StateManager.currentState = inputState    
        
class InputState(State):
    def __init__(self):
        State.__init__(self)
        
        self.add(Button("1",13,81))
        self.add(Button("2",88,81))
        self.add(Button("3",163,81))
        
        self.add(Button("4",13,141))
        self.add(Button("5",88,141))
        self.add(Button("6",163,141))
        
        self.add(Button("7",13,201))
        self.add(Button("8",88,201))
        self.add(Button("9",163,201))
        
        self.add(Button("*",13,261))
        self.add(Button("0",88,261))
        self.add(Button("#",163,261))

    def on_render(self,surface):
        surface.fill(BLACK)
        mask = '*' * len(controller.currentCode)
        codeMask = maskFont.render(mask,1,ORANGE);
        position = codeMask.get_rect()
        position.centerx = SCREEN_W/2
        position.centery = 48
        surface.blit(bg_image,[0,0])
        surface.blit(codeMask,position)
        State.on_render(self,surface)
             
#
# Main Apllication Class
#
class App:

    def __init__(self,width,height,fps=60):

        self._runnting = True
        self._display_surf = None
        self.size = width,height
        self.fps = fps
        self._curStateIndex=0
        pygame.init()
        self._display_surf = pygame.display.set_mode(self.size)
        pygame.display.set_caption("Lock")

    def on_init(self):
        self._running = True
        self._clock = pygame.time.Clock()

    def on_event(self,event):
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            self._running = False

        if StateManager.currentState != None:
            StateManager.currentState.on_event(event)
        

    def on_loop(self):
        if StateManager.currentState != None:
            StateManager.currentState.on_loop()

    def on_render(self):
        if StateManager.currentState != None:
            StateManager.currentState.on_render(self._display_surf)

    def on_cleanup(self):
        pygame.quit()
        sys.exit()

    def on_execute(self):
        if self.on_init() == False:
            self._running = False

        while self._running:
            for event in pygame.event.get():
                self.on_event(event)

            self.on_loop()
            self.on_render()

            pygame.display.flip()
            self._clock.tick(self.fps)

        self.on_cleanup()

if __name__ == "__main__":

    theApp = App(SCREEN_W,SCREEN_H,FPS)

    controller = LockController(CODE,MAX_CHARS)
    bg_image = pygame.image.load("assets/input_bg.jpg").convert()
    font = pygame.font.Font("assets/Bender.otf",32)
    maskFont = pygame.font.Font("assets/Bender.otf",64)


    openState = OpenState()
    inputState = InputState()
    StateManager.currentState = inputState
    theApp.on_execute()
