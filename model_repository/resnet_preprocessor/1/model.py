import json
import logging
import numpy as np 
import subprocess
import sys
import triton_python_backend_utils as pb_utils
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
from PIL import Image

class TritonPythonModel:
    """This model preprocesses input images for ResNet50 model.
    """

    def initialize(self, args):
        from torchvision import transforms
        from PIL import Image
        # Define the preprocessing transformations
        self.transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                 std=[0.229, 0.224, 0.225]),
        ])
        logging.info("Model initialized successfully")
        
    def execute(self, requests):
        logging.info(f"Processing {len(requests)} requests")
        responses = []
        for request in requests:
            logging.info("Processing a request")
            
            # Get input tensor as numpy array
            input_tensor = pb_utils.get_input_tensor_by_name(request, "INPUT__0")
            image_array = input_tensor.as_numpy()
            
            # Handle single image only (H, W, C) - no batching at this level
            # Image can be any size - we'll resize it
            if image_array.ndim == 3:
                # Check if it's (C, H, W) format and convert to (H, W, C)
                if image_array.shape[0] == 3 or image_array.shape[0] == 1:  # Channels first
                    image_array = np.transpose(image_array, (1, 2, 0))
                
                # Create PIL Image from numpy array
                image = Image.fromarray(image_array.astype(np.uint8))
            else:
                raise ValueError(f"Invalid image shape: {image_array.shape}. Expected 3D array (H, W, C).")
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
                
            # Apply preprocessing (resize, normalize, etc.)
            preprocessed_image = self.transform(image)
            # Convert to numpy (shape: [3, 224, 224])
            preprocessed_image = preprocessed_image.numpy()
            
            # NO batch dimension added - output is [3, 224, 224]
            # Triton will batch these at the model level
            
            # Create output tensor
            output_tensor = pb_utils.Tensor("OUTPUT__0", preprocessed_image.astype(np.float32))
            response = pb_utils.InferenceResponse(output_tensors=[output_tensor])
            responses.append(response)
        return responses