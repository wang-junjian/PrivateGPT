import os
import hashlib
import yaml
import redis


class KeyValueStore:
    def __init__(self, config):
        self.config = config

    def get(self, key):
        pass

    def set(self, key, value):
        pass

class RedisKeyValueStore(KeyValueStore):
    """
    docker run --name redis -d -p 6379:6379 -v $(pwd)/vectorstore/redis:/data redis redis-server --save 60 1
    docker run --name redis -it --rm -p 6379:6379 -v $(pwd)/vectorstore/redis:/data redis redis-server --save 60 1
    """

    def __init__(self, config):
        super().__init__(config)
        self.r = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, decode_responses=True)
        self.r.ping()

    def get(self, key):
        return self.r.get(key)

    def set(self, key, value):
        self.r.set(key, value)

class FileKeyValueStore(KeyValueStore):
    def __init__(self, config):
        super().__init__(config)
        self.kvs = self._read_kvs()

    def _get_storage_path(self):
        return os.path.join(self.config.DEDUPLICATION_DIRECTORY, 'keyvalues.yaml')
    
    def _read_kvs(self):
        try:
            with open(self._get_storage_path(), 'r') as f:
                return yaml.load(f, Loader=yaml.FullLoader)
        except FileNotFoundError:
            return {}
        
    def _write_kvs(self):
        with open(self._get_storage_path(), 'w') as f:
            yaml.dump(self.kvs, f)

    def get(self, key):
        return self.kvs.get(key)

    def set(self, key, value):
        self.kvs[key] = value
        self._write_kvs()


class FileDeduplication:
    def __init__(self, config):
        os.makedirs(config.DEDUPLICATION_DIRECTORY, exist_ok=True)

        try:
            self.key_value_store = RedisKeyValueStore(config=config)
        except redis.exceptions.ConnectionError:
            self.key_value_store = FileKeyValueStore(config=config)

    def get_file_hash(self, file_path):
        return hashlib.md5(open(file_path, 'rb').read()).hexdigest()
    
    def is_duplicated(self, file_hash):
        file_path = self.key_value_store.get(file_hash)
        return file_path is not None

    def set(self, file_hash, file_path):
        self.key_value_store.set(file_hash, file_path)
