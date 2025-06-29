import numpy as np
import torch
import torch.nn as nn

def flatten_model_weights(model):
    return np.concatenate([param.data.numpy().flatten() for param in model.parameters()])

def set_model_weights_from_flat(model, flat_weights):
    """Assign weights to model from a flat numpy array."""
    if not isinstance(flat_weights, np.ndarray):
        weights = np.asarray(flat_weights)
    else:
        weights = flat_weights
        #raise ValueError("flat_weights must be a numpy array")
    idx = 0
    for param in model.parameters():
        shape = param.shape
        size = np.prod(shape)
        param.data = torch.from_numpy(weights[idx:idx + size].reshape(shape)).float()
        idx += size