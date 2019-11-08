import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pickle
from statistics import pvariance



data_path = './data/' #change this address to your local path

type_folders = {'power':'Power_Signals/', 'force':'Force_Signals/'}
signal_type = list(type_folders.keys())

feat_labels = ['welding_pressure', 'pre_height', 'post_height', 'height_change', 
               'time_f1', 'time_f2', 'time_f3', 'time_f4',
              'freq_f1', 'freq_f2', 'freq_f3', 'freq_f4']
