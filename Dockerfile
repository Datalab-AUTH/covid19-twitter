FROM python:3
COPY requirements.txt run.sh update_twitter.py /app/
WORKDIR /app
RUN pip install -r requirements.txt
CMD [ "./run.sh" ]
