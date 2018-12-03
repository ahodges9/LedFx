import numpy as np
from functools import lru_cache

@lru_cache(maxsize=32)
def _normalized_linspace(size):
    return np.linspace(0, 1, size)

def interpolate(y, new_length):
    """Resizes the array by linearly interpolating the values"""

    if len(y) == new_length:
        return y

    x_old = _normalized_linspace(len(y))
    x_new = _normalized_linspace(new_length)
    z = np.interp(x_new, x_old, y)
    
    return z


@lru_cache(maxsize=32)
def _easing_func(x, height=1, length=1, slope=2.4, lean=1):
    # Apply easing function to value x.
    # https://www.desmos.com/calculator/stq7jdlrak
    g = (x / length) ** slope
    return (height * g) / (g + (1 - x / length) ** slope)

def ease_array(x, height, length, slope=2.4, lean=1):
    # Apply easing function over each value in np.array x.
    # https://www.desmos.com/calculator/stq7jdlrak
    g = np.power(np.divide(x, length), slope)
    return np.divide((height * g), (g + np.power((1 - np.divide(x, length)), lean*slope)))

class TemporalFilter:
    """Exponential smoothing filter across time for a 2d array of pixels"""

    def __init__(self, val=None, rise=0.5, decay=0.5):
        assert type(val) is np.ndarray
        self.val = val.T
        self.exp_filters = []
        self.n_filters = self.val.shape[0]
        for i in range(self.n_filters):
            self.exp_filters.append(ExpFilter(np.zeros(self.val.shape[1]),
                                              alpha_rise=rise,
                                              alpha_decay=decay))

    def update(self, val):
        for i in range(self.n_filters):
            self.val[i] = self.exp_filters[i].update(val.T[i])
        return self.val.T


class ExpFilter:
    """Simple exponential smoothing filter"""

    def __init__(self, val=None, alpha_decay=0.5, alpha_rise=0.5):
        assert 0.0 < alpha_decay < 1.0, 'Invalid decay smoothing factor'
        assert 0.0 < alpha_rise < 1.0, 'Invalid rise smoothing factor'
        self.alpha_decay = alpha_decay
        self.alpha_rise = alpha_rise
        self.value = val

    def update(self, value):

        # Handle deferred initilization
        if self.value is None:
            self.value = value
            return self.value

        if isinstance(self.value, (list, np.ndarray, tuple)):
            alpha = value - self.value
            alpha[alpha > 0.0] = self.alpha_rise
            alpha[alpha <= 0.0] = self.alpha_decay
        else:
            alpha = self.alpha_rise if value > self.value else self.alpha_decay
        self.value = alpha * value + (1.0 - alpha) * self.value

        return self.value