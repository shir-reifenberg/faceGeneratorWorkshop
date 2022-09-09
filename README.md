# faceGeneratorWorkshop

### TL;DR

This repo contains the relevant code nesseccery for generating multiple face images based on an existing identity using [FaceGen software](https://facegen.com/sdk.htm).
To be able to run the code, FaceGen3 sdk is required.
The code uses the photofit module of FaceGen3 sdk in order to generate the images.

---

#### Preprocessing

The photofit module, which is used to create mutiple images, requires one source photo (jpg format), together with a .bpt file containing specific facial landmarks which are used by FaceGen.
In order to programmatically calculate the facial landmark of a given photo, we used [dlib's 68 facial landmark detector](http://dlib.net/face_landmark_detection.py.html), which is also included in [this repo](https://github.com/shir-reifenberg/faceGeneratorWorkshop/blob/main/data/shape_predictor_68_face_landmarks.dat).
The script [`landmark_detect.py`](https://github.com/shir-reifenberg/faceGeneratorWorkshop/blob/main/faceGenerator/landmark_detect.py) uses the landmark detector to generate the .bpt file which includes the relevant coordinates used by photofit for a given facial image.

---

#### Generating Images

After the preprocessing phase, it's possible to create multiple images out of the source image using [`face_generator.py`](https://github.com/shir-reifenberg/faceGeneratorWorkshop/blob/main/faceGenerator/face_generator.py).
The input for the script should be a directory which contains one directory for each identity, with the source image and the bpt file with the corresponding facial landmarks coordinates.
Please note that you will need to update the path of the desired source an output directory.
You can also configure the number of images that will be created per identity, by editing the variable `num_images_per_id`.

---

#### Prepare data for DCNN (Deep convolutional neural networks)

The main goal of this project was to create a dataset of computer-generated images in order to test if DCNN (that was trained using the generated images) can succeed in real human face recognition tasks.
One the computer-generated images were created, we used the code in `utils` to split the data into train-set and test-set.


---
