# Use an official Python runtime as a parent image
FROM python:3.10-bullseye

# Set the working directory in the container
WORKDIR /app

# Define a build argument for the embedding model
ARG EMBEDDING_MODEL="BAAI/bge-small-en-v1.5"

# Copy the requirements file into the container
COPY ./requirements.txt /tmp/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copy the entire project into the container
COPY . .

# Copy the entrypoint script and make it executable
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Expose the port your application runs on
EXPOSE 8000

# Define environment variables for Qdrant connection
ENV QDRANT_HOST=localhost
ENV QDRANT_PORT=6333

# Pre-download the embedding model used by Qdrant/FastEmbed
# This ensures the model is available within the Docker image and speeds up container startup.
RUN python -c "from fastembed import TextEmbedding; TextEmbedding(model_name='$EMBEDDING_MODEL')"

# Set the entrypoint for the container
ENTRYPOINT ["docker-entrypoint.sh"]

# Run the application
CMD ["python", "main.py"]