"""
This is the main window
It should be able to:
    1) Load an image
    2) Process an image (prepare_panorama)
    3) Ask user to complete the image in web browser
    4) After pressing OK, combine the images (function combine_images)
"""

import tkinter as tk
import tkinter.filedialog

from image_preparation.data import Directions
from image_preparation.panorama_dalle2 import prepare_panorama, combine_images
from PIL import Image, ImageTk


class MainWindow(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Panorama dalle 2")
        self.geometry("1900x800")
        self.resizable(False, False)
        self.filename = None
        self.impath = None
        self.directions = None
        self.chosen_directions = [
            tk.Variable(value='0'),
            tk.Variable(value='0'),
            tk.Variable(value='0'),
            tk.Variable(value='0'),
        ]
        self.num_pixels = None
        self.prepare_panorama_button = None
        self.combine_images_button = None
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
        for i, direction in enumerate(Directions):
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
        # combine images button
        self.combine_images_button = tk.Button(
            left_column,
            text="Combine images",
            command=self.combine_images,
        )
        self.combine_images_button.pack(fill=tk.X, expand=True)

    def prepare_panorama(self):
        self.directions = [
            direction if x.get()=='1' else None
            for x, direction in zip(self.chosen_directions, Directions)
        ]
        print(self.directions)
        print([x.get() for x in self.chosen_directions])
        # filter None out
        self.directions = [
            direction for direction in self.directions if direction
        ]
        print(self.directions)
        self.num_pixels = 1024 - 1024 // 3
        self.impath = self.filename
        if self.impath:
            prepare_panorama(self.impath, self.directions)

            # View OK pop-up and tell paths to the generated images
            self.view_ok_popup()

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
        combined_path = combine_images(self.impath, self.directions, self.num_pixels)

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
    root = MainWindow()
    root.mainloop()
