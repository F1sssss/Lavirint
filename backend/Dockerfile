# Use the official Python image from the Docker Hub
FROM python:3.8


# Copy the requirements file to the working directory
RUN mkdir -p /home/boca/prc/certificate_store/

RUN mkdir -p /home/boca/prc/log/efi/

RUN mkdir -p /home/boca/megas/filestore

COPY certificate_store/* /home/boca/prc/certificate_store


# Set the timezone
RUN ln -sf /usr/share/zoneinfo/Europe/Podgorica /etc/localtime && echo "Europe/Podgorica" > /etc/timezone


# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the local files to the container
#COPY . .

COPY . .



#ENV VIRTUAL_ENV=/app/megas-venv
#ENV PATH="$VIRTUAL_ENV/bin:$PATH"

EXPOSE 9100


RUN pip install --no-cache-dir -r requirements.txt

# Install the dependencies
RUN apt-get update && apt-get install -y wkhtmltopdf 


# Run the application
CMD ["make", "run"]
