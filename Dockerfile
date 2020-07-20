FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

COPY ./app /app

ENV PYTHONPATH=/

EXPOSE 8080
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
