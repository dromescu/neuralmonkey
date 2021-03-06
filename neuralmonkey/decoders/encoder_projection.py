"""Encoder Projection Module.

This module contains different variants of projection of encoders into the
initial state of the decoder.
"""


from typing import List, Optional, Callable

import tensorflow as tf

from neuralmonkey.model.stateful import Stateful
from neuralmonkey.nn.utils import dropout
from neuralmonkey.logging import log


# pylint: disable=unused-argument
# The function must conform the API
def empty_initial_state(train_mode: tf.Tensor,
                        rnn_size: Optional[int],
                        encoders: List[Stateful] = None) -> tf.Tensor:
    """Return an empty vector.

    Arguments:
        train_mode: tf 0-D bool Tensor specifying the training mode (not used)
        rnn_size: The size of the resulting vector
        encoders: The list of encoders (not used)
    """
    if rnn_size is None:
        raise ValueError("You must supply rnn_size for this type of "
                         "encoder projection")
    return tf.zeros([rnn_size])


def linear_encoder_projection(
        dropout_keep_prob: float) -> Callable[
            [tf.Tensor, Optional[int], Optional[List[Stateful]]],
            tf.Tensor]:
    """Return a linear encoder projection.

    Return a projection function which applies dropout on concatenated
    encoder final states and returns a linear projection to a rnn_size-sized
    tensor.

    Arguments:
        dropout_keep_prob: The dropout keep probability
    """
    def func(train_mode: tf.Tensor,
             rnn_size: Optional[int] = None,
             encoders: Optional[List[Stateful]] = None) -> tf.Tensor:
        """Linearly project encoders' encoded value.

        Linearly project encoders' encoded value to rnn_size
        and apply dropout.

        Arguments:
            train_mode: tf 0-D bool Tensor specifying the training mode
            rnn_size: The size of the resulting vector
            encoders: The list of encoders
        """
        if rnn_size is None:
            raise ValueError("You must supply rnn_size for this type of "
                             "encoder projection")

        if encoders is None or not encoders:
            raise ValueError("There must be at least one encoder for this type"
                             " of encoder projection")

        encoded_concat = tf.concat([e.output for e in encoders], 1)
        encoded_concat = dropout(
            encoded_concat, dropout_keep_prob, train_mode)

        return tf.layers.dense(encoded_concat, rnn_size,
                               name="encoders_projection")

    return func


def concat_encoder_projection(
        train_mode: tf.Tensor,
        rnn_size: Optional[int] = None,
        encoders: Optional[List[Stateful]] = None) -> tf.Tensor:
    """Create the initial state by concatenating the encoders' encoded values.

    Arguments:
        train_mode: tf 0-D bool Tensor specifying the training mode (not used)
        rnn_size: The size of the resulting vector (not used)
        encoders: The list of encoders
    """
    if encoders is None or not encoders:
        raise ValueError("There must be at least one encoder for this type "
                         "of encoder projection")

    if rnn_size is not None:
        assert rnn_size == sum(e.output.get_shape()[1].value
                               for e in encoders)

    encoded_concat = tf.concat([e.output for e in encoders], 1)

    # pylint: disable=no-member
    log("The inferred rnn_size of this encoder projection will be {}"
        .format(encoded_concat.get_shape()[1].value))
    # pylint: enable=no-member

    return encoded_concat
