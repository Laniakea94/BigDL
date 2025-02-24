#
# Copyright 2016 The BigDL Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from .base_metric import INCMetric


class PytorchINCMetric(INCMetric):
    def stack(self, preds, labels):
        import torch
        # calculate accuracy
        preds = torch.stack(preds)
        labels = torch.stack(labels)
        return preds, labels

    def to_scalar(self, tensor):
        return tensor.item()


class TensorflowINCMetric(INCMetric):
    def stack(self, preds, labels):
        import tensorflow as tf
        # calculate accuracy
        preds = tf.stack(preds)
        labels = tf.stack(labels)
        return preds, labels

    def to_scalar(self, tensor):
        return tensor.numpy()
