FROM python:3

ADD hello_docker.py /

CMD [ "python", "./hello_docker.py"]
