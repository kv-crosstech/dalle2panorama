from typing import List, Optional, Dict

import cv2
import numpy as np
import os

from image_preparation import shift, shift_large, replace_logo
from image_preparation.data import Directions, PanoramaPart


def prepare_panorama(
    impath: str, directions: Optional[List[Directions]] = None
):
    """
    Prepare for image generation
    Read the image. Shift the image and save it near the other with name
    {impath}_shifted.png
    :param impath: path to the image
    :param directions: list of directions to shift the image
    :return: None
    """
    if directions is None:
        directions = Directions
    folder = os.path.dirname(impath)
    basename = os.path.basename(impath)
    basename_without_extension = os.path.splitext(basename)[0]
    im = cv2.imread(impath, cv2.IMREAD_UNCHANGED)
    im = cv2.cvtColor(im, cv2.COLOR_RGB2RGBA)
    for direction in directions:
        shifted_im = shift(im, direction=direction)
        cv2.imwrite(
            os.path.join(
                folder, basename_without_extension + f"_{direction}.png"
            ),
            shifted_im,
        )


def prepare_full_panorama(
    impath: str, directions: Optional[List[Directions]] = None
) -> Dict[Directions, List[PanoramaPart]]:
    """
    Prepare for image generation
    Read the image. Shift the image and save it near the other with name
    {impath}_shifted.png
    :param impath: path to the image
    :param directions: list of directions to shift the image
    :return: dictionary of shifted images
    """
    if directions is None:
        directions = Directions
    folder = os.path.dirname(impath)
    basename = os.path.basename(impath)
    basename_without_extension = os.path.splitext(basename)[0]
    im = cv2.imread(impath, cv2.IMREAD_UNCHANGED)
    im = cv2.cvtColor(im, cv2.COLOR_RGB2RGBA)
    ret = {}
    for direction in directions:
        ret[direction] = []
        # shifted_ims = shift_large(im, direction=direction)
        shifted_ims = shift_large(im, direction=direction)
        for i, shifted_im in enumerate(shifted_ims):
            shifted_im_name = os.path.join(
                folder,
                basename_without_extension + f"_{direction}_{i:03d}.png",
            )

            ret[direction].append(
                PanoramaPart(
                    path=shifted_im_name,
                    direction=direction,
                    img=shifted_im,
                    part_number=i,
                )
            )
    return ret


def combine_parts(
    old_part: PanoramaPart, new_part: PanoramaPart, num_pixels=1024 // 3
) -> PanoramaPart:
    """
    :param old_part:
    :param new_part:
    :return:
    """
    ret_part = PanoramaPart(
        path=new_part.path,
        part_number=new_part.part_number,
        direction=new_part.direction,
        img=new_part.img,
    )
    if old_part.direction == Directions.UP:
        ret_part.img[:, :num_pixels, :] = old_part.img[:, -num_pixels:, :]
    elif old_part.direction == Directions.DOWN:
        ret_part.img[:, :num_pixels, :] = old_part.img[:, -num_pixels:, :]
    elif old_part.direction == Directions.LEFT:
        ret_part.img[:num_pixels, :, :] = old_part.img[-num_pixels:, :, :]
    elif old_part.direction == Directions.RIGHT:
        ret_part.img[:num_pixels, :, :] = old_part.img[-num_pixels:, :, :]

    return ret_part


def combine_images(
    impath: str,
    directions: Optional[List[Directions]] = None,
    num_pixels: int = 1024 - 1024 // 3,
) -> str:
    """
    Combine the images with the given direction images
    Reads image, reads direction_done image.
    Image should be extended to the size of num_pixels in the opposite
    direction, then changes from direction_done are applied to the image
    :param impath: path to the image
    :param directions: list of directions to combine the image
    :param num_pixels: number of pixels to extend the image in any direction
    :return: combined_path
    """
    folder = os.path.dirname(impath)
    basename = os.path.basename(impath)
    basename_without_extension = os.path.splitext(basename)[0]
    if directions is None:
        directions = Directions
    im = cv2.imread(impath, cv2.IMREAD_UNCHANGED)
    im = cv2.cvtColor(im, cv2.COLOR_RGB2RGBA)
    for direction in directions:
        im_direction = cv2.imread(
            os.path.join(
                folder, basename_without_extension + f"_{direction}_done.png"
            ),
            cv2.IMREAD_UNCHANGED,
        )
        im_direction = cv2.cvtColor(im_direction, cv2.COLOR_RGB2RGBA)
        if direction == Directions.LEFT:
            # extend image to the right
            im = np.concatenate(
                (
                    im,
                    np.zeros((im.shape[0], num_pixels, 4), dtype=im.dtype),
                ),
                axis=1,
            )
            # replace new part with im_direction
            im[:, -1024:] = im_direction
        if direction == Directions.RIGHT:
            # replace logo
            im_direction = replace_logo(im_direction, im, direction=direction)
            # extend image to the left
            im = np.concatenate(
                (
                    np.zeros((im.shape[0], num_pixels, 4), dtype=im.dtype),
                    im,
                ),
                axis=1,
            )
            # replace new part with im_direction
            im[:, :1024] = im_direction
        if direction == Directions.UP:
            # extend image to the bottom
            im = np.concatenate(
                (
                    im,
                    np.zeros((num_pixels, im.shape[1], 4), dtype=im.dtype),
                ),
                axis=0,
            )
            # replace new part with im_direction
            im[-1024:, :] = im_direction
        if direction == Directions.DOWN:
            # replace logo
            im_direction = replace_logo(
                im_direction, im[:1024], direction=direction
            )
            # im_direction[-17:, -81:] = im[1024-17:1024, 1024-81:1024]

            # extend image to the top
            im = np.concatenate(
                (
                    np.zeros((num_pixels, im.shape[1], 4), dtype=im.dtype),
                    im,
                ),
                axis=0,
            )
            # replace new part with im_direction
            im[:1024, :] = im_direction
    combined_path = os.path.join(
        folder, basename_without_extension + f"_full.png"
    )
    cv2.imwrite(
        combined_path,
        im,
    )
    return combined_path
