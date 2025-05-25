# Use a PyTorch base image with CUDA support for GPU-accelerated ML
FROM pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY frozen_requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r frozen_requirements.txt

# Copy all the code files from your local directory into the container
COPY . .

# # Default command to execute your Python script
# # This allows passing command-line arguments when running the container.
CMD ["python", "inference_only/run_aws.py"]

# Combine remount and script execution in CMD

# pass --shm-size=8g locally for testing, mounting will work in AWS batch (allegedly)
# CMD ["/bin/sh", "-c", "if mount | grep /dev/shm | grep -q 'size='; then echo 'shm-size set externally'; else mount -o remount,size=8G /dev/shm; fi && python inference_only/run_aws.py"]
