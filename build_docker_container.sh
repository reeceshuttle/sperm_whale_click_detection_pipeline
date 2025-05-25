docker build -t myimage:aws . # it is setup with my current code so that this will work.
# optional, to test:
docker run \
  --env-file .env \ # this contains AWS credentials, only for local testing
  -e INPUT_S3_BUCKET=reeceshuttle-bucket \
  -e INPUT_S3_KEY=sw061b001.wav \
  --gpus device=7 \ # only for local testing
  --shm-size=8g \ # only for local testing
  myimage:aws