# Start from official python image
FROM python:3.10
# Set workdir
WORKDIR /code
# Copy requirements
COPY ./requirements.txt /code/requirements.txt
# Install requirements
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
# Copy app code
COPY ./app /code/app
# Run server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]

