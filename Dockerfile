# Covid_visialization Flask application Dockerfile

FROM python:3.10

# Create working directory
WORKDIR /app

# Copy all files from current
COPY . /app

# Install all necessary libraries
RUN pip install -r /app/requirements.txt

Expose 8000

# Command to run the script
CMD ["python", "app.py"]
