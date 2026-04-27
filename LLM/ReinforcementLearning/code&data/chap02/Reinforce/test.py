import gymnasium
import torch
from cart import Agent

# --------------- 环境初始化（带渲染）---------------
env = gymnasium.make('CartPole-v1', render_mode="human")  # v1 + 图形渲染

agent = Agent()
# 加载模型
agent.pi.load_state_dict(torch.load('policy_model.pth', weights_only=True))
agent.pi.eval()  # 推理模式


def test_render(agent, env, episodes=5):
    for episode in range(episodes):
        state, _ = env.reset()
        done = False
        total_reward = 0

        while not done:
            # 实时画图
            env.render()

            # 动作选择
            action, _ = agent.get_action(state)

            # 执行动作
            next_state, reward, terminated, truncated, _ = env.step(action)
            done = terminated or truncated

            state = next_state
            total_reward += reward

        print(f"回合 {episode + 1}: 总奖励 = {total_reward}")

    env.close()


if __name__ == '__main__':
    test_render(agent, env)