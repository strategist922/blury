#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os.path import dirname, join, splitext, exists
from os import pardir
from collections import Counter
from cv2 import imread, GaussianBlur, imwrite
from face_recognition import face_locations
from darkflow.net.build import TFNet
import sys
import io
import yaml

# Insert project path in variable project_dir 
# and src_dir in sys_path to import our module
project_dir = join(dirname(__file__), pardir)
src_dir = join(project_dir, 'src')
data_raw = join(project_dir, 'data/raw')
sys.path.append(src_dir)

class Blury:
    """This class is used to blur plate and persons/faces on an image.
    ...
    Attributes
    ----------
    img : numpy.ndarray
        image input read with opencv.
    nb_filter : int
        filter power (number of filter apply to the image).
    tfnet : darkflow.net.build.TFNet
        YOLO model using darkflow package
    """

    def __init__(self,
                 model=join(dirname(__file__), 'data/cfg/yolo.cfg'),
                 load=join(dirname(__file__), 'data/models/yolo.weights'),
                 config=join(dirname(__file__), 'data/cfg/'),
                 threshold=0.1,
                 nb_filter=3):
        """Constuctor method.
        
        Parameters
        ----------
        model : string, optional
            path to config file for YOLO
        load : string, optional
            path to yolo weights
        threshold : float, optional
            value which define how strict is you model
        nb_filter : int, optional
            filter power (number of filter apply to the image).
            
        """

        self.nb_filter = nb_filter
        self.img = None
        self.tfnet = TFNet({
            'model': model,
            'load': load,
            'threshold': threshold,
            'config': config
        })
    
    def load_img(self, img_file, config_file=None):
        """Load img with opencv.
        
        Parameters
        ----------
        img_file : string
            absolute path to image file.
            
        Returns
        -------
        bool
            True if successful, False otherwise.
            
        """
          
        try:
            # Test if file is an image
            if splitext(img_file)[-1] not in ('.jpg', '.jpeg', '.png'):
                print("this file is not an image: {}".format(img_file))
                return False
            # Read image
            self.img = imread(img_file)
            if self.img is None:
                return False
            return True
        except Exception:
            print("Fail to read image {}".format(img_file))
        else:
            return False

    def predict(self):
        """Recognize objects from multiple image given by 
        
        input_dir using darkflow 
        (python implementation of darknet, YOLO)
        
        Returns
        -------
        list
            return all predictions
            
        """

        return self.tfnet.return_predict(self.img)

    def get_coordinate_from_boxes(self, prediction):
        """take coordinates prediction from yolo and convert them.
        
        Returns
        -------
        int, int, int, int
            return 4 bounding box coordinates
            
        """

        left, top = (int(prediction['topleft']['x']),
                     int(prediction['topleft']['y']))
        right, bottom = (int(prediction['bottomright']['x']),
                         int(prediction['bottomright']['y']))

        return left, top, right, bottom

    def blur(self, predictions):
        """blur roi on the image.
        
        Parameters
        ----------
        predictions : list
            list of all predictions for the image.
            
        Returns
        -------
        None
        
        """

        for prediction in predictions:
            if prediction['label'] == 'person':
                left, top, right, bottom = self.get_coordinate_from_boxes(
                    prediction)
                self.blur_person(left, top, right, bottom)

            elif prediction['label'] in ('car', 'truck', 'bus', 'train'):
                left, top, right, bottom = self.get_coordinate_from_boxes(
                    prediction)
                self.blur_plate(left, top, right, bottom)

        return True

    def filter(self, roi):
        """apply filter on roi.
        
        Parameters
        ----------
        roi : numpy.ndarray
            part of the image to be blured
            
        Returns
        -------
        numpy.ndarray
            roi filtered
            
        """

        for e in range(self.nb_filter):
            roi = GaussianBlur(roi, (25, 25), 30)
        return roi

    def blur_person(self, left, top, right, bottom):
        """blur persons or faces on the image.
        
        Parameters
        ----------
        left : int
        top : int
        right : int
        bottom : int
        
        Returns
        -------
        None
        
        """
        # store ROI on the image
        blur_persons = self.img[top:bottom, left:right]
        # take face coordinates with face_locations module which use dlib
        face_detected = face_locations(blur_persons, model='hog')

        # if faces detected on image just blur face overwise blur 
        # all the person
        if len(face_detected):
            x, y_prime, x_prime, y = face_detected[-1]
            blur_face = blur_persons[x:x_prime, y:y_prime]

            # apply multiple Gaussian filter to the face
            blur_face = self.filter(blur_face)

            # merge the two images
            blur_persons[x:x_prime, y:y_prime] = blur_face
            
        if len(face_detected) == 0:
            # apply multiple Gaussian filter to the face
            blur_persons = self.filter(blur_persons)
            
        # merge the two images
        self.img[top:bottom, left:right] = blur_persons

        return True

    def blur_plate(self, left, top, right, bottom):
        """blur plate on the image.
        
        Parameters
        ----------
        left : int
        top : int
        right : int
        bottom : int
        
        Returns
        -------
        None
        
        """
        
        # we want just the part of the car with th license plate
        top_plate = top + int((bottom - top) * 0.30)
        bottom_plate = bottom + int((bottom - top) * 0.10)
        left_plate = left + int((right - left) * 0.10)
        right_plate = right - int((right - left) * 0.10)

        # store ROI on the image (plate license)
        plate_licence = self.img[top_plate:bottom_plate, left_plate:
                                 right_plate]
        plate_licence = self.filter(plate_licence)

        self.img[top_plate:bottom_plate, left_plate:
                 right_plate] = plate_licence

        return True

    def save(self, out_dir, img_file):
        """save the blur image in output directoy.
        
        Parameters
        ----------
        out_dir : string
            absolute path to output directory
        img_file : string
            filename of the blur image
            
        Returns
        -------
        bool
            True if successful, False otherwise.
            
        """

        # save image in output dir
        try:
            imwrite(join(out_dir, img_file), self.img)
            return True
        except Exception:
            print("fail to save image {}".format(img_file))
        else:
            return False

def read_config_file(file):
    """Function to read config argument from yaml 
    structured file.
        
        Parameters
        ----------
        file : string
            absolute path to config file
            
        Returns
        -------
        (str, str)
            tuple with absolute path to directories in and out.
            Return (None, None) if not succed
            
        """
    try:
        if type(file) is str and exists(file):
            with open(file) as ymlfile:
                config = yaml.load(ymlfile)
            return config['dirs']['nas.url.source'], config['dirs']['nas.url.cible']
        else:
            print('This file does not exist : {}'.format(file))
            return (None, None)
    except Exception:
            print("fail to load yaml file {}".format(file))
    else:
        return (None,None)