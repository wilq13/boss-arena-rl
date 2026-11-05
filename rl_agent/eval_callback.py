from stable_baselines3.common.callbacks import BaseCallback
from baselines import evaluate
from curriculum import make_attacks_env

class WinRateEvalCallback(BaseCallback):
    def __init__(self, eval_freq, best_model_path):
        super().__init__()

        self.eval_freq = eval_freq
        self.best_model_path = best_model_path
        self.eval_seeds = range(20000, 20030)
        self.best_win_rate = -1.0

    def _evaluate_model(self):
        
        def policy_factory(seed):
            def policy(obs):
                action, _ = self.model.predict(obs
                                               ,deterministic=True)
                return action
            return policy

        result = evaluate(
                make_attacks_env,
                policy_factory,
                seeds=self.eval_seeds,
        )

        self.logger.record("eval/win_rate", result["win_rate"])
        self.logger.record("eval/mean_reward", result["reward"])
        self.logger.record("eval/win_steps", result["win_steps"])
        self.logger.record("eval/damage_taken", result["damage_taken"])
        self.logger.record("eval/loss_damage_taken", result["loss_damage_taken"])
        for source, damage in result["damage_by_source"].items():
            self.logger.record(f"eval/damage_from_{source}", damage)
            self.logger.record(
                f"eval/loss_damage_from_{source}",
                result["loss_damage_by_source"][source],
            )
        self.logger.dump(step=self.num_timesteps)

        print(f"Оценка: победы {result['win_rate']:.1%}")

        if result["win_rate"] > self.best_win_rate:
            self.model.save(self.best_model_path)
            self.best_win_rate = result["win_rate"]

            print(f"Сохранена лучшая модель: {self.best_win_rate:.1%}")


    def _on_training_start(self):
        self._evaluate_model()

    def _on_training_end(self):
        self._evaluate_model()

    def _on_step(self):
        if self.n_calls % self.eval_freq == 0:
            self._evaluate_model()

        return True
