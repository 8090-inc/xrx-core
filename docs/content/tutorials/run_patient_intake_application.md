---
sidebar_position: 3
---

# Run the Patient Intake Application

This application provides an audio and visual experience for gathering information from a patient before they enter a doctor's office. As you talk, the screen fills in with the details you share, making reviewing your information easy in addition to verbal confirmation.

> **Note:** For additional information and details about the Patient Intake application, please refer to the Patient Intake README file in the repository.

## Check Redis Integration

_No action is needed for this section if you are using the docker-compose setup and pre-provided `.env` file._

The Shopify agent uses a Redis container (xrx-redis) to shop and manage task statuses. This allows for efficient, real-time status updates and checks across the distributed system.

If you are using the docker-compose setup, the Redis container will be automatically started and the reasoning agent will be able to use it as long as the environment variable is correctly set as shown below.

```
REDIS_HOST="xrx-redis"
```

If you are running the agent locally outside of docker compose, the reasoning agent will look for a Redis container on the default host (`localhost`) and port (`6379`). In order to start that server, you can use the following command:

```
docker run -d --name redis-server -p 6379:6379 redis
```

## Deploy the Containers

Once you have completed the above step, you can deploy the containers by running the following command:

```
docker compose up --build
```

This use case is super simple and ready to be deployed.
Enjoy experimenting!
