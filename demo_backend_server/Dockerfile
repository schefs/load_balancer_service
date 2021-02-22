FROM python:3.9.2
WORKDIR /code
COPY requirements.txt  demo_backend_server.py /code
RUN pip install -r requirements.txt
CMD ["python", "-u", "demo_backend_server.py"]