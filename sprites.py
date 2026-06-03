from __future__ import annotations

import random

import pygame

import motions
import settings


MOTION_FUNCTIONS = {
    "straight": motions.moveStraightDown,
    "sine": motions.moveSineWave,
    "zigzag": motions.moveZigzag,
}


class BackgroundScroller:
    def __init__(self, backgrounds) -> None:
        self.backgrounds = backgrounds
        self.currentIndex = 0
        self.nextIndex = 1 % len(backgrounds)
        self.offsetY = 0.0
        self.elapsedSwitchSeconds = 0.0

    def updateBackground(self, deltaSeconds) -> None:
        self.offsetY += settings.BACKGROUND_SCROLL_SPEED * deltaSeconds
        self.elapsedSwitchSeconds += deltaSeconds

        if self.offsetY >= settings.WINDOW_HEIGHT:
            self.offsetY -= settings.WINDOW_HEIGHT
            self.currentIndex = self.nextIndex
            self.nextIndex = (self.nextIndex + 1) % len(self.backgrounds)

        if self.elapsedSwitchSeconds >= settings.BACKGROUND_SWITCH_SECONDS:
            self.elapsedSwitchSeconds = 0.0
            self.nextIndex = (self.currentIndex + 1) % len(self.backgrounds)

    def drawBackground(self, screen) -> None:
        currentBackground = self.backgrounds[self.currentIndex]
        nextBackground = self.backgrounds[self.nextIndex]
        drawY = int(self.offsetY)

        screen.blit(currentBackground, (0, drawY))
        screen.blit(nextBackground, (0, drawY - settings.WINDOW_HEIGHT))


class Missile(pygame.sprite.Sprite):
    def __init__(self, image, center, velocity, damage, owner) -> None:
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(center=center)
        self.position = pygame.Vector2(self.rect.center)
        self.velocity = pygame.Vector2(velocity)
        self.damage = damage
        self.owner = owner

    def updatePosition(self, deltaSeconds) -> None:
        self.position += self.velocity * deltaSeconds
        self.rect.center = (round(self.position.x), round(self.position.y))

    def isOutOfBounds(self, playArea) -> bool:
        return (
            self.rect.bottom < playArea.top
            or self.rect.top > playArea.bottom
            or self.rect.right < playArea.left
            or self.rect.left > playArea.right
        )


class PlayerPlane(pygame.sprite.Sprite):
    def __init__(self, image, missileImage, playArea) -> None:
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.playArea = playArea
        self.rect.midbottom = (playArea.centerx, playArea.bottom - 28)
        self.position = pygame.Vector2(self.rect.center)
        self.missileImage = missileImage
        self.health = settings.PLAYER_HEALTH
        self.lastShotMilliseconds = -settings.PLAYER_MISSILE_COOLDOWN_MS
        self.invincibleUntilMilliseconds = 0

    def handleInput(self, movementKeys: set[int], deltaSeconds: float) -> None:
        movement = pygame.Vector2()
        if pygame.K_LEFT in movementKeys:
            movement.x -= 1
        if pygame.K_RIGHT in movementKeys:
            movement.x += 1
        if pygame.K_UP in movementKeys:
            movement.y -= 1
        if pygame.K_DOWN in movementKeys:
            movement.y += 1

        if movement.length_squared() > 0:
            movement = movement.normalize()
        self.position += movement * settings.PLAYER_SPEED * deltaSeconds
        self.rect.center = (round(self.position.x), round(self.position.y))
        self.rect.clamp_ip(self.playArea)
        self.position.update(self.rect.center)

    def shootMissile(self, nowMilliseconds):
        if nowMilliseconds - self.lastShotMilliseconds < settings.PLAYER_MISSILE_COOLDOWN_MS:
            return None

        self.lastShotMilliseconds = nowMilliseconds
        missileCenter = (self.rect.centerx, self.rect.top - 12)
        return Missile(
            self.missileImage,
            missileCenter,
            (0, settings.PLAYER_MISSILE_SPEED),
            settings.PLAYER_MISSILE_DAMAGE,
            "player",
        )

    def takeDamage(self, nowMilliseconds) -> None:
        if nowMilliseconds < self.invincibleUntilMilliseconds:
            return

        self.health -= 1
        self.invincibleUntilMilliseconds = nowMilliseconds + settings.PLAYER_INVINCIBLE_MS

    def isVisible(self, nowMilliseconds) -> bool:
        if nowMilliseconds >= self.invincibleUntilMilliseconds:
            return True
        return (nowMilliseconds // 120) % 2 == 0


class EnemyPlane(pygame.sprite.Sprite):
    def __init__(
        self,
        frames,
        missileImage,
        startCenter,
        health,
        scoreValue,
        speed,
        motionName,
        shootCooldownMilliseconds,
        playArea,
    ) -> None:
        super().__init__()
        self.frames = frames
        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=startCenter)
        self.startX = startCenter[0]
        self.startY = self.rect.y
        self.health = health
        self.scoreValue = scoreValue
        self.speed = speed
        self.motionName = motionName
        self.motionFunction = MOTION_FUNCTIONS[motionName]
        self.direction = random.choice([-1, 1])
        self.elapsedSeconds = 0.0
        self.animationSeconds = 0.0
        self.missileImage = missileImage
        self.shootCooldownMilliseconds = shootCooldownMilliseconds
        self.lastShotMilliseconds = random.randint(-shootCooldownMilliseconds, 0)
        self.playArea = playArea

    def updatePosition(self, deltaSeconds) -> None:
        self.elapsedSeconds += deltaSeconds
        self.animationSeconds += deltaSeconds
        frameIndex = int(self.animationSeconds * 8) % len(self.frames)
        self.image = self.frames[frameIndex]

        self.direction = self.motionFunction(
            self.rect,
            deltaSeconds,
            self.elapsedSeconds,
            self.startX,
            self.startY,
            self.speed,
            self.direction,
            self.playArea,
        )

    def shootMissile(self, nowMilliseconds):
        if nowMilliseconds - self.lastShotMilliseconds < self.shootCooldownMilliseconds:
            return None

        self.lastShotMilliseconds = nowMilliseconds
        missileCenter = (self.rect.centerx, self.rect.bottom + 16)
        return Missile(
            self.missileImage,
            missileCenter,
            (0, settings.ENEMY_MISSILE_SPEED),
            1,
            "enemy",
        )

    def takeDamage(self, damage) -> bool:
        self.health -= damage
        return self.health <= 0

    def isOutOfBounds(self, playArea) -> bool:
        return self.rect.top > playArea.bottom + 20


class BossPlane(pygame.sprite.Sprite):
    def __init__(self, image, missileImage, playArea) -> None:
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(midtop=(playArea.centerx, -image.get_height()))
        self.position = pygame.Vector2(self.rect.center)
        self.playArea = playArea
        self.health = settings.BOSS_HEALTH
        self.scoreValue = settings.BOSS_SCORE
        self.speed = settings.BOSS_SPEED
        self.direction = 1
        self.missileImage = missileImage
        self.lastShotMilliseconds = -settings.BOSS_MISSILE_COOLDOWN_MS

    def updatePosition(self, deltaSeconds) -> None:
        if self.rect.top < settings.BOSS_TARGET_TOP:
            self.position.y += self.speed * deltaSeconds
        else:
            self.position.x += self.direction * self.speed * deltaSeconds

        self.rect.center = (round(self.position.x), round(self.position.y))

        if self.rect.left <= self.playArea.left:
            self.rect.left = self.playArea.left
            self.direction = 1
        if self.rect.right >= self.playArea.right:
            self.rect.right = self.playArea.right
            self.direction = -1

        self.position.update(self.rect.center)

    def shootMissileBurst(self, nowMilliseconds):
        if nowMilliseconds - self.lastShotMilliseconds < settings.BOSS_MISSILE_COOLDOWN_MS:
            return []

        self.lastShotMilliseconds = nowMilliseconds
        missileCenters = [
            (self.rect.centerx - 78, self.rect.bottom - 16),
            (self.rect.centerx, self.rect.bottom + 8),
            (self.rect.centerx + 78, self.rect.bottom - 16),
        ]
        velocities = [
            (-150, settings.BOSS_MISSILE_SPEED),
            (0, settings.BOSS_MISSILE_SPEED + 45),
            (150, settings.BOSS_MISSILE_SPEED),
        ]

        missiles = []
        for missileCenter, velocity in zip(missileCenters, velocities):
            missiles.append(Missile(self.missileImage, missileCenter, velocity, 1, "enemy"))
        return missiles

    def takeDamage(self, damage) -> bool:
        self.health -= damage
        return self.health <= 0