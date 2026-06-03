import pygame

import settings


class GameAssets:
    def __init__(self) -> None:
        self.images = {}
        self.backgrounds = self.loadBackgrounds()

    def loadImage(self, fileName):
        if fileName in self.images:
            return self.images[fileName]

        imagePath = settings.RESOURCE_DIR / fileName
        image = pygame.image.load(str(imagePath)).convert_alpha()
        self.images[fileName] = image
        return image

    def loadScaledImage(self, fileName, targetWidth):
        image = self.loadImage(fileName)
        scale = targetWidth / image.get_width()
        targetHeight = int(image.get_height() * scale)
        return pygame.transform.smoothscale(image, (targetWidth, targetHeight))

    def loadAnimationFrames(self, fileNames):
        return [self.loadImage(fileName) for fileName in fileNames]

    def loadBackgrounds(self):
        backgrounds = []
        for fileName in settings.BACKGROUND_FILES:
            imagePath = settings.RESOURCE_DIR / fileName
            background = pygame.image.load(str(imagePath)).convert()
            if background.get_size() != (settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT):
                background = pygame.transform.smoothscale(
                    background,
                    (settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT),
                )
            backgrounds.append(background)
        return backgrounds