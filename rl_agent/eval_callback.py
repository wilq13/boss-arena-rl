from stable_baselines3.common.callbacks import BaseCallback
from baselines import evaluate


class WinRateEvalCallback(BaseCallback):
    def __init__(self, eval_freq, best_model_path, env_factory, label):
        super().__init__()

        self.eval_freq = eval_freq
        self.best_model_path = best_model_path
        self.env_factory = env_factory
        self.label = label
        self.eval_seeds = range(20000, 20100)
        self.best_win_rate = -1.0

    def _evaluate_model(self):
        def policy_factory(seed):
            def policy(obs):
                action, _ = self.model.predict(
                    obs, deterministic=True
                )
                return action
            return policy

        result = evaluate(
            self.env_factory,
            policy_factory,
            seeds=self.eval_seeds,
        )

        print(f"{self.label}: победы {result['win_rate']:.1%}")

        if result["win_rate"] > self.best_win_rate:
            self.model.save(self.best_model_path)
            self.best_win_rate = result["win_rate"]

            print(
                f"{self.label}: сохранена лучшая модель "
                f"({self.best_win_rate:.1%})"
            )

        metrics = {
            "win_rate": result["win_rate"],
            "best_win_rate": self.best_win_rate,
            "mean_reward": result["reward"],
            "win_steps": result["win_steps"],
            "damage_taken": result["damage_taken"],
            "loss_damage_taken": result["loss_damage_taken"],
        }

        for key, value in metrics.items():
            self.logger.record(f"{self.label}/{key}", value)

        for source, damage in result["damage_by_source"].items():
            self.logger.record(
                f"{self.label}/damage_from_{source}", damage
            )
            self.logger.record(
                f"{self.label}/loss_damage_from_{source}",
                result["loss_damage_by_source"][source],
            )

        self.logger.record("time/total_timesteps", self.num_timesteps)
        self.logger.dump(step=self.num_timesteps)

    def _on_training_start(self):
        self._evaluate_model()

    def _on_training_end(self):
        self._evaluate_model()

    def _on_step(self):
        if self.n_calls % self.eval_freq == 0:
            self._evaluate_model()

        return True
