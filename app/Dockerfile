FROM python:3.11-slim

# Enable using 'print' statements for logging in cloud run
ENV PYTHONUNBUFFERED True

# Define the working directory inside the container. 
# All the paths will be relative to this directory.
ENV APP_HOME /app
WORKDIR $APP_HOME

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the content of the local app folder to the working directory
COPY . ./

# Expose the Streamlit port
EXPOSE 8080

# Specify the command to run on container start
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]