class RepositoryError(Exception):
    pass


class NoResultFound(RepositoryError):
    pass


class MultipleResultsFound(RepositoryError):
    pass
