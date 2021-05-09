"""Run this class only to check if you have all dependencies installed.
If you do not have them all installed, an error message will appear. """

# Libraries

# import matplotlib.pyplot as plt
# import pandas as pd
import torch

# Preliminaries

from torchtext.legacy.data import Field, TabularDataset, BucketIterator, Iterator


# Models

import torch.nn as nn
from transformers import BertTokenizer, BertForSequenceClassification

# Training

import torch.optim as optim

# Evaluation

# from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
# import seaborn as sns

# Files

from pathlib import Path

# server

from flask import Flask, request, jsonify, json


print("all dependencies installed")
