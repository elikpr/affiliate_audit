FROM python:3.9-slim

WORKDIR /opt/AFFILIATED_PERSONS_CHECK
COPY . /opt/AFFILIATED_PERSONS_CHECK/

RUN mkdir -p /opt/AFFILIATED_PERSONS_CHECK/log
RUN apt-get update ##[edited]

RUN pip install --upgrade -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "web_app.main:app", "--host=0.0.0.0", "--reload"]