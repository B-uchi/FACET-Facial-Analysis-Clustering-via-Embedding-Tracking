FROM python:3.10-slim

WORKDIR /app

# OS deps
RUN apt-get update && \
    apt-get install -y ffmpeg libgl1 libglib2.0-0 build-essential git cmake && \
    rm -rf /var/lib/apt/lists/*

# Install PyTorch first (required by bytetrack)
RUN pip install --no-cache-dir \
    torch==2.2.1+cpu \
    torchvision==0.17.1+cpu \
    torchaudio==2.2.1+cpu \
    -f https://download.pytorch.org/whl/cpu/torch_stable.html

# Install numpy 1.x before other packages
RUN pip install --no-cache-dir "numpy==1.23.5"

# Install remaining requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install YOLOX from git
RUN git clone https://github.com/Megvii-BaseDetection/YOLOX.git /tmp/YOLOX && \
    cd /tmp/YOLOX && pip install -e .

# # Install ByteTrack properly
# RUN git clone https://github.com/ifzhang/ByteTrack.git /tmp/ByteTrack && \
#     cd /tmp/ByteTrack && \
#     sed -i 's/numpy==1.23.5/numpy<2.0.0/g' requirements.txt && \
#     pip install -r requirements.txt && \
#     python3 setup.py develop
# Install ByteTrack properly by stripping strict ONNX requirements
RUN git clone https://github.com/ifzhang/ByteTrack.git /tmp/ByteTrack && \
    cd /tmp/ByteTrack && \
    # Remove the specific version constraints for numpy, onnx, and onnxruntime
    sed -i 's/numpy==1.23.5/numpy<2.0.0/g' requirements.txt && \
    sed -i 's/onnx==1.8.1//g' requirements.txt && \
    sed -i 's/onnxruntime==1.8.0//g' requirements.txt && \
    pip install --no-cache-dir -r requirements.txt && \
    python3 setup.py develop
    
WORKDIR /app
COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]