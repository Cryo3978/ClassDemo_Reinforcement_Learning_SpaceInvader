from Space_Invaders_RL import SpaceInvadersEnv
from stable_baselines3 import DQN
# from gym.wrappers import RecordVideo
import pygame

if __name__ == "__main__":
    # ------- Training --------
    env = SpaceInvadersEnv()
    model = DQN('MlpPolicy', env, verbose=0, buffer_size=20000, learning_starts=20000, train_freq=4, batch_size=32)
    model.learn(total_timesteps=1000000)
    model.save("dqn_spaceinvaders")

    # ------- Test and Visualization --------
    env = SpaceInvadersEnv()
    model = DQN.load("dqn_spaceinvaders")
    obs = env.reset()
    done = False
    while not done:
        action, _ = model.predict(obs, deterministic=True)
        obs, reward, done, info = env.step(action)
        env.render()
        pygame.time.wait(30)