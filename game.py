import random
from typing import cast

import pygame

import settings
from assets import GameAssets
from sprites import BackgroundScroller, BossPlane, EnemyPlane, Missile, PlayerPlane


class Game:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption(settings.GAME_TITLE)
        self.screen = pygame.display.set_mode((settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.playArea = self.screen.get_rect()
        self.assets = GameAssets()
        self.titleFont = self.loadUiFont(54)
        self.largeFont = self.loadUiFont(38)
        self.smallFont = self.loadUiFont(24)
        self.tipFont = self.loadUiFont(24)
        self.running = True
        self.movementKeys: set[int] = set()
        self.isFiring: bool = False
        self.resetGame()
        self.state = settings.STATE_START

    def loadUiFont(self, size):
        for fontName in settings.UI_FONT_NAMES:
            fontPath = pygame.font.match_font(fontName)
            if fontPath is not None:
                return pygame.font.Font(fontPath, size)
        return pygame.font.Font(None, size)

    def runGame(self) -> None:
        while self.running:
            deltaSeconds = self.clock.tick(settings.FPS) / 1000.0
            self.handleEvents()
            self.updateGame(deltaSeconds)
            self.drawGame()

        pygame.quit()

    def resetGame(self) -> None:
        self.background = BackgroundScroller(self.assets.backgrounds)
        self.player = PlayerPlane(
            self.assets.loadImage("myPlane.png"),
            self.assets.loadImage(settings.PLAYER_MISSILE_FILE),
            self.playArea,
        )
        self.playerMissiles = pygame.sprite.Group()
        self.enemyMissiles = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.boss = None
        self.score = 0
        self.waveIndex = 0
        self.spawnedInWave = 0
        self.nextEnemySpawnMilliseconds = pygame.time.get_ticks() + 600
        self.finishedSpawningEnemies = False
        self.movementKeys.clear()
        self.isFiring = False

    def handleEvents(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                self.handleKeyDown(event.key)
            if event.type == pygame.KEYUP:
                self.handleKeyUp(event.key)

    def handleKeyDown(self, key) -> None:
        if key == pygame.K_ESCAPE:
            self.running = False
            return

        if key in (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT):
            self.movementKeys.add(key)
            return

        if key != pygame.K_SPACE:
            return

        if self.state in (settings.STATE_START, settings.STATE_WIN, settings.STATE_GAME_OVER):
            self.resetGame()
            self.state = settings.STATE_PLAYING
        self.isFiring = True

    def handleKeyUp(self, key) -> None:
        if key in self.movementKeys:
            self.movementKeys.remove(key)
        if key == pygame.K_SPACE:
            self.isFiring = False

    def updateGame(self, deltaSeconds) -> None:
        nowMilliseconds = pygame.time.get_ticks()
        self.background.updateBackground(deltaSeconds)

        if self.state != settings.STATE_PLAYING:
            return

        self.player.handleInput(self.movementKeys, deltaSeconds)

        if self.isFiring:
            playerMissile = self.player.shootMissile(nowMilliseconds)
            if playerMissile is not None:
                self.playerMissiles.add(playerMissile)

        self.spawnEnemyWave()
        self.updateEnemies(deltaSeconds, nowMilliseconds)
        self.updateBoss(deltaSeconds, nowMilliseconds)
        self.updateMissiles(deltaSeconds)
        self.handleCollisions(nowMilliseconds)
        if self.state != settings.STATE_PLAYING:
            return
        self.trySpawnBoss()

    def spawnEnemyWave(self) -> None:
        if self.finishedSpawningEnemies:
            return

        nowMilliseconds = pygame.time.get_ticks()
        if nowMilliseconds < self.nextEnemySpawnMilliseconds:
            return

        if self.waveIndex >= len(settings.ENEMY_WAVES):
            self.finishedSpawningEnemies = True
            return

        waveConfig = settings.ENEMY_WAVES[self.waveIndex]
        if self.spawnedInWave >= waveConfig["count"]:
            self.waveIndex += 1
            self.spawnedInWave = 0
            self.nextEnemySpawnMilliseconds = nowMilliseconds + settings.ENEMY_WAVE_DELAY_MS
            return

        self.spawnEnemy(waveConfig)
        self.spawnedInWave += 1
        self.nextEnemySpawnMilliseconds = nowMilliseconds + settings.ENEMY_SPAWN_INTERVAL_MS

    def spawnEnemy(self, waveConfig: settings.EnemyWaveConfig) -> None:
        frames = self.assets.loadAnimationFrames(waveConfig["frames"])
        missileImage = self.assets.loadImage(settings.ENEMY_MISSILE_FILE)
        margin = max(frame.get_width() for frame in frames) // 2 + 8
        startX = random.randint(margin, settings.WINDOW_WIDTH - margin)
        startY = -max(frame.get_height() for frame in frames) - random.randint(0, 60)

        enemy = EnemyPlane(
            frames,
            missileImage,
            (startX, startY),
            waveConfig["health"],
            waveConfig["score"],
            waveConfig["speed"],
            waveConfig["motion"],
            waveConfig["shootCooldownMs"],
            self.playArea,
        )
        self.enemies.add(enemy)

    def spawnBoss(self) -> None:
        bossImage = self.assets.loadScaledImage("enemyPlane_boss.png", settings.BOSS_WIDTH)
        missileImage = self.assets.loadImage(settings.ENEMY_MISSILE_FILE)
        self.boss = BossPlane(bossImage, missileImage, self.playArea)

    def trySpawnBoss(self) -> None:
        if self.boss is not None:
            return
        if not self.finishedSpawningEnemies:
            return
        if len(self.enemies) > 0:
            return

        self.spawnBoss()

    def updateEnemies(self, deltaSeconds, nowMilliseconds) -> None:
        for enemy in list(self.enemies):
            enemy.updatePosition(deltaSeconds)
            if enemy.isOutOfBounds(self.playArea):
                enemy.kill()
                continue

            enemyMissile = enemy.shootMissile(nowMilliseconds)
            if enemyMissile is not None:
                self.enemyMissiles.add(enemyMissile)

    def updateBoss(self, deltaSeconds, nowMilliseconds) -> None:
        if self.boss is None:
            return

        self.boss.updatePosition(deltaSeconds)
        for missile in self.boss.shootMissileBurst(nowMilliseconds):
            self.enemyMissiles.add(missile)

    def updateMissiles(self, deltaSeconds) -> None:
        for missileGroup in (self.playerMissiles, self.enemyMissiles):
            for missile in list(missileGroup):
                missile.updatePosition(deltaSeconds)
                if missile.isOutOfBounds(self.playArea):
                    missile.kill()

    def handleCollisions(self, nowMilliseconds) -> None:
        self.handleEnemyHits()
        self.handleBossHits()
        self.handlePlayerHits(nowMilliseconds)

        if self.player.health <= 0:
            self.state = settings.STATE_GAME_OVER

    def handleEnemyHits(self) -> None:
        for missileSprite in list(self.playerMissiles):
            missile = cast(Missile, missileSprite)
            for enemySprite in list(self.enemies):
                enemy = cast(EnemyPlane, enemySprite)
                if not missile.rect.colliderect(enemy.rect):
                    continue

                missile.kill()
                if enemy.takeDamage(missile.damage):
                    self.score += enemy.scoreValue
                    enemy.kill()
                break

    def handleBossHits(self) -> None:
        if self.boss is None:
            return

        for sprite in list(self.playerMissiles):
            missile = cast(Missile, sprite)
            if not self.boss.rect.colliderect(missile.rect):
                continue

            missile.kill()
            if self.boss.takeDamage(missile.damage):
                self.score += self.boss.scoreValue
                self.boss = None
                self.state = settings.STATE_WIN
                return

    def handlePlayerHits(self, nowMilliseconds) -> None:
        if nowMilliseconds < self.player.invincibleUntilMilliseconds:
            return

        missileHits = self.collectPlayerMissileHits()
        enemyHits = self.collectPlayerEnemyHits()
        bossHit = self.boss is not None and self.player.rect.colliderect(self.boss.rect)

        if missileHits or enemyHits or bossHit:
            self.player.takeDamage(nowMilliseconds)

    def collectPlayerMissileHits(self) -> bool:
        hasHit = False
        for sprite in list(self.enemyMissiles):
            missile = cast(Missile, sprite)
            if self.player.rect.colliderect(missile.rect):
                missile.kill()
                hasHit = True
        return hasHit

    def collectPlayerEnemyHits(self) -> bool:
        hasHit = False
        for sprite in list(self.enemies):
            enemy = cast(EnemyPlane, sprite)
            if self.player.rect.colliderect(enemy.rect):
                enemy.kill()
                hasHit = True
        return hasHit

    def drawGame(self) -> None:
        nowMilliseconds = pygame.time.get_ticks()
        self.background.drawBackground(self.screen)

        if self.state == settings.STATE_START:
            self.drawOverlay(settings.GAME_TITLE, settings.START_MESSAGE, settings.CONTROL_TIP)
        elif self.state == settings.STATE_PLAYING:
            self.drawPlayingScene(nowMilliseconds)
        elif self.state == settings.STATE_WIN:
            self.drawPlayingScene(nowMilliseconds)
            self.drawOverlay(settings.WIN_MESSAGE, settings.RESTART_MESSAGE)
        elif self.state == settings.STATE_GAME_OVER:
            self.drawPlayingScene(nowMilliseconds)
            self.drawOverlay(settings.GAME_OVER_MESSAGE, settings.RESTART_MESSAGE)

        pygame.display.flip()

    def drawPlayingScene(self, nowMilliseconds) -> None:
        self.playerMissiles.draw(self.screen)
        self.enemies.draw(self.screen)
        if self.boss is not None:
            self.screen.blit(self.boss.image, self.boss.rect)
        self.enemyMissiles.draw(self.screen)
        if self.player.isVisible(nowMilliseconds):
            self.screen.blit(self.player.image, self.player.rect)
        self.drawHud()

    def drawHud(self) -> None:
        bossHealth = 0 if self.boss is None else self.boss.health
        hudText = settings.HUD_TEXT.format(
            health=self.player.health,
            score=self.score,
            bossHealth=bossHealth,
        )
        hudImage = self.smallFont.render(hudText, True, settings.WHITE)
        self.screen.blit(hudImage, (12, 10))

    def drawOverlay(self, title, message, tip=None) -> None:
        overlay = pygame.Surface((settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill(settings.DARK_OVERLAY)
        self.screen.blit(overlay, (0, 0))

        titleImage = self.titleFont.render(title, True, settings.YELLOW)
        messageImage = self.largeFont.render(message, True, settings.WHITE)
        titleRect = titleImage.get_rect(center=(settings.WINDOW_WIDTH // 2, settings.WINDOW_HEIGHT // 2 - 48))
        messageRect = messageImage.get_rect(center=(settings.WINDOW_WIDTH // 2, settings.WINDOW_HEIGHT // 2 + 20))
        self.screen.blit(titleImage, titleRect)
        self.screen.blit(messageImage, messageRect)

        if tip is not None:
            tipImage = self.tipFont.render(tip, True, settings.WHITE)
            tipRect = tipImage.get_rect(center=(settings.WINDOW_WIDTH // 2, settings.WINDOW_HEIGHT // 2 + 66))
            self.screen.blit(tipImage, tipRect)