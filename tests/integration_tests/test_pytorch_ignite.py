from typing import Iterable
from unittest.mock import patch

import pytest
from ignite.engine import Engine

import optuna
from optuna.testing.integration import DeterministicPruner
from optuna.testing.integration import create_running_trial


def test_pytorch_ignite_pruning_handler() -> None:
    def update(engine: Engine, batch: Iterable) -> None:

        pass

    trainer = Engine(update)
    evaluator = Engine(update)

    # The pruner is activated.
    study = optuna.create_study(pruner=DeterministicPruner(True))
    trial = create_running_trial(study, 1.0)

    handler = optuna.integration.PyTorchIgnitePruningHandler(trial, "accuracy", trainer)
    with patch.object(trainer, "state", epoch=3):
        with patch.object(evaluator, "state", metrics={"accuracy": 1}):
            with pytest.raises(optuna.TrialPruned):
                handler(evaluator)
            assert study.trials[0].intermediate_values == {3: 1}

    # The pruner is not activated.
    study = optuna.create_study(pruner=DeterministicPruner(False))
    trial = create_running_trial(study, 1.0)

    handler = optuna.integration.PyTorchIgnitePruningHandler(trial, "accuracy", trainer)
    with patch.object(trainer, "state", epoch=5):
        with patch.object(evaluator, "state", metrics={"accuracy": 2}):
            handler(evaluator)
            assert study.trials[0].intermediate_values == {5: 2}
