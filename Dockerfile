# Use CUDA base image
FROM nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04

# Install python
RUN apt-get update && apt-get install -y python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /bot

# Copy project files
COPY . /bot

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install torch torchvision 
RUN pip install pillow
RUN pip install python-telegram-bot

# No output buffering
ENV PYTHONUNBUFFERED=1

# Run the bot
CMD ["python3", "bot.py"]