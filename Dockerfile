# Use PyTorch + CUDA base image
FROM pytorch/pytorch:2.2.2-cuda11.8-cudnn8-runtime

# Set working directory
WORKDIR /bot

# Copy project files
COPY . /bot

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Run the bot
CMD ["python", "bot.py"]