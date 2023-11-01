#!/bin/python

# split data in imgs folder into training and validation sets for the MAE fine-tuning

import os
import numpy as np 
import splitfolders

# save data to new folder

input_dir = 'IMGS/' # outer directory, inside IMGS is imgs with all of the images
output_dir = 'IMAGE_DIR/' # where the training and validation folders will be placed

split_ratio = (.8, .2) # 80% train, 20% validation, 0% test 

splitfolders.ratio(input_dir, output=output_dir, seed=1337, ratio=split_ratio, group_prefix=None)
    