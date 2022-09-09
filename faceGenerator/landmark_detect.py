from os import listdir, makedirs, chdir
import sys
import os.path as path
import shutil
import numpy as np
import cv2 
import dlib
from lxml import etree as ET
from imutils import face_utils

example_xml_file = r'replaceThiswithActualPath\landmarks_example.bpt.xml'
landmarks_detector_model = r'replaceThiswithActualPath\shape_predictor_68_face_landmarks.dat'

# Gets the path that contains all folders with the photos inside
# Returns a list with all photo paths 
def get_nested_photo_paths(root_path):
    if not path.isdir(root_path):
        raise Exception(f'The Path:{root_path} is not a directory')
    all_photo_dirs = [d for d in listdir(root_path) if path.isdir(path.join(root_path, d))]
    all_photo_paths = []
    for dir in all_photo_dirs:
        current_photo_dir = path.join(root_path, dir)
        current_photo_name = path.join(current_photo_dir, dir+'.jpg')
        
        chdir(current_photo_dir)
        if not path.exists(current_photo_name):
            raise Exception(f'The Photo:{current_photo_name} does not exists')
        all_photo_paths.append(current_photo_name)
        chdir(root_path)
    return all_photo_paths
        
        
# iterate all photos in original_photos_path
# for each photo, create a directory containing the photo and its landmarks file
def prepare_photofit_input(original_photos_path, output_photos_path):
    
    # check the input path is a directory
    if not path.isdir(original_photos_path):
        raise Exception(f'The Path:{original_photos_path} is not a directory')

    all_photo_names = [f for f in listdir(original_photos_path) if path.isfile(path.join(original_photos_path, f))]
    
    # check the output path is a directory or create one if it doesnt exists
    if not path.exists(output_photos_path):
        makedirs(output_photos_path)
    elif not path.isdir(output_photos_path):
            raise Exception(f'The Path:{original_photos_path} is not a directory')
    chdir(output_photos_path)

    for photo_name in all_photo_names:
        new_folder_name = photo_name.replace('.jpg','')
        if not path.exists(new_folder_name):
            makedirs(new_folder_name)
        new_photo_path = shutil.copy(path.join(original_photos_path, photo_name), path.join(output_photos_path, new_folder_name))
        
        # Change directory to the current photo's folder
        new_folder_path = path.join(output_photos_path, new_folder_name)
        chdir(new_folder_path)
        
        # find the photo landmarks and save it to an xml file
        new_photo_landmarks = get_facial_landmarks(new_photo_path)
        generate_xml_two(new_photo_landmarks, new_folder_name)
        
        # Change directory back to the output photo path
        chdir(output_photos_path)


# calculate the pupil coordinates given all the face detector coordinates 
def calculate_eye_centers(all_coordinates):
    left_eye_idx = [37,38,41,40]
    right_eye_idx = [43, 44, 47, 46]
    left_i = all_coordinates[left_eye_idx]
    right_i = all_coordinates[right_eye_idx]
    left_x = (left_i[0][0] + left_i[1][0]) // 2
    left_y = (left_i[0][1] + left_i[2][1]) // 2
    right_x = (right_i[0][0] + right_i[1][0]) // 2
    right_y = (right_i[0][1] + right_i[2][1]) // 2
    return np.array([(left_x,left_y), (right_x, right_y)])

# The function returns the required facial landmarks for FaceGen Photofit
# Using the dlib's 68 facial landmark detector
def get_facial_landmarks(image_path):
    # initialize dlib's face detector (HOG-based) and then create
    # the facial landmark predictor
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor(landmarks_detector_model)
    
    # load the input image, resize it, and convert it to grayscale
    image = cv2.imread(image_path)
    # image = imutils.resize(image, width=500) # TODO: check if a resize is nesecery
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # detect faces in the grayscale image
    rects = detector(gray, 1)
    # loop over the face detections
    for (i, rect) in enumerate(rects):
	# determine the facial landmarks for the face region, then
	# convert the facial landmark (x, y)-coordinates to a NumPy array
        shape = predictor(gray, rect)
        shape = face_utils.shape_to_np(shape)
        
        # the required landmarks indices in the shape array
        required_indices_no_eyes = [1, 4, 8, 12, 15, 31, 35, 48, 54]
        eyes_coordinates = calculate_eye_centers(shape)
        all_face_landmarks = np.concatenate((eyes_coordinates, shape[required_indices_no_eyes] ))
        return all_face_landmarks 
 
# insert facial landmarks to xml file in FaceGen photofit format
def generate_xml(landmarks, file_name):
    tree = ET.parse(example_xml_file)
    root = tree.getroot()
    coordinate_idx = 0
    for col in root.iter('column'):
        new_col_val = landmarks[coordinate_idx][0]
        col.text = str(new_col_val)
        coordinate_idx += 1
    coordinate_idx = 0
    for row in root.iter('row'):
        new_row_val = landmarks[coordinate_idx][1]
        row.text = str(new_row_val)
        coordinate_idx += 1
    tree.write(file_name+'.bpt.xml',xml_declaration=True, encoding='UTF-8')
    
def generate_xml_two(landmarks, file_name):
    tree = ET.parse(example_xml_file)
    root = tree.getroot()
    coordinate_idx = 0
    for col in root.iter('column'):
        new_col_val = landmarks[coordinate_idx][0]
        col.text = str(new_col_val)
        coordinate_idx += 1
    coordinate_idx = 0
    for row in root.iter('row'):
        new_row_val = landmarks[coordinate_idx][1]
        row.text = str(new_row_val)
        coordinate_idx += 1
    out_file = open(file_name+'.bpt.xml', 'wb')
    out_file.write(b'<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>\n')
    tree.write(out_file, encoding = 'UTF-8', xml_declaration = False)
    out_file.close()
    
if __name__ == '__main__':
    if (len(sys.argv) < 3 ):
        print ('an input and output paths are neccesery!')
        exit()
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    prepare_photofit_input(input_path, output_path)
    #get_nested_photo_paths(output_path)