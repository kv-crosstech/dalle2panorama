"""
This is the main window
It should be able to:
    1) Load an image
    2) Process an image (prepare_panorama)
    3) If image is too large - prepare only parts of it and then combine live
    3) Ask user to complete the image in web browser
    4) After pressing OK, combine the images (function combine_images)

For now it's semi-automatic process. Image generation is on user.
TODO: Later use api module for image generation.
"""
import os
import tkinter as tk
import tkinter.filedialog
from typing import List, Dict

import cv2
import numpy as np

from image_preparation import cut_logo
from image_preparation.data import Directions, PanoramaPart
from image_preparation.data.directions import CombinedDirections
from image_preparation.panorama_dalle2 import (
    combine_parts,
    combine_images,
    prepare_full_panorama,
)
from PIL import Image, ImageTk


class MainWindowFull(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Panorama dalle 2")
        self.geometry("1900x800")
        self.resizable(False, False)
        self.filename = None
        self.impath = None
        self.directions = None
        self.parts: Dict[Directions, List[PanoramaPart]] = {}
        self.current_part = None
        self.current_direction = None
        self.chosen_directions = [
            tk.Variable(value="0"),
            tk.Variable(value="0"),
        ]
        self.num_pixels = 1024 - 1024 // 3
        self.prepare_panorama_button = None
        self.next_part_ready_button = None
        self.create_widgets()

    def create_widgets(self):
        # left column is buttons only
        # right column contains one cell which is image
        left_column = tk.Frame(self)
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)

        right_column = tk.Frame(self)
        right_column.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # load image button
        self.load_image_button = tk.Button(
            left_column,
            text="Load image",
            command=self.load_image,
        )
        self.load_image_button.pack(fill=tk.X, expand=True)

        # show directions checkboxes
        directions_frame = tk.Frame(left_column)
        directions_frame.pack(fill=tk.BOTH, expand=False)
        self.directions_checkboxes = []
        for i, direction in enumerate(CombinedDirections):
            checkbox = tk.Checkbutton(
                directions_frame,
                text=str(direction),
                variable=self.chosen_directions[i],
            )
            checkbox.pack(side=tk.LEFT, fill=tk.X, expand=False)
            # add new line
            if i % 2 == 1:
                directions_frame = tk.Frame(left_column)
                directions_frame.pack(fill=tk.BOTH, expand=False)
            self.directions_checkboxes.append(checkbox)

        self.image_label = tk.Label(right_column)
        self.image_label.pack(fill=tk.BOTH, expand=True)

        # prepare panorama button
        self.prepare_panorama_button = tk.Button(
            left_column,
            text="Prepare panorama",
            command=self.prepare_panorama,
        )
        self.prepare_panorama_button.pack(fill=tk.X, expand=True)

        # next button
        self.next_part_ready_button = tk.Button(
            left_column,
            text="Next part ready",
            command=self.next_part,
        )
        self.next_part_ready_button.pack(fill=tk.X, expand=True)

        # combine images button
        # self.combine_images_button = tk.Button(
        #     left_column,
        #     text="Combine images",
        #     command=self.combine_images,
        # )
        # self.combine_images_button.pack(fill=tk.X, expand=True)

    def prepare_panorama(self):
        chosen_directions = [
            direction if x.get() == "1" else None
            for x, direction in zip(self.chosen_directions, CombinedDirections)
        ]
        print(chosen_directions)
        print([x.get() for x in self.chosen_directions])
        # filter None out
        chosen_directions = [
            direction for direction in chosen_directions if direction
        ]
        if len(chosen_directions) > 1:
            raise ValueError("Only one combined direction is supported")

        if CombinedDirections.LEFT_RIGHT in chosen_directions:
            self.directions = [Directions.LEFT, Directions.RIGHT]
        elif CombinedDirections.UP_DOWN in chosen_directions:
            self.directions = [Directions.UP, Directions.DOWN]
        self.impath = self.filename
        if self.impath:
            self.parts: Dict[
                Directions, List[PanoramaPart]
            ] = prepare_full_panorama(self.impath, self.directions)
            for dir in self.parts:
                print(dir, len(self.parts[dir]))

            # View OK pop-up and tell paths to the generated images
            self.view_ok_popup()

    def get_done(self, part: PanoramaPart):
        folder = os.path.dirname(part.path)
        basename = os.path.basename(part.path)
        basename_without_extension = os.path.splitext(basename)[0]
        done_path = os.path.join(
            folder, basename_without_extension + f"_done.png"
        )
        if not os.path.exists(done_path):
            raise ValueError(f"{done_path} does not exist")
        im = cv2.imread(done_path, cv2.IMREAD_UNCHANGED)
        im = cv2.cvtColor(im, cv2.COLOR_RGB2RGBA)
        return PanoramaPart(
            path=done_path,
            direction=part.direction,
            img=cut_logo(im),
            part_number=part.part_number,
        )

    def combine_parts(
        self,
        parts: List[PanoramaPart],
        num_pixels: int = 1024 // 3,
        default_shape=1024,
    ) -> np.ndarray:
        for part in parts:
            part.img = self.get_done(part).img
        result_img = parts[0].img
        # result-img save to

        direction: Directions = parts[0].direction
        for part in parts[1:]:
            # concatenate images given direction
            # UP and DOWN are concatenated left to right
            # LEFT and RIGHT are concatenated top to bottom
            # using np.concatenate.
            # result_img should be cut to the num_pixels from border.
            # New part is concatenated fully
            # each cycle result_img is cut to the num_pixels from border
            if direction == Directions.UP or direction == Directions.DOWN:
                result_img = np.concatenate(
                    (
                        result_img[:, :-num_pixels],
                        part.img,
                    ),
                    axis=1,
                )
            elif direction == Directions.LEFT or direction == Directions.RIGHT:
                result_img = np.concatenate(
                    (
                        result_img[:-num_pixels, :],
                        part.img,
                    ),
                    axis=0,
                )

        folder = os.path.dirname(self.impath)
        basename = os.path.basename(self.impath)
        basename_without_extension = os.path.splitext(basename)[0]
        result_path = os.path.join(
            folder, basename_without_extension + f"_{direction}_done.png"
        )
        print("saving", result_path)
        cv2.imwrite(result_path, result_img)
        return result_img

    def next_part(self):
        """

        :return:
        """
        if (
            self.parts is not None
            and self.current_part is None
            and self.current_direction is None
        ):
            self.current_part = 0
            self.current_direction = list(self.parts.keys())[0]

            cv2.imwrite(
                self.parts[self.current_direction][self.current_part].path,
                self.parts[self.current_direction][self.current_part].img,
            )
            self.display_image(
                self.parts[self.current_direction][self.current_part].path
            )
        elif (
            self.parts is not None
            and self.current_part is not None
            and self.current_direction is not None
        ):
            # merge parts together
            try:
                done_part = self.get_done(
                    self.parts[self.current_direction][self.current_part]
                )
                self.parts[self.current_direction][
                    self.current_part + 1
                ] = combine_parts(
                    done_part,
                    self.parts[self.current_direction][self.current_part + 1],
                )
            except IndexError:
                pass
            self.current_part += 1
            max_part = len(self.parts[self.current_direction]) - 1
            if self.current_part > max_part:
                # merge image on direction
                self.combine_parts(self.parts[self.current_direction])

                # get next part
                self.current_part = 0
                current_dir_id = list(self.parts.keys()).index(
                    self.current_direction
                )
                try:
                    self.current_direction = list(self.parts.keys())[
                        current_dir_id + 1
                    ]
                except IndexError:
                    # self.combine_parts(self.parts[self.current_direction])
                    combine_images(
                        impath=self.impath, directions=list(self.parts.keys())
                    )

                    # show _full image
                    folder = os.path.dirname(self.impath)
                    basename = os.path.basename(self.impath)
                    basename_without_extension = os.path.splitext(basename)[0]
                    result_path = os.path.join(
                        folder, basename_without_extension + f"_full.png"
                    )
                    self.display_image(result_path)
                    self.view_ok_popup()
                    return
            # write next part on disk
            cv2.imwrite(
                self.parts[self.current_direction][self.current_part].path,
                self.parts[self.current_direction][self.current_part].img,
            )
            self.display_image(
                self.parts[self.current_direction][self.current_part].path
            )

    def view_ok_popup(self):
        """Displays message Success and 'Press to close' button
        that closes window"""
        popup = tk.Tk()
        popup.title("Success")
        popup.geometry("300x100")
        popup.resizable(False, False)
        popup.wm_attributes("-topmost", 1)
        popup.configure(background="white")
        label = tk.Label(popup, text="Success", font=("Helvetica", 20))
        label.pack(fill=tk.BOTH, expand=True)
        button = tk.Button(popup, text="Press to close", command=popup.destroy)
        button.pack(fill=tk.BOTH, expand=True)
        popup.mainloop()

    def combine_images(self):
        self.impath = self.filename
        combined_path = combine_images(
            self.impath, self.directions, self.num_pixels
        )

        # display combined image
        self.display_image(combined_path)

    def load_image(self):
        self.filename = tk.filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg")]
        )
        self.impath = self.filename
        self.display_image(self.impath)

        self.title(f"Panorama dalle 2 - {self.filename}")

    def display_image(self, impath):
        # Display loaded image
        im = Image.open(impath)
        # resize image to 600xN where N is height
        # of image with respect to it's width if height is greater
        # or if width is greater than height, resize to Nx600
        # if im.height > im.width:
        #     im = im.resize((600, int(im.height * 600 / im.width)))
        # else:
        #     im = im.resize((int(im.width * 600 / im.height), 600))

        # but maximum width is 1600
        # and maximum height is 800
        if im.width > 1600:
            im = im.resize((1600, int(im.height * 1600 / im.width)))
        if im.height > 700:
            im = im.resize((int(im.width * 700 / im.height), 700))

        im = ImageTk.PhotoImage(im)
        self.image_label.configure(image=im)
        self.image_label.image = im


if __name__ == "__main__":
    root = MainWindowFull()
    root.mainloop()
