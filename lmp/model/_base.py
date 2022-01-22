"""Language model base class."""

import abc
import argparse
from typing import Any, ClassVar, Optional, Tuple

import torch

import lmp.dset
import lmp.util.path


class BaseModel(abc.ABC, torch.nn.Module):
  """Language model abstract base class.

  Implement basic functionalities for language model, including training loss calculation, next token id prediction
  and parsing training arguments.

  Parameters
  ----------
  kwargs: typing.Any, optional
    Useless parameter.  Intently left for subclasses inheritance.

  Attributes
  ----------
  model_name: typing.ClassVar[str]
    CLI Display name of the model.  Only used to parse CLI arguments.
  """

  model_name: ClassVar[str] = 'base'

  def __init__(self, **kwargs: Any):
    super().__init__()

  @abc.abstractmethod
  def forward(self, batch_cur_tkids: torch.Tensor, batch_next_tkids: torch.Tensor) -> torch.Tensor:
    """Calculate language model training loss.

    This method must only be used to train model.  For inference use :py:meth:`lmp.model.BaseModel.pred` instead.

    Parameters
    ----------
    batch_cur_tkids: torch.Tensor
      Batch of token ids which represent input token ids of all time steps.  ``batch_cur_tkids`` has shape
      ``(batch_size, seq_len)`` and ``dtype == torch.int``.
    batch_next_tkids: torch.Tensor
      Batch of token ids which represent prediction targets of all time steps.  ``batch_next_tkids`` has the same shape
      and ``dtype`` as ``batch_cur_tkids``.

    Returns
    -------
    torch.Tensor
      Mini-batch loss of next token id prediction.  Returned tensor has shape ``(1)`` and ``dtype == torch.float``.

    See Also
    --------
    lmp.tknzr.BaseTknzr.enc
      Token encoding was done by tokenizers.
    """
    raise NotImplementedError

  @torch.no_grad()
  @abc.abstractmethod
  def pred(
    self,
    batch_cur_tkids: torch.Tensor,
    batch_prev_states: Optional[torch.Tensor] = None,
  ) -> Tuple[torch.Tensor, torch.Tensor]:
    """Calculate next token id probability distribution given previous hidden states and current input token id.

    This method must only be used for inference.  For training use :py:meth:`lmp.model.BaseModel.forward` instead.  No
    tensor graphs will be constructed and no gradients will be calculated.

    Parameters
    ----------
    batch_cur_tkids: torch.Tensor
      Batch of current input token ids.  ``batch_cur_tkids`` has shape ``(batch_size)`` and ``dtype == torch.int``.
    batch_prev_states: typing.Optional[torch.Tensor], default: None
      Batch of previous calculation results.  Set to ``None`` to use initial hidden state.  Different models have
      different hidden state structure.

    Returns
    -------
    tuple[torch.Tensor, torch.Tensor]
      The first tensor is the batch of next token id probability distribution.  The first tensor has shape
      ``(batch_size, vocab_size)`` and ``dtype == torch.float``.  The second tensor is the current hiddent state.
      Different models have different hidden state structure.
    """
    raise NotImplementedError

  @classmethod
  def train_parser(cls, parser: argparse.ArgumentParser) -> None:
    """CLI arguments parser for training language model.

    Parameters
    ----------
    parser: argparse.ArgumentParser
      CLI arguments parser.

    Returns
    -------
    None

    See Also
    --------
    lmp.script.train_model
      Language model training script.

    Examples
    --------
    >>> import argparse
    >>> from lmp.model import BaseModel
    >>> parser = argparse.ArgumentParser()
    >>> BaseModel.train_parser(parser)
    >>> args = parser.parse_args([
    ...   '--batch_size', '32',
    ...   '--beta1', '0.9',
    ...   '--beta2', '0.99',
    ...   '--ckpt_step', '1000',
    ...   '--dset_name', 'wiki-text-2',
    ...   '--eps', '1e-8',
    ...   '--exp_name', 'my_exp',
    ...   '--log_step', '200',
    ...   '--lr', '1e-4',
    ...   '--max_norm', '1',
    ...   '--max_seq_len', '-1',
    ...   '--n_epoch', '10',
    ...   '--tknzr_exp_name', 'my_tknzr_exp',
    ...   '--ver', 'train',
    ...   '--wd', '1e-2',
    ... ])
    >>> args.batch_size == 32
    True
    >>> args.beta1 == 0.9
    True
    >>> args.beta2 == 0.99
    True
    >>> args.ckpt_step == 1000
    True
    >>> args.dset_name == 'wiki-text-2'
    True
    >>> args.eps == 1e-8
    True
    >>> args.exp_name == 'my_exp'
    True
    >>> args.log_step == 200
    True
    >>> args.lr == 1e-4
    True
    >>> args.max_norm == 1
    True
    >>> args.max_seq_len == -1
    True
    >>> args.n_epoch == 10
    True
    >>> args.seed == 42
    True
    >>> args.tknzr_exp_name == 'my_tknzr_exp'
    True
    >>> args.ver == 'train'
    True
    >>> args.wd == 1e-2
    True
    """
    # `parser` validation.
    lmp.util.validate.raise_if_not_instance(val=parser, val_name='parser', val_type=argparse.ArgumentParser)

    # Required arguments.
    group = parser.add_argument_group('language model training arguments')
    group.add_argument(
      '--batch_size',
      help='Mini-batch size.',
      required=True,
      type=int,
    )
    group.add_argument(
      '--beta1',
      help='First beta coefficient of AdamW optimizer.',
      required=True,
      type=float,
    )
    group.add_argument(
      '--beta2',
      help='Second beta coefficient of AdamW optimizer.',
      required=True,
      type=float,
    )
    group.add_argument(
      '--ckpt_step',
      help='Checkpoint save interval.',
      required=True,
      type=int,
    )
    group.add_argument(
      '--dset_name',
      choices=lmp.dset.DSET_OPTS.keys(),
      help='Name of the dataset which will be used to train language model.',
      required=True,
      type=str,
    )
    group.add_argument(
      '--eps',
      help='Denominator smooth term of AdamW optimizer.',
      required=True,
      type=float,
    )
    group.add_argument(
      '--exp_name',
      help='Name of the language model training experiment.',
      required=True,
      type=str,
    )
    group.add_argument(
      '--log_step',
      help='Performance log interval.',
      required=True,
      type=int,
    )
    group.add_argument(
      '--lr',
      help='Learning rate.',
      required=True,
      type=float,
    )
    group.add_argument(
      '--max_norm',
      help='Gradient max-norm constraint.',
      required=True,
      type=float,
    )
    group.add_argument(
      '--max_seq_len',
      help=' '.join(['Maximum sequence length constraint.', 'Set to `-1` to allow arbitrary token sequence length.']),
      required=True,
      type=int,
    )
    group.add_argument(
      '--n_epoch',
      help='Number of training epochs.',
      required=True,
      type=int,
    )
    group.add_argument(
      '--tknzr_exp_name',
      help='Name of the pre-trained tokenizer experiment.',
      required=True,
      type=str,
    )
    group.add_argument(
      '--ver',
      help='Version of the dataset.',
      required=True,
      type=str,
    )
    group.add_argument(
      '--wd',
      help='Weight decay coefficient of AdamW optimizer.',
      required=True,
      type=float,
    )

    # Optional arguments.
    group.add_argument(
      '--seed',
      default=42,
      help='Random seed.',
      type=int,
    )
