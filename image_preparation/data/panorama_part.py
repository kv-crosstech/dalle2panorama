import numpy as np
from dataclasses import dataclass

from image_preparation.data import Directions


@dataclass
class PanoramaPart:
    path: str
    direction: Directions
    img: np.ndarray
    part_number: int
