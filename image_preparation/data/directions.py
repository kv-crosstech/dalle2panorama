from enum import Enum


class Directions(str, Enum):
    # Values for the shift (this side image shifts)
    # Strings used in filenames (which side generation shall apply)
    LEFT = "RIGHT"
    RIGHT = "LEFT"
    UP = "DOWN"
    DOWN = "UP"


class CombinedDirections(str, Enum):
    LEFT_RIGHT = "LEFT and RIGHT"
    UP_DOWN = "UP and DOWN"

    def __str__(self):
        return self.value
