import os
import warnings

from lib.annotator import Annotator

warnings.filterwarnings("ignore")

info = (
    """
    ========= MRI ANNOTATOR v0.1 =========
    
    
    OPERATION GUIDE:
    
    USE Q/W TO NAVIGATE IMAGE SLICES
    L MOUSE TO ANNOTATE POSITIVE N LESION
    R MOUSE TO REMOVE PREVIOUS ANNOTATION
    ESC TO SAVE AND PROCEED
    
    
    ========= MRI ANNOTATOR v0.1 =========
                                       cjj
    """
)

if __name__ == "__main__":
    print(info)
    root_img = input("please enter root dir of MR images: ")
    patients = os.listdir(root_img)

    path_save = input("please enter directory to save annotations: ")

    for pat in patients:
        dir = os.path.join(root_img, pat)
        try:
            anno = Annotator(output_path=path_save, dir=dir)
            anno.show_arr()
        except:
            print(dir, "error! proceed to next...")
            continue
