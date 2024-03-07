import threading

import pygame
import random
import socket


pygame.init()

#INITIALS
WIDTH, HEIGHT = 1000,600
wn = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong Game")
run = True
direction = [0, 1]
angle = [0, 1, 2, 3]
#Colors
BLUE = (0, 0, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
#Ball specs
radius = 15
ball_x, ball_y = WIDTH/2-radius, HEIGHT/2-radius
ball_vel_x, ball_vel_y = 20, 20

# Paddle specs
paddle_width, paddle_height = 20, 120
left_paddle_y = right_paddle_y = HEIGHT/2-paddle_height/2
left_paddle_x, right_paddle_x = 100-paddle_width/2, WIDTH- (100-paddle_width/2)
right_paddle_vel = left_paddle_vel = 0

# Screen Elements
score_p1 = 0
score_p2 = 0

# Main Loop
while run:
    wn.fill(BLACK)

    for i in pygame.event.get():
        if i.type == pygame.QUIT:
            run = False
        elif i.type == pygame.KEYDOWN:
            if i.key == pygame.K_UP: #K_UP prints as integer 1073741906
                right_paddle_vel =-0.7
            if i.key == pygame.K_DOWN: #K_DOWN prints as integer 1073741905
                right_paddle_vel = 0.7
            if i.key == pygame.K_w:
                left_paddle_vel =  -0.7
            if i.key == pygame.K_s:
                left_paddle_vel = 0.7
            if i.type == pygame.KEYUP:
                right_paddle_vel = 0
                left_paddle_vel = 0

    # Ball's moves control
    if ball_y <= 0 + radius or ball_y >= HEIGHT-radius:
        ball_vel_y *= -1
    if ball_x  >= WIDTH-radius:
        score_p1 += 1
        ball_x, ball_y = WIDTH/2 - radius, HEIGHT/2 - radius
        dir = random.choice(direction)
        ang = random.choice(angle)
        if dir == 0:
            if ang == 0:
                ball_vel_y, ball_vel_x = -0.4, 0.2
            if ang == 1:
                ball_vel_y, ball_vel_x = -0.2, 0.2
            if ang == 2:
                ball_vel_y, ball_vel_x = -0.2, 0.4

        if dir == 1:
            if ang == 0:
                ball_vel_y, ball_vel_x = 0.4, 0.2
            if ang == 1:
                ball_vel_y, ball_vel_x = 0.2, 0.2
            if ang == 2:
                ball_vel_y, ball_vel_x = 0.2, 0.4
        ball_vel_x *= -1
    if ball_x <= 0 + radius:
        score_p2 += 1
        ball_x, ball_y = WIDTH/2 - radius, HEIGHT/2 - radius
        dir = random.choice(direction)
        ang = random.choice(angle)
        if dir == 0:
            if ang == 0:
                ball_vel_y, ball_vel_x = -0.4, 0.2
            if ang == 1:
                ball_vel_y, ball_vel_x = -0.2, 0.2
            if ang == 2:
                ball_vel_y, ball_vel_x = -0.2, 0.4
        if dir == 1:
            if ang == 0:
                ball_vel_y, ball_vel_x = 0.4, 0.2
            if ang == 1:
                ball_vel_y, ball_vel_x = 0.2, 0.2
            if ang == 2:
                ball_vel_y, ball_vel_x = 0.2, 0.4
        ball_vel_x, ball_vel_y = 0.2, 0.2

    # Paddle's moves control
    if left_paddle_y >= HEIGHT - paddle_height:
        left_paddle_y = HEIGHT - paddle_height
    if left_paddle_y <= 0:
        left_paddle_y = 0
    if right_paddle_y >= HEIGHT - paddle_height:
        right_paddle_y = HEIGHT - paddle_height
    if right_paddle_y <= 0:
        right_paddle_y = 0
    # Collisions
    # left paddle
    if left_paddle_x <= ball_x <= left_paddle_x + paddle_width:
        if left_paddle_y <= ball_y <= left_paddle_y + paddle_height:
            ball_x = left_paddle_x + paddle_width
            ball_vel_x *= -1
    # right paddle
    if right_paddle_x <= ball_x <= right_paddle_x + paddle_width :
        if right_paddle_y <= ball_y <= right_paddle_y + paddle_height:
            ball_x = right_paddle_x
            ball_vel_x *= -1

    # Score board
    font = pygame.font.SysFont("callibri", 32)
    score = font.render("Player_1:" + str(score_p1), True, WHITE)
    wn.blit(score, (25, 25))
    score = font.render("Player_2:" + str(score_p2), True, WHITE)
    wn.blit(score, (WIDTH-200, 25))
    #Movements
    ball_x += ball_vel_x
    ball_y += ball_vel_y
    right_paddle_y += right_paddle_vel
    left_paddle_y += left_paddle_vel    # OBJECTS
    pygame.draw.circle(wn, BLUE, (ball_x, ball_y), radius)
    pygame.draw.rect(wn, RED, pygame.Rect(left_paddle_x, left_paddle_y, paddle_width, paddle_height))
    pygame.draw.rect(wn, RED, pygame.Rect(right_paddle_x, right_paddle_y, paddle_width, paddle_height))
    pygame.display.update()
