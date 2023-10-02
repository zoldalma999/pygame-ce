import pygame


pygame.mixer.init()
screen = pygame.display.set_mode((100, 100))

sfx = pygame.mixer.Sound("examples\\data\\boom.wav")
channel = pygame.mixer.Channel(1)

channel.set_source_location(90, 200)
channel.play(sfx)
pygame.time.delay(1500)
channel.play(sfx)
# channel.queue(sfx)

pygame.time.delay(3000)
