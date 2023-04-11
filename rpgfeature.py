from constants import *

class RPGFeature:
    def __init__(self, name, img, desc):
        self.name = name
        self.img = pygame.image.load(img).convert_alpha()
        self.current_block = None
        self.desc = desc
        self.describing = False
    
    def draw(self, surface, x, y):
        surface.blit(self.img, (x, y))

all_rpg_features = {
            "portal1": RPGFeature(name='portal1', img='assets/png/portal1.png', desc='a golf portal'),
            "portal2": RPGFeature(name='portal2', img='assets/png/portal2.png', desc='another golf portal'),
            "portal3": RPGFeature(name='portal3', img='assets/png/portal3.png', desc='yet another golf portal'),
            "portal4": RPGFeature(name='portal4', img='assets/png/portal4.png', desc='just a golf portal')
            }