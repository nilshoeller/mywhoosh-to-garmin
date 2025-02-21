# MyWhoosh to Garmin

This program fetches your latest activity from your MyWhoosh account and uploads it to your Garmin Connect profile. It automates the process of transferring data from MyWhoosh to Garmin in just a few simple steps.

## Prerequisites

- Docker (to run the project in a container)
- A MyWhoosh account
- A Garmin Connect account

## Setup

Before running the program, create a `.env` file in the root directory of your project. This file will store your credentials for both MyWhoosh and Garmin Connect. It should contain the following variables:

```.env
MYWHOOSH_EMAIL=email@example.com
MYWHOOSH_PASSWORD=your_mywhoosh_password
GARMIN_USERNAME=email@example.com
GARMIN_PASSWORD=your_garmin_password
```

Replace the placeholders with your actual login details for both services.

## Building the Project

To build the Docker image for this project, use the following command:

```bash
docker build -t mywhoosh-to-garmin .
```

This will create an image tagged mywhoosh-to-garmin that you can run in a Docker container.

## Running the Docker Image

Once the image is built, you can run it with the following command:

```bash
docker run --env-file .env mywhoosh-to-garmin
```

This will fetch your latest activity from MyWhoosh and upload it to your Garmin Connect account. Make sure your .env file is in the same directory where you run the command.

## Notes

- Make sure you have a stable internet connection during the operation.
- This script is designed for simplicity and does not include additional error handling or retries. If you encounter any issues, check your credentials and internet connection.
