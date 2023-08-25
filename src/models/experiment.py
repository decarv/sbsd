"""

# experiment = Experiment(sample_function)
# experiment.run(5, 3)
# experiment.run(8, 2)
# experiment.save('experiment.json')

# times, outputs = Experiment.parse('experiment.json')
"""

import json
import numpy as np
import pandas as pd
import os
import sys
import time
import config
from typing import Union
import sqlite3
from sentence_transformers import SentenceTransformer
import pickle
from sklearn.metrics.pairwise import cosine_similarity
import logging
from utils import log
import functools



class Experiment:
    def __init__(self, pipeline, name):
        self.pipeline = pipeline
        self.times = []
        self.outputs = []
        self.name = name

    def run(self, *args, **kwargs):
        start_time = time.time()
        output = self.pipeline()
        end_time = time.time()

        self.times.append(end_time - start_time)
        self.outputs.append(output)

    def write(self, filename):
        with open(filename, 'w') as file:
            json.dump({
                'times': self.times,
                'outputs': self.outputs
            }, file)

    @staticmethod
    def read(filename):
        with open(filename, 'r') as file:
            data = json.load(file)
            return data['times'], data['outputs']

