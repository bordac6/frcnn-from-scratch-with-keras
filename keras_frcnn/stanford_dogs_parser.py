import os
import cv2
import xml.etree.ElementTree as ET
from scipy.io import loadmat
import numpy as np


def get_data(data_paths):
        all_imgs = []
        classes_count = {}
        class_mapping = {}
        visualise = False

        print("data path:", data_paths)
        train_list = loadmat(os.path.join(data_paths, 'lists', 'train_list.mat'))
        # test_list = loadmat(os.path.join(data_paths, 'lists', 'test_list.mat'))

        print('Parsing annotation files')
        annot_path = os.path.join(data_paths, 'Annotation')
        imgs_path = os.path.join(data_paths, 'Images')
        
        trainval = [tr[0][0] for tr in train_list['file_list']]
        trainval_files = trainval[:int(len(trainval)*0.8)]
        test_files = trainval[int(len(trainval)*0.8):]

        annots = [os.path.join(annot_path, s[0][0]) for s in train_list['annotation_list']]
        idx = 0
        for annot in annots:
                try:
                        idx += 1

                        et = ET.parse(annot)
                        element = et.getroot()

                        element_objs = element.findall('object')
                        element_filename = element.find('filename').text
                        element_width = int(element.find('size').find('width').text)
                        element_height = int(element.find('size').find('height').text)

                        if len(element_objs) > 0:
                                path_to_filename = element_filename
                                for file_name in trainval:
                                        if element_filename in file_name:
                                                path_to_filename = file_name
                                annotation_data = {'filepath': os.path.join(imgs_path, path_to_filename), 'width': element_width,
                                                                   'height': element_height, 'bboxes': []}

                                if any( element_filename in tv for tv in trainval_files):
                                        annotation_data['imageset'] = 'trainval'
                                elif any(element_filename in tst for tst in test_files):
                                        annotation_data['imageset'] = 'test'
                                else:
                                        annotation_data['imageset'] = 'trainval'

                        for element_obj in element_objs:
                                class_name = element_obj.find('name').text
                                if class_name not in classes_count:
                                        classes_count[class_name] = 1
                                else:
                                        classes_count[class_name] += 1

                                if class_name not in class_mapping:
                                        class_mapping[class_name] = len(class_mapping)

                                obj_bbox = element_obj.find('bndbox')
                                x1 = int(round(float(obj_bbox.find('xmin').text)))
                                y1 = int(round(float(obj_bbox.find('ymin').text)))
                                x2 = int(round(float(obj_bbox.find('xmax').text)))
                                y2 = int(round(float(obj_bbox.find('ymax').text)))
                                difficulty = 1 # parse all files.
                                annotation_data['bboxes'].append(
                                        {'class': class_name, 'x1': x1, 'x2': x2, 'y1': y1, 'y2': y2, 'difficult': difficulty})
                        
                        all_imgs.append(annotation_data) 

                        # if visualise:
                        #         img = cv2.imread(annotation_data['filepath'])
                        #         for bbox in annotation_data['bboxes']:
                        #                 cv2.rectangle(img, (bbox['x1'], bbox['y1']), (bbox[
                        #                                           'x2'], bbox['y2']), (0, 0, 255))
                        #         cv2.imshow('img', img)
                        #         cv2.waitKey(0)

                except Exception as e:
                        print(e)
                        continue
                
        return all_imgs, classes_count, class_mapping
