FROM python:3.9.2
WORKDIR /code
COPY requirements.txt  main.py prometheus_counters.py /code
RUN pip install -r requirements.txt
CMD ["python", "-u", "main.py"]