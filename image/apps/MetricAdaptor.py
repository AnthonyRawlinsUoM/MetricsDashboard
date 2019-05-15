class MetricAdaptor:
    _initialised = False

    def __init__(self, metric, **adapted_methods):
        self.metric = metric
        for key, value in adapted_methods.items():
            func = getattr(self.metric, value)
            self.__setattr__(key, func)
        self._initialised = True

    def __setattr__(self, key, value):
        if not self._initialised:
            super().__setattr__(key, value)
        else:
            setattr(self.metric, key, value)

    def __getattr__(self, attr):
        return getattr(self.metric, attr)
