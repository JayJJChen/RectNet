import os
import warnings

import numpy as np
import pandas as pd
import pydicom

warnings.filterwarnings("ignore")


class MRIImage:
    info_cols = ['InstanceNumber', 'PatientID', 'PatientName', 'ImageOrientationPatient', 'ImagePositionPatient',
                 'PixelSpacing', 'SpacingBetweenSlices', 'SeriesInstanceUID', 'SliceThickness', "img_path"]

    def __init__(self, dir):
        self.dir = dir
        self.info = None
        self._arr = None

    @property
    def image_arr(self):
        if self.info is None:
            self._parse_ds()
        if self._arr is None:
            arr = []
            for ind in range(len(self.info)):
                p = self.info.loc[ind, "img_path"]
                arr.append(self._get_image_arr(p))
            self._arr = np.array(arr)
        return self._arr

    @property
    def image_arr_norm(self):
        arr = self.image_arr
        arr = np.clip(arr, 0, 1000) / 1000 * 255
        return arr.astype(np.uint8)

    @property
    def spacing_zyx(self):
        if self.info is None:
            self._parse_ds()
        spacing_z = np.unique(self.info["SpacingBetweenSlices"])
        spacing_xy = np.unique(self.info["PixelSpacing"])
        if len(spacing_z) != 1 or len(spacing_xy) != 1:
            raise ValueError(
                "Spacing info error! spacing_xy unique:{} spacing_z unique:{}".format(spacing_xy, spacing_z))
        return spacing_z[0], spacing_xy[0][1], spacing_xy[0][0]

    def _parse_ds(self):
        """find dicom images and relevant information"""
        if self.info is None:
            info = []
            img_root = self._find_img_files()
            if img_root is None:
                raise RuntimeError("Can't find enough dicom files in folder!")
            img_names = os.listdir(img_root)
            img_paths = [os.path.join(img_root, img_names[i]) for i in range(len(img_names))]
            for p in img_paths:
                img_info = self._read_image_info(p)
                if img_info is not None:
                    info.append(img_info)
            info = pd.DataFrame(info, columns=self.info_cols)
            info = info.astype("float32", errors="ignore")
            info = info.sort_values(by="InstanceNumber")
            info.index = list(range(len(info)))
            self.info = info
        return self.info

    def _find_img_files(self):
        """finds the first folder containing >10 files, assuming they are dicoms"""
        for root, folders, files in os.walk(self.dir):
            if len(files) > 10:
                return root
        return None

    def _read_image_info(self, img_path):
        try:
            with pydicom.dcmread(img_path) as ds:
                info_row = []
                for col_name in self.info_cols:
                    if col_name == "img_path":
                        info_row.append(img_path)
                    else:
                        item = ds.get(col_name)
                        if isinstance(item, pydicom.multival.MultiValue):
                            item = list(map(float, item))  # convert to list
                        info_row.append(item)
                return info_row
        except pydicom.errors.InvalidDicomError:
            return None

    @staticmethod
    def _get_image_arr(img_path):
        with pydicom.dcmread(img_path) as ds:
            return ds.pixel_array
