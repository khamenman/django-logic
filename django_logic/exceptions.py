class DjangoLogicException(Exception):
    pass


class TransitionNotAllowed(DjangoLogicException):
    def __init__(self, *args, hints=None):
        super().__init__(*args)
        self.hints = hints or []
