r"""Neural network language model module.

All language model classes must be re-imported in this file.

Attributes
==========
ALL_MODELS: List[:py:class:`lmp.model.BaseModel`]
    All available language models.
    Every time a new language model is added, it must also be added to
    ``ALL_MODELS`` list.
MODEL_OPTS: Final[Dict[str, :py:class:`lmp.model.BaseModel`]]
    Mapping from language model's name to language model's class.
    All language models must have class attribute ``model_name``.
PRIVA_MODELS: Final[Dict[str, List[torch.nn.Module]]]
    Mapping from language model's name to private models used internally.
    This is only used for documentation purpose.

Examples
========
Check ``'RNN'`` is an available language model.

>>> from lmp.model import MODEL_OPTS
>>> 'RNN' in MODEL_OPTS
True

Get ``'RNN'`` language model class.

>>> from lmp.model import RNNModel
>>> MODEL_OPTS['RNN'] == RNNModel
True
"""


from typing import Dict, Final, List

import torch.nn

from lmp.model._base import BaseModel
from lmp.model._gru import GRUModel
from lmp.model._lstm import LSTMModel
from lmp.model._res_gru import ResGRUBlock, ResGRUModel
from lmp.model._res_lstm import ResLSTMBlock, ResLSTMModel
from lmp.model._res_rnn import ResRNNBlock, ResRNNModel
from lmp.model._rnn import RNNModel

ALL_MODELS: Final[List[BaseModel]] = [
    GRUModel,
    LSTMModel,
    RNNModel,
    ResGRUModel,
    ResRNNModel,
    ResLSTMModel,
]
MODEL_OPTS: Final[Dict[str, BaseModel]] = {m.model_name: m for m in ALL_MODELS}
PRIVA_MODELS: Final[Dict[str, List[torch.nn.Module]]] = {
    ResGRUModel.model_name: [ResGRUBlock],
    ResLSTMModel.model_name: [ResLSTMBlock],
    ResRNNModel.model_name: [ResRNNBlock],
}
