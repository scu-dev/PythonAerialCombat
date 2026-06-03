import math

SINE_AMPLITUDE = 112
SINE_FREQUENCY = 2.5
ZIGZAG_HORIZONTAL_SPEED = 155.0


def moveStraightDown(rect, deltaSeconds, elapsedSeconds, startX, startY, speed, direction, playArea):
    rect.centerx = int(startX)
    rect.y = int(startY + elapsedSeconds * speed)
    return direction


def moveSineWave(rect, deltaSeconds, elapsedSeconds, startX, startY, speed, direction, playArea):
    offsetX = math.sin(elapsedSeconds * SINE_FREQUENCY) * SINE_AMPLITUDE
    rect.centerx = int(startX + offsetX)
    rect.y = int(startY + elapsedSeconds * speed)
    keepRectInsidePlayArea(rect, playArea)
    return direction


def moveZigzag(rect, deltaSeconds, elapsedSeconds, startX, startY, speed, direction, playArea):
    rect.y += int(speed * deltaSeconds)
    rect.x += int(ZIGZAG_HORIZONTAL_SPEED * direction * deltaSeconds)

    if rect.left <= playArea.left:
        rect.left = playArea.left
        direction = 1
    if rect.right >= playArea.right:
        rect.right = playArea.right
        direction = -1

    return direction


def keepRectInsidePlayArea(rect, playArea):
    if rect.left < playArea.left:
        rect.left = playArea.left
    if rect.right > playArea.right:
        rect.right = playArea.right