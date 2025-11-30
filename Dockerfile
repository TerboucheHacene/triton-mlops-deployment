FROM nvcr.io/nvidia/tritonserver:23.08-py3

# install what your python model needs
RUN pip install torch==2.3.1 torchvision --index-url https://download.pytorch.org/whl/cu121

RUN pip install --no-cache-dir transformers 
