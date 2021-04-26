import os
import torch
from torch.nn.functional import softmax

import numpy as np
from PIL import Image
from torchvision import transforms

from .models import Image as im, Image_Classification

from .model import Net

def process_image(image:im) -> Image_Classification:
	# load the trained model
	filename = os.path.join(os.getcwd(), 'melanoma_app/model/InceptionV3.pt')
	Net.load_state_dict(torch.load(filename, map_location=torch.device('cpu')))
	Net.eval()

	# iterate over files
	"""directory = os.path.join(os.getcwd(), 'melanoma_app/test_images')"""
	file = os.path.join(os.getcwd(), image.directory, str(image.image))
	input_image = Image.open(file)

	# apply transforms to image
	preprocess = transforms.Compose([
		transforms.Resize(299),
		transforms.ToTensor(),
		transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
	])

	# apple transforms to undo 
	deprocess = transforms.Compose([
		transforms.Normalize(mean=[0, 0, 0], std=[4.3668, 4.4643, 4.4444]),
		transforms.Normalize(mean=[-0.485, -0.456, -0.406], std=[1, 1, 1]),
		transforms.ToPILImage()
	])

	input_tensor = preprocess(input_image)
	input_batch = input_tensor.unsqueeze(0)	# create a mini-batch as expected by the model

	# move the input and model to GPU for speed if available
	if torch.cuda.is_available():
		input_batch = input_batch.to('cuda')
		Net.to('cuda')

	with torch.no_grad():
		output = Net(input_batch)

	# softmax results from model output
	results = softmax(output[0], dim=0).cpu().numpy()

	ic: str

	if(results[0] >= 0.70):
		# Melanoma
		#print("Malignant/Melanoma")
		ic = 'melanoma'
	elif(results[1] >= 0.70):
		# Nevus
		#print("Nevus")
		ic = 'nevus'
	elif(results[2] >= 0.70):
		# Benign
		#print("Benign")
		ic = 'benign'
	else:
		# Unclear
		#print("Unclear")
		ic = 'unclear'
	return ic