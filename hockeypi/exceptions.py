class UnknownPlayerException(Exception):
    def __init__(self, message):
      super().__init__(message)

class TeamNotFoundException(Exception):
    def __init__(self, message):
      super().__init__(message)

class PlayerNotFoundException(Exception):
    def __init__(self, message):
      super().__init__(message)