class NotFoundError(Exception):
    """Объект не найден."""

    pass


class AlreadyExistsError(Exception):
    """Объект с такими данными уже существует."""

    pass
