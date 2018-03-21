from os.path import dirname, join, splitext, isdir
from os import pardir
from collections import Counter
from cv2 import imread, GaussianBlur, imwrite
from face_recognition import face_locations
from darkflow.net.build import TFNet
import argparse
import sys
import numpy
import pytest
import yaml

# add the data directory global variable
data = join(dirname(__file__), '../blury/data/')
data_test = join(data, 'test')

from blury.lib import Blury, read_config_file

blury = Blury(model=join(data, 'cfg/yolo.cfg'),
              load=join(data, 'models/yolo.weights'),
              config=join(data, 'cfg/'),
              threshold=0.25, nb_filter=5)

def test_load_img():
    img = 'img.jpeg'
    blury.load_img(join(data_test, img))
    assert type(blury.img) == numpy.ndarray
    result = blury.load_img('toto.txt')
    assert result == False
    
def test_predict():
    predictions = blury.predict()
    prediction = predictions[0]
    assert type(predictions) == list
    assert type(prediction) == dict
    for key in ('confidence', 'label', 'bottomright', 'topleft'):
        assert key in prediction.keys()
    for coordinate in ('x', 'y'):
        assert coordinate in prediction['bottomright']
        assert coordinate in prediction['topleft']
        assert type(prediction['bottomright'][coordinate]) in (numpy.int32, int)
        assert type(prediction['topleft'][coordinate]) in (numpy.int32, int)
    assert type(prediction['confidence']) in (numpy.float32, float)
    assert type(prediction['label']) == str
    
def test_get_coordinate_from_boxes():
    prediction = blury.predict()[0]
    coordinates = blury.get_coordinate_from_boxes(prediction)
    assert type(coordinates) is tuple
    for coordinate in coordinates:
        assert type(coordinate) in (numpy.int32, int) 
    
def test_filter():
    img = 'img.jpeg'
    blury.load_img(join(data_test, img))
    prediction = blury.predict()[0]
    left, top, right, bottom = blury.get_coordinate_from_boxes(prediction)
    roi = blury.img[top:bottom, left:right]
    assert type(roi) is numpy.ndarray
    blured_roi = blury.filter(roi)
    assert type(blured_roi) is numpy.ndarray 
    assert roi.shape == blured_roi.shape

def test_read_config_file():
    result = read_config_file(3)
    assert result == (None, None)
    in_dir, out_dir = read_config_file(join(data_test, 'batch.properties'))
    assert type(in_dir) is str and type(out_dir) is str
    assert isdir(join(dirname(__file__), in_dir)) == True and \
        isdir(join(dirname(__file__), out_dir)) == True
    result = read_config_file('toto.txt')
    assert result == (None, None)