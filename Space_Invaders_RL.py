import gym
import pygame
import random
import numpy as np
from gym import spaces
from step import update_player, update_bullets, update_enemies, check_collisions, failure
import numpy

class SpaceInvadersEnv(gym.Env):
    def __init__(self):
        # Score and lives
        self.score = 0
        self.lives = 5
        self.left_cooldown = 0
        self.right_cooldown = 0
        self.shoot_cooldown = 0

        # Player coordinates
        self.playerX = 400
        self.playerY = 550

        # Enemies, bullets, barriers, etc.
        self.animationOn = 0
        self.direction = 1
        self.enemySpeed = 5
        self.lastEnemyMove = 0
        self.bullet = None
        self.bulletspeed = 2
        self.bullets = []
        self.chance = 996
        self.done = False
        self.kills = 0
        self.lefts = 0
        self.rights = 0
        self.shoots = 0
        self.killsrecord = []
        self.shootsrecord = []
        self.rightsrecord = []
        self.leftsrecord = []
        self.scoresrecord = []

        self.enemies = []
        self.barrierParticles = []
        self._init_enemies()
        self._init_barriers()

        self.action_space = spaces.Discrete(4)
        self.observation_space = spaces.Box(low=0, high=1, shape=(10,), dtype=np.float32)

    def _init_enemies(self):
        self.enemies = []
        startY = 50
        startX = 50
        for row in range(6):
            row_enemies = []
            if row < 2:
                enemy_type = 0
            elif row < 4:
                enemy_type = 1
            else:
                enemy_type = 2
            for col in range(10):
                row_enemies.append({
                    'type': enemy_type,
                    'x': startX * col,
                    'y': startY * row,
                    'w': 35,
                    'h': 35
                })
            self.enemies.append(row_enemies)

    def _init_barriers(self):
        self.barrierParticles = []
        barrierDesign = [
            [], [0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0],
            [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0],
            [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
            [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
            [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1]
        ]
        space = 100
        barrierY_init = 400
        for offset in range(1, 5):
            barrierY = barrierY_init
            for row in barrierDesign:
                bx = 150 * offset
                for i, b in enumerate(row):
                    if b != 0:
                        self.barrierParticles.append({
                            'x': bx + 5 * i,
                            'y': barrierY,
                            'w': 5,
                            'h': 5
                        })
                barrierY += 3

    def reset(self):
        self.score = 0
        self.lives = 2
        self.playerX = 400
        self.playerY = 550
        self.animationOn = 0
        self.direction = 1
        self.enemySpeed = 5
        self.lastEnemyMove = 0
        self.bullet = None
        self.bulletspeed = 2
        self.bullets = []
        self.chance = 996
        self.done = False
        self._init_enemies()
        self._init_barriers()
        self.kills = 0
        self.lefts = 0
        self.rights = 0
        self.shoots = 0
        return self._get_obs()

    def _get_obs(self):
        # Nearest enemy
        min_dist = 9999
        nearest_enemy_x, nearest_enemy_y = 0, 0
        for row in self.enemies:
            for enemy in row:
                dx = enemy['x'] - self.playerX
                dy = enemy['y'] - self.playerY
                dist = (dx ** 2 + dy ** 2) ** 0.5
                if dist < min_dist:
                    min_dist = dist
                    nearest_enemy_x = enemy['x']
                    nearest_enemy_y = enemy['y']

        # Nearest bullet
        min_bullet_dist = 9999
        nearest_bullet_x, nearest_bullet_y = 0, 0
        for bullet in self.bullets:
            dx = bullet['x'] - self.playerX
            dy = bullet['y'] - self.playerY
            dist = (dx ** 2 + dy ** 2) ** 0.5
            if dist < min_bullet_dist:
                min_bullet_dist = dist
                nearest_bullet_x = bullet['x']
                nearest_bullet_y = bullet['y']

        obs = np.array([
            self.playerX / 800,
            self.playerY / 600,
            (nearest_enemy_x - self.playerX) / 800,
            (nearest_enemy_y - self.playerY) / 600,
            (nearest_bullet_x - self.playerX) / 800,
            (nearest_bullet_y - self.playerY) / 600,
            self.lives / 5,
            self.score / 5000,
            1 if self.bullet is not None else 0,
            sum(len(row) for row in self.enemies) / 60,
        ], dtype=np.float32)
        return obs

    def step(self, action):
        reward = 0

        # Cooldown decrement
        if self.left_cooldown > 0:
            self.left_cooldown -= 1
        if self.right_cooldown > 0:
            self.right_cooldown -= 1
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        # Process action
        true_action = 0  # Default: do nothing

        if action == 1 and self.left_cooldown == 0:
            true_action = 1
            self.left_cooldown = 2
        elif action == 2 and self.right_cooldown == 0:
            true_action = 2
            self.right_cooldown = 2
        elif action == 3 and self.shoot_cooldown == 0 and self.bullet is None:
            true_action = 3
            self.shoot_cooldown = 5
        # Otherwise, do not respond (still in cooldown)

        reward += update_player(self, true_action)
        self.enemySpeed = min(30, max(10, self.score / 300))
        update_bullets(self)
        update_enemies(self)
        reward += check_collisions(self)

        if failure(self):
            self.done = True
            self.killsrecord.append(self.kills)
            self.scoresrecord.append(self.score)

            print(f'You Lose! Score:{self.score}. kills:{self.kills} lefts:{self.lefts} rights:{self.rights} shoots:{self.shoots} Rec_kills:{np.mean(self.killsrecord[-10:])} Rec_score:{np.mean(self.scoresrecord[-10:])}')
        elif all(len(row) == 0 for row in self.enemies):
            self.done = True
            self.score += 1000
            reward += 1000
            print(f'You Win! Score:{self.score}. kills:{self.kills} lefts:{self.lefts} rights:{self.rights} shoots:{self.shoots}')

        return self._get_obs(), reward, self.done, {}

    def render(self, mode='human'):
        if not hasattr(self, 'screen'):
            pygame.init()
            self.screen = pygame.display.set_mode((800, 600))
            pygame.display.set_caption('Space Invaders RL')
        self.screen.fill((0, 0, 0))

        # ==== Player (flashing or color change when invincible) ====
        if hasattr(self, 'invincible') and self.invincible > 0:
            # Flash every 2 frames
            if self.invincible % 4 < 2:
                pygame.draw.rect(self.screen, (52, 200, 255), (self.playerX, self.playerY, 35, 35))  # Light blue
        else:
            pygame.draw.rect(self.screen, (52, 255, 0), (self.playerX, self.playerY, 35, 35))  # Normal green

        # ==== Enemies ====
        for row in self.enemies:
            for enemy in row:
                pygame.draw.rect(self.screen, (255, 255, 255), (enemy['x'], enemy['y'], enemy['w'], enemy['h']))

        # ==== Player bullet ====
        if self.bullet is not None:
            pygame.draw.rect(self.screen, (0, 255, 0),
                             (self.bullet['x'], self.bullet['y'], self.bullet['w'], self.bullet['h']))

        # ==== Enemy bullets ====
        for bullet in self.bullets:
            pygame.draw.rect(self.screen, (255, 0, 0), (bullet['x'], bullet['y'], bullet['w'], bullet['h']))

        # ==== Barriers ====
        for barrier in self.barrierParticles:
            pygame.draw.rect(self.screen, (0, 200, 0), (barrier['x'], barrier['y'], barrier['w'], barrier['h']))

        # ==== Score and lives ====
        font = pygame.font.SysFont("arial", 18)
        text = font.render(f"Lives: {self.lives}  Score: {int(self.score)}", True, (255, 255, 255))
        self.screen.blit(text, (10, 10))

        pygame.display.flip()