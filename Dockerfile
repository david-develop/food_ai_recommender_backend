FROM python:3.9

WORKDIR /food_api

COPY ./requirements.txt /food_api/requirements.txt

RUN pip install --no-cache-dir -r /food_api/requirements.txt

COPY . /food_api

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]