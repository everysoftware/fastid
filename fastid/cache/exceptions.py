class CacheError(Exception):
    pass


class KeyNotFoundError(CacheError):
    pass


class LockError(CacheError):
    pass


class LockLostError(LockError):
    pass
