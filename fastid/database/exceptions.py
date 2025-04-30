class RepositoryError(Exception):
    pass


class NoResultFoundError(RepositoryError):
    pass


class NotSupportedPaginationError(RepositoryError):
    pass
