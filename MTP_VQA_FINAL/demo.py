# -*- coding: utf-8 -*-
"""demo.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1Cw1A8dzriONDlAxgjik6BsX17vy91MR2

# Importing required files
"""
import streamlit as st

import sys
import os.path
import math
import json

import torch
import torch.nn as nn
import torch.optim as optim
from torch.autograd import Variable
import torch.backends.cudnn as cudnn
from tqdm import tqdm

import config
import data
import model
import utils

import h5py
from PIL import Image
from torch.autograd import Variable
import torch.nn as nn
import torch.backends.cudnn as cudnn
import torch.utils.data
import torchvision.models as models

import config
import data
import utils
from resnet import resnet as caffe_resnet

"""# Wrote custom functions to process input to the neural network"""

def prepare_questions(questions):
    '''
    Remove punctuation marks and spaces. Returns list
    '''
    questions = [questions]
    for question in questions:
        question = question.lower()[:-1]
        yield question.split(' ')

def encode_question(question):
    '''
    Encode questions
    Get ids using vocabulary created using tokens during training
    '''
    vec = torch.zeros(len(question)).long()
    with open(config.vocabulary_path, 'r') as fd:
        vocab_json = json.load(fd)
    token_to_index = vocab_json['question']
    for i, token in enumerate(question):
        index = token_to_index.get(token, 0)
        vec[i] = index
    return vec, len(question)

class Net(nn.Module):
    '''
    Loading Resnet pretrained model to get image features
    '''
    def __init__(self):
        super(Net, self).__init__()
        self.model = models.resnet152(pretrained=True)

        def save_output(module, input, output):
            self.buffer = output
        self.model.layer4.register_forward_hook(save_output)

    def forward(self, x):
        self.model(x)
        return self.buffer


def encode_img(net,img_path):
    '''
    Encoding input image using Resnet features. Resizes input image to config.image_size
    '''
    cudnn.benchmark = True
    transform = utils.get_transform(config.image_size, config.central_fraction)
    img = Image.open(img_path).convert('RGB')
    img = transform(img)
    ix,iy = img.size()[1],img.size()[2]
    net = Net()
    net.eval()
    with torch.no_grad():
        img = Variable(img)
        out = net(img.view(1,3,ix,iy))
        features = out.data.cpu().numpy().astype('float32')
    return features

"""# Run Demo below"""

# Commented out IPython magic to ensure Python compatibility.
# %matplotlib inline
import matplotlib.pyplot as plt
import skimage
import torch
import model

def demo(img_path,question):
    '''
    Main demo function. Takes input image path and Question string as input
    Returns top 5 answers, shows input image and visualizes attention applied
    '''
    print('The Question asked was: ',question)
    cudnn.benchmark = True
    # Load pre-trained image
    # Download from https://github.com/snagiri/ECE285_Jarvis_ProjectA/releases/download/v1.0/50epoch.pth
    log = torch.load('50epoch.pth', map_location=torch.device('cpu'))

    tokens = len(log['vocab']['question']) + 1
    net = model.Net(tokens)
    net.load_state_dict(log['weights'])
    net.eval()

    questions = list(prepare_questions(question))
    questions = [encode_question(q) for q in questions]
    q,q_len = questions[0]
    q = q.unsqueeze(0)

    v = encode_img(net,img_path)
    v = torch.from_numpy(v).to(torch.float)
    q_len = torch.tensor([q_len])
    with torch.no_grad():
        v = Variable(v)
        q = Variable(q)
        q_len = Variable(q_len)

    out,att_out = net.forward(v,q,q_len)
    out = out.data.cpu()
    _, answer5 = torch.topk(out,5)
    answers = []
    with open(config.vocabulary_path, 'r') as fd:
        vocab_json = json.load(fd)
    a_to_i = vocab_json['answer']
    for answer in answer5:
        answer = (answer.view(-1))
        for a in answer.data:
            answers.append(list(a_to_i.keys())[a.data])
    print_answers(answers)
    visualize_attention(att_out,img_path)
    return answers



import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import skimage.transform
from PIL import Image, ImageDraw





import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from skimage.transform import pyramid_expand

def visualize_attention(att_out, img_path):
    '''
    Takes output of attention layer and overlays it on the input image. Then shows both.
    '''
    att_out = att_out.view(-1, 14, 14)
    num_im = att_out.size(0)
    im = Image.open(img_path)
    im = np.array(im)
    im = cv2.resize(im,(896,896))

    fig, axs = plt.subplots(1, num_im, figsize=(10, 10))

    for i in range(num_im):
        attention_map = att_out[i].cpu().detach().numpy()
        attention_map = pyramid_expand(attention_map, upscale=64)

        # Calculate bounding box coordinates from the attention map
        nonzero_indices = np.where(attention_map > 0.5)  # Assuming a threshold of 0.5 for attention
        ymin, ymax = np.min(nonzero_indices[0]), np.max(nonzero_indices[0])
        xmin, xmax = np.min(nonzero_indices[1]), np.max(nonzero_indices[1])

        # Draw bounding box on the attention image
        rect = plt.Rectangle((xmin, ymin), xmax - xmin, ymax - ymin,
                             linewidth=2, edgecolor='r', facecolor='none')
        # attention_map = im +attention_map
        # Get the height and width of the attention_map
        im = np.array(im)
        height, width = attention_map.shape[:2]

        # Resize im to match the dimensions of attention_map
        resized_image = cv2.resize(im, (width, height))
        axs[i].imshow(resized_image)
        # print(np.shape(im))
        print(np.shape(attention_map))
        # axs[i].imshow(attention_map, cmap='gray', alpha=0.65)
        axs[i].add_patch(rect)
        axs[i].set_title(f'Attention Image {i}')
        axs[i].axis('off')
        st.image(resized_image, caption=f'Attention Image {i}')

    st.pyplot(fig)
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from skimage.transform import pyramid_expand
import cv2


import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from skimage.transform import pyramid_expand
import cv2




import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from skimage.transform import pyramid_expand

ans = []
def print_answers(answers):
    '''
    Function to print top 5 answers
    '''
    
    for i,a in enumerate(answers):
        ans.append((f"The top ",i+1," answer is ",a))
    return ans

"""# __The results of demo are show below__

Here the system gets the answer right. We can see the attention output also focusing on the umbrella
"""

# demo('test_img.jpg','What color is the umbrella?')

# """Here the system gets the answer wrong. But the 2nd answer was right. Input image is taken from MS COCO v1 validation set from VQA website"""

# demo('test_img.jpg','Is the umbrella yellow?')

# """Here the system gets it right. We can see more attention applied on the shoes than above"""

# demo('test_img.jpg','What color are the shoes?')

# """This image is taken from Googling for tennis images. The system gets both questions right. It also gets questions like 'is the woman playing tennis?' and 'Is she playing badminton?' right"""

# demo('tennis.jpg','What is the color of the dress?')

# demo('tennis.jpg','What is she playing?')

# """This image is taken from googling for dogs. The answer is ambiguous since I cannot tell where the dogs are but the output options are reasonable"""

# demo('dogs.jpg','Where are the dogs?')
