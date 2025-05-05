class CacheError(Exception):
    pass


class KeyNotFoundError(CacheError):
    pass
