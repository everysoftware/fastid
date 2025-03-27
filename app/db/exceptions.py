class RepositoryError(Exception):
    pass


class NoResultFoundError(RepositoryError):
    pass


class MultipleResultsFoundError(RepositoryError):
    pass
