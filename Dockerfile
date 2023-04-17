FROM python:3.11

# set working directory
WORKDIR /app

# copy src files
COPY antro.py .
COPY requirements.txt .


# install dependencies
RUN pip install -r requirements.txt

# run the app
CMD ["python", "antro.py"]
