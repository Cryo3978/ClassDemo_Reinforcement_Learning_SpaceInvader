import random

def update_player(env, action):
    reward = 0
    step_size = 20
    player_width = 35
    # 0: Do nothing, 1: Move left, 2: Move right, 3: Shoot
    if action == 1 and env.playerX > 0:
        env.playerX -= step_size
        env.lefts += 1
        env.score += 0.1
        reward += 0.1
    elif action == 2 and env.playerX < 800 - player_width:
        env.playerX += step_size
        env.rights += 1
        env.score += 0.1
        reward += 0.1
    if action == 3 and env.bullet is None:
        env.shoots += 1
        env.bullet = {
            'x': env.playerX + player_width // 2 - 2,
            'y': env.playerY - 15,
            'w': 5,
            'h': 10
        }
    return reward

def update_bullets(env):
    # Player's bullet
    if env.bullet is not None:
        env.bullet['y'] -= 20
        if env.bullet['y'] < 0:
            env.bullet = None

    # Enemy bullets
    new_enemy_bullets = []
    for bullet in env.bullets:
        bulletspeed = max(2, env.score / 200)
        bullet['y'] += bulletspeed
        if bullet['y'] <= 600:
            new_enemy_bullets.append(bullet)
    env.bullets = new_enemy_bullets

def update_enemies(env):
    need_move_down = False
    for row in env.enemies:
        for enemy in row:
            enemy['x'] += env.enemySpeed * env.direction
            if enemy['x'] >= 750 or enemy['x'] <= 0:
                need_move_down = True

    if need_move_down:
        for row in env.enemies:
            for enemy in row:
                enemy['y'] += 10
        env.direction *= -1

    # Animation switching (optional)
    if env.animationOn:
        env.animationOn -= 1
    else:
        env.animationOn += 1

    # Enemies shoot
    for row in env.enemies:
        for enemy in row:
            if random.randint(0, 1000) > env.chance and len(env.bullets) <= 11:
                env.bullets.append({
                    'x': enemy['x'] + enemy['w'] // 2,
                    'y': enemy['y'] + enemy['h'],
                    'w': 5,
                    'h': 10
                })

def check_collisions(env):
    reward = 0
    # Player's bullet hits an enemy
    if env.bullet is not None:
        bullet = env.bullet
        hit = False
        for row in env.enemies:
            for enemy in row:
                if (bullet['x'] < enemy['x'] + enemy['w'] and
                    bullet['x'] + bullet['w'] > enemy['x'] and
                    bullet['y'] < enemy['y'] + enemy['h'] and
                    bullet['y'] + bullet['h'] > enemy['y']):
                    row.remove(enemy)
                    env.bullet = None
                    env.chance = max(10, env.chance - 0.2)
                    env.score += 100
                    reward += 100
                    env.kills += 1
                    hit = True
                    break
            if hit:
                break
        # Bullet hits a barrier
        if env.bullet is not None:
            hit_barrier = None
            for p in env.barrierParticles:
                if (bullet['x'] < p['x'] + p['w'] and
                    bullet['x'] + bullet['w'] > p['x'] and
                    bullet['y'] < p['y'] + p['h'] and
                    bullet['y'] + bullet['h'] > p['y']):
                    hit_barrier = p
                    break
            if hit_barrier is not None:
                env.barrierParticles.remove(hit_barrier)
                env.bullet = None
                reward -= 0.1
                env.score -= 0.1

    # Enemy bullets hit the player (invincibility frame check)
    if hasattr(env, 'invincible') and env.invincible > 0:
        env.invincible -= 1
    else:
        hit_bullet = None
        player_rect = {
            'x': env.playerX, 'y': env.playerY,
            'w': 35, 'h': 35
        }
        for bullet in env.bullets:
            if (bullet['x'] < player_rect['x'] + player_rect['w'] and
                bullet['x'] + bullet['w'] > player_rect['x'] and
                bullet['y'] < player_rect['y'] + player_rect['h'] and
                bullet['y'] + bullet['h'] > player_rect['y']):
                hit_bullet = bullet
                break
        if hit_bullet is not None:
            env.lives -= 1
            env.bullets.remove(hit_bullet)
            env.playerX = 400  # Reset player
            env.invincible = 90  # 30 frames invincible
            # You can add sound effects or special effects here

    # Enemy bullet hits a barrier
    to_remove_bullet = None
    to_remove_barrier = None
    for bullet in env.bullets:
        for p in env.barrierParticles:
            if (bullet['x'] < p['x'] + p['w'] and
                bullet['x'] + bullet['w'] > p['x'] and
                bullet['y'] < p['y'] + p['h'] and
                bullet['y'] + bullet['h'] > p['y']):
                to_remove_bullet = bullet
                to_remove_barrier = p
                break
        if to_remove_bullet:
            break
    if to_remove_bullet and to_remove_barrier:
        env.bullets.remove(to_remove_bullet)
        env.barrierParticles.remove(to_remove_barrier)
    return reward

def failure(env):
    bottom_limit = 550
    for row in env.enemies:
        for column in row:
            if column['h'] + column['y'] >= bottom_limit:
                return True
    if env.lives <= 0:
        return True
    return False