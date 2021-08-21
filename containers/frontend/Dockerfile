FROM python:3.9.6-alpine3.14
WORKDIR /app

COPY . .
RUN pip3 install -r dependencies.txt
EXPOSE 8080
CMD [ "/bin/sh", "start.sh" ]
