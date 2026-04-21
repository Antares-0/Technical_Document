import time
import numpy as np
import gymnasium as gym

# 🔥 关键：用 render_mode="human" 原生显示，不用 matplotlib！
env = gym.make("CartPole-v1", render_mode="human")

state, info = env.reset()
done = False

while not done:
    # 环境会自动弹出窗口实时显示画面
    env.render()

    # 每1秒执行一步动作
    action = np.random.choice([0, 1])
    state, reward, terminated, truncated, info = env.step(action)
    done = terminated or truncated

    print(f"状态: {state.round(2)} | 奖励: {reward}")

    # 1秒刷新一次
    time.sleep(1)

env.close()