
from os import listdir, makedirs, chdir
from PIL import Image
import os.path as path
import shutil
import numpy as np
import cv2 
import dlib
from lxml import etree as ET
from imutils import face_utils

# Gets a directory path with many
# images and randomley picks one picture of each identity
def extract_pics_by_identity(source_path):
    img_by_id = dict()
    for image_path in listdir(source_path):
        id_and_name = image_path.split('d')
        if id_and_name[0] not in img_by_id:
            img_by_id[id_and_name[0]] = id_and_name[0] + 'd' + id_and_name[1]
    
    selected_img_paths = list(img_by_id.values())
    result_folder_name = source_path+'/result'
    makedirs(result_folder_name)
    for i in selected_img_paths:
        shutil.move(path.join(source_path, i), result_folder_name)
        
def convert_png_to_jpg(path, output_path):
    for image_path in listdir(path):
        im1 = Image.open(path+'\\'+image_path)
        new_file_name = image_path.split('.')
        dest_path = output_path+'\\'+new_file_name[0]+'.jpg'
        im1.save(dest_path)
    