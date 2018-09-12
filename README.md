handwriting-to-text-slack-bot
=================

A slack bot running in a docker container which recognizes handwritten text for you.

## Setup
1. Create a Slack Bot and get the token for it as described [here](https://api.slack.com/bot-users#creating-bot-user)
2. Create a Service Key for Azure Cognitive Services [here](https://azure.microsoft.com/en-us/services/cognitive-services/computer-vision/)
3. Start this container
```
sudo docker run \
-e SLACK_BOT_TOKEN=<YOUR_TOKEN> \
-e SLACK_BOT_NAME=<YOUR_BOT_NAME> \
-e AZURE_COGNITIVE_SERVICES_TOKEN=<YOUR_TOKEN> \
-e AZURE_COGNITIVE_SERVICES_URL=<YOUR_SERVICE_URL>
eifinger/handwriting-to-text-slack-bot:latest
```
Example:
```
sudo docker run \
-e SLACK_BOT_TOKEN=xoxb-725471920163-473829104631-2afTJdhwoSMWJSnfuwkjaf2a \
-e SLACK_BOT_NAME=handwriting-bot \
-e AZURE_COGNITIVE_SERVICES_TOKEN=31987d87237e8129f3891a98397ff997 \
-e AZURE_COGNITIVE_SERVICES_URL=https://westus.api.cognitive.microsoft.com/vision/v1.0/RecognizeText
eifinger/handwriting-to-text-slack-bot:latest
```

## Usage
1. Send a file to your bot or in a channel where you added your bot. ~~Be sure to attach a name to the file.~~ A message for the upload is no longer needed
<p align="center">
  <img width="50%" height="500%" src="images/handwriting-bot-example-upload.png">
</p>

2. The bot answers with two files. One is a text file containing the identified text entities and the other a visual representation of where he found it
<p align="center">
  <img width="50%" height="500%" src="images/handwriting-bot-example-redacted.png">
</p>

## Links
- https://docs.microsoft.com/en-us/azure/cognitive-services/Computer-vision/quickstarts/python-hand-text
- https://github.com/Microsoft/Cognitive-Vision-Python/blob/master/Jupyter%20Notebook/Handwriting%20OCR%20API%20Example.ipynb
