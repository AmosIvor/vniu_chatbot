FROM rasa/rasa:3.6.20

WORKDIR /app

COPY . .

COPY ./data /app/data

# Create the models directory and set permissions
USER root
RUN rm -rf /app/models
RUN rm -rf /app/venv

RUN rasa train

VOLUME /app
VOLUME /app/data
VOLUME /app/models

USER 1001

CMD ["run","-m","/app/models","--enable-api","--cors","*","--debug" ,"--endpoints", "endpoints.yml", "--debug"]

