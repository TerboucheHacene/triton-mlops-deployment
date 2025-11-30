import json
import logging
import numpy as np 
import os
import triton_python_backend_utils as pb_utils

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TritonPythonModel:

    def initialize(self, args):
        # Load ImageNet labels from local file
        model_config = json.loads(args['model_config'])
        
        # Get the model directory path
        model_dir = os.path.dirname(os.path.realpath(__file__))
        label_file = os.path.join(model_dir, 'imagenet_labels.json')
        
        logger.info(f"Loading ImageNet labels from: {label_file}")
        
        with open(label_file, 'r') as f:
            self.imagenet_labels = json.load(f)
        
        logger.info(f"ResNet postprocessor initialized with {len(self.imagenet_labels)} labels")
        

    def execute(self, requests):
        logger.info(f"Processing {len(requests)} requests")
        responses = []
        for request in requests:
            
            output_tensor = pb_utils.get_input_tensor_by_name(request, "INPUT__0")
            output_data = output_tensor.as_numpy()
            
            # Handle single output (no batching at this level)
            # Input shape: [1000] - single prediction scores
            if output_data.ndim == 1:
                # Get top prediction (argmax)
                predicted_idx = int(np.argmax(output_data))
                
                # Convert index to label with bounds checking
                if 0 <= predicted_idx < len(self.imagenet_labels):
                    predicted_label = self.imagenet_labels[predicted_idx]
                else:
                    logger.warning(f"Invalid prediction index: {predicted_idx}, using 'unknown'")
                    predicted_label = "unknown"
                
                logger.info(f"Predicted label: {predicted_label}")
                
                # Create output tensor - single label
                label_tensor = pb_utils.Tensor(
                    "LABELS", 
                    np.array([predicted_label], dtype=object)
                )
            else:
                raise ValueError(f"Invalid output shape: {output_data.shape}. Expected 1D array [1000].")
            
            response = pb_utils.InferenceResponse(output_tensors=[label_tensor])
            responses.append(response)
        return responses
