import os

import cv2
import numpy as np
import pandas as pd

from lib.reader import MRIImage


class CoordinateStore:
    def __init__(self):
        self.points_pos = []
        # self.points_neg = []

    def select_point(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONUP:
            self.points_pos.append([x, y, param])
            self._show()

        elif event == cv2.EVENT_RBUTTONUP:
            if len(self.points_pos):
                self.points_pos.pop(-1)
            self._show()

    def _show(self):
        print(np.array(self.points_pos))
        print("=" * 15)


class Annotator(MRIImage):
    def __init__(self, output_path=None, **kwargs):
        MRIImage.__init__(self, **kwargs)
        self.output_path = output_path
        self._coords = CoordinateStore()

    def show_arr(self):
        arr = self.image_arr_norm
        name = str(self.info.loc[0, "PatientName"])
        print("start annotating", name)
        arr_length = len(arr)
        i = 0
        key = -1
        cv2.namedWindow(name)
        while key != 27:
            cv2.setMouseCallback(name, self._coords.select_point, i)
            img = arr[i]
            cv2.imshow(name, img)
            key = cv2.waitKey()
            if key == 81 and i > 0:  # q, needs CAPS for surface
                i -= 1
            if key == 87 and i < arr_length - 1:  # w, needs CAPS for surface
                i += 1
        self.save(name)

    def save(self, name):
        # save annotation csv
        if self.output_path is not None:
            csv_path = self.output_path
        else:
            csv_path = os.path.join(self.dir, "label")

        if not os.path.exists(csv_path):
            os.mkdir(csv_path)
        anno_path = os.path.join(csv_path, "{}.csv".format(name))

        # failsafe if path exists
        cnt = 0
        while os.path.exists(anno_path):
            cnt += 1
            print("{} exists, saving to new file".format(anno_path))
            anno_path = os.path.join(csv_path, "{}_{}.csv".format(name, cnt))
        label_df = pd.DataFrame(self._coords.points_pos, columns=["x", "y", "z"])
        label_df.to_csv(anno_path, index=None)
        print("annotation finished, save to", anno_path)
        cv2.destroyAllWindows()


if __name__ == "__main__":
    dir = r"D:\MRI\mr\baiyongyu0956486"
    anno = Annotator(dir=dir)
    anno.show_arr()
