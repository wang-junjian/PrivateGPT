import threading

class SingletonMeta(type):
    _instances = {}
    _lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            with cls._lock:
                if cls not in cls._instances:
                    cls._instances[cls] = super(SingletonMeta, cls).__call__(*args, **kwargs)
        
        return cls._instances[cls]

class Model(metaclass=SingletonMeta):
    
    def __init__(self):
        self.model = None

    def load(self, config):
        pass

    def __call__(self):
        return self.model
