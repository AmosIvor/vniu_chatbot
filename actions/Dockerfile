FROM rasa/rasa-sdk:3.6.2

WORKDIR /app

COPY . .

USER root

EXPOSE 5055

USER root

# Set the entrypoint
ENTRYPOINT ["python", "-m", "rasa_sdk.endpoint"]