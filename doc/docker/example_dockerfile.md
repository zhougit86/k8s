```txt
FROM ubuntu:latest

RUN apt-get -y update && apt-get install -y python3-dev python3-pip libpq-dev
RUN pip3 install --upgrade pip setuptools

ADD requirement.txt requirement.txt
RUN pip install -r requirement.txt && rm -r /root/.cache

RUN apt-get autoremove -y
RUN echo "export LC_ALL="en_US.UTF-8"" >> /etc/profile

WORKDIR /opt/usms

ENV PYTHONIOENCODING UTF-8

CMD ["python3", "usms.py"]
```

