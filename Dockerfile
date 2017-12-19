FROM nikolaik/python-nodejs:latest
RUN pip install gunicorn
COPY . /usr/src/app
WORKDIR /usr/src/app
RUN pip install -r requirements.txt
CMD ["gunicorn", "-w", "2","-b", "0.0.0.0:5023", "--timeout", "120", "nom_track_app.app.app:app"]
