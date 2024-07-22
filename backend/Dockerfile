# Use the official Python image from the Docker Hub
FROM python:3.8

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the local files to the container
#COPY . .

COPY . .


# Install any needed packages specified in requirements.txt
#RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables to use the virtual environment
#ENV VIRTUAL_ENV=/app/megas-venv
#ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Make port 9100 available to the world outside this container
EXPOSE 9100


RUN pip install --no-cache-dir -r requirements.txt

# Run the application
CMD ["make", "run"]
