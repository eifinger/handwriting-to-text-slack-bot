FROM jjanzic/docker-python3-opencv:latest

RUN pip3 install slackclient matplotlib
ADD app.py /
ADD slackbot.py /
ADD projectOxfordHandler.py /

CMD [ "python3", "./app.py" ]