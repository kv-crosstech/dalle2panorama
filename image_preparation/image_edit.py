from typing import List

import numpy as np

from image_preparation.data import Directions


def replace_logo(im: np.ndarray, old_im: np.ndarray, direction: Directions):
    """
    shifts the new image to the right and replaces the logo in the image
    with the logo in the new_im
    """
    if direction == Directions.RIGHT:
        old_im = shift(old_im, direction=Directions.RIGHT)
    if direction == Directions.DOWN:
        old_im = shift(old_im, direction=Directions.DOWN)
    im[-17:, -81:] = old_im[-17:, -81:]
    return im


def cut_logo(im: np.ndarray):
    """
    sets the logo in the lower right corner to black

    logo is positioned 17 pixels by Y from the bottom and 81 pixels by X from the right
    alpha channel is edited to 0
    """
    im[-17:, -81:] = 0
    im[-17:, -81:, 3] = 0
    return im


def shift(
    im: np.ndarray,
    direction: Directions,
    num_pixels: int = 1024 - 1024 // 3,
    to_cut_logo: bool = True,
) -> np.ndarray:
    """
    Shifts the image (4d array) in the given direction by num_pixels pixels
    If image shifts to the left or up, the logo is cutted off
    And then sets alpha channel of shifted pixels to 0
    :param im: 4d array of the image
    :param direction: direction to shift the image
    :param num_pixels: number of pixels to shift the image
    :param to_cut_logo: if True, logo is cutted off at LEFT and UP directions
    :return: shifted image, but only 1024 pixels of it in given direction
    """
    new_im = np.zeros(im.shape, dtype=im.dtype)
    new_im[:, :] = im[:, :].copy()
    if direction == Directions.LEFT:
        if to_cut_logo:
            new_im = cut_logo(new_im)
        new_im[:, :-num_pixels] = new_im[:, num_pixels:]
        new_im[:, -num_pixels:] = 0
        new_im[:, -num_pixels:, 3] = 0
        new_im = new_im[:, -1024:]  # leave only 1024 pixels to the left

    elif direction == Directions.RIGHT:
        new_im[:, num_pixels:] = new_im[:, :-num_pixels]
        new_im[:, :num_pixels] = 0
        new_im[:, :num_pixels, 3] = 0
        new_im = new_im[:, :1024]  # leave only 1024 pixels to the right

    elif direction == Directions.UP:
        if to_cut_logo:
            new_im = cut_logo(new_im)
        new_im[:-num_pixels, :] = new_im[num_pixels:, :]
        new_im[-num_pixels:, :] = 0
        new_im[-num_pixels:, :, 3] = 0
        new_im = new_im[-1024:, :]  # leave only 1024 pixels to the top
    elif direction == Directions.DOWN:
        new_im[num_pixels:, :] = new_im[:-num_pixels, :]
        new_im[:num_pixels, :] = 0
        new_im[:num_pixels, :, 3] = 0
        new_im = new_im[:1024, :]  # leave only 1024 pixels to the bottom

    return new_im


def shift_large(
    im: np.ndarray,
    direction: Directions,
    num_pixels: int = 1024 - 1024 // 3,
    to_cut_logo: bool = True,
    default_shape: int = 1024,
) -> List[np.ndarray]:
    """
    :param im: 4d array of the image
    :param direction: direction to shift the image
    :param num_pixels: number of pixels to shift the image
    :param to_cut_logo: if True, logo is cutted off at LEFT and UP directions
    :param default_shape: default shape of the generated image
    :return: List of images 1024 by 1024, they are part of the input image
            with num_pixels pixels shifted
    """
    shifted_image = shift(
        im, direction=direction, num_pixels=num_pixels, to_cut_logo=to_cut_logo
    )

    # if the image is not of the default shape,
    # slice it to the default shape images each with shift of num_pixels
    ret = []

    if (
        shifted_image.shape[0] != default_shape
        or shifted_image.shape[1] != default_shape
    ):
        if direction == Directions.LEFT or direction == Directions.RIGHT:
            max_shift = shifted_image.shape[0]
        else:
            max_shift = shifted_image.shape[1]
        for num_shift in range(0, max_shift - num_pixels, num_pixels):

            # if direction is left or right, go vertically
            # else go horizontally
            if direction == Directions.LEFT or direction == Directions.RIGHT:
                ret.append(
                    shifted_image[num_shift : num_shift + default_shape, :]
                )
            else:
                ret.append(
                    shifted_image[:, num_shift : num_shift + default_shape]
                )
    else:
        ret.append(shifted_image)
    return ret
