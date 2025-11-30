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


class TritonPythonModel:
    """This model loops through different dtypes to make sure that
    serialize_byte_tensor works correctly in the Python backend.
    """

    def initialize(self, args):
        from transformers import pipeline
        # initialize tokenizer
        self.model = pipeline("text-classification", model="nlptown/bert-base-multilingual-uncased-sentiment")
        logging.info("Model initialized successfully")
        
    def execute(self, requests):
        logging.info(f"Processing {len(requests)} requests")
        responses = []
        for request in requests:
            logging.info("Processing a request")
            sampInput = pb_utils.get_input_tensor_by_name(request, "text")
            inpData = sampInput.as_numpy()
            
            # Convert list item to string for model to process
            decoded_str = inpData[0].decode('utf-8')
            sentiment = self.model(decoded_str)
            
            # Extract label and score from the sentiment result
            label = sentiment[0]['label']
            score = sentiment[0]['score']
            
            # Create separate output tensors for label and score
            label_tensor = pb_utils.Tensor(
                "label", 
                np.array([label.encode('utf-8')], dtype=object)
            )
            score_tensor = pb_utils.Tensor(
                "score", 
                np.array([score], dtype=np.float32)
            )
            
            # Return both outputs
            response = pb_utils.InferenceResponse([label_tensor, score_tensor])
            responses.append(response)
        return responses