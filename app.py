from slackbot import Slackbot
from projectOxfordHandler import ProjectOxfordHandler
import os
import sys
import logging
import time
import uuid
import shutil

__LOGGER_NAME__ = "handwriting-to-text-slack-bot"
__VERSION__ = "1.2"
__SAVE_DIR__ = "/save/"

def main():
    global logger
    logger = setup_logger()
    logger.info("Running Version: {}".format(__VERSION__))

    logger.info("Starting...")
    #Get Environment Variables
    if not os.environ.get('SLACK_BOT_TOKEN'):
        sys.exit("No environment variable \"SLACK_BOT_TOKEN\" found.")
    SLACK_BOT_TOKEN = os.environ.get('SLACK_BOT_TOKEN')

    if not os.environ.get('SLACK_BOT_NAME'):
        sys.exit("No environment variable \"SLACK_BOT_NAME\" found.")
    SLACK_BOT_NAME = os.environ.get('SLACK_BOT_NAME')

    if not os.environ.get('AZURE_COGNITIVE_SERVICES_TOKEN'):
        sys.exit("No environment variable \"AZURE_COGNITIVE_SERVICES_TOKEN\" found.")
    AZURE_COGNITIVE_SERVICES_TOKEN = os.environ.get('AZURE_COGNITIVE_SERVICES_TOKEN')

    if not os.environ.get('AZURE_COGNITIVE_SERVICES_URL'):
        sys.exit("No environment variable \"AZURE_COGNITIVE_SERVICES_URL\" found.")
    AZURE_COGNITIVE_SERVICES_URL = os.environ.get('AZURE_COGNITIVE_SERVICES_URL')

    if not os.environ.get('SAVE_TO_DISK'):
        SAVE_TO_DISK = False
    else:
        SAVE_TO_DISK = os.environ.get('SAVE_TO_DISK')
    
    bot = Slackbot(SLACK_BOT_TOKEN, SLACK_BOT_NAME)

    projectOxfordHandler = ProjectOxfordHandler(AZURE_COGNITIVE_SERVICES_TOKEN, AZURE_COGNITIVE_SERVICES_URL)

    READ_WEBSOCKET_DELAY = 0.1  # 1 second delay between reading from firehose
    if bot.slack_client.rtm_connect():
        logger.info("StarterBot connected and running!")
        while True:
            command, channel, user, is_AT_bot, url_private_download, permalink, filename = bot.parse_slack_output(bot.slack_client.rtm_read())
            if channel and user:
                if url_private_download and permalink and filename:
                    try:
                        #A file was uploaded
                        logger.info("A file was posted")
                        logger.info("Generating filename: {}".format(filename))
                        logger.info("Downloading from {} into local file {}".format(url_private_download, filename))
                        bot.downloadFile(filename, url_private_download)
                        logger.info("Getting Annotations from Microsoft Cognitive Services")
                        result = projectOxfordHandler.getResultForImage(filename)
                        text_filename = projectOxfordHandler.getTextFileFromResult(result, filename)
                        annotated_image_filename = projectOxfordHandler.showResultOnImage(result, filename)
                        logger.info("Sending back Annotated image")
                        bot.send_file(channel, annotated_image_filename)
                        logger.info("Sending back Text File")
                        bot.send_file(channel, text_filename)
                        if SAVE_TO_DISK:
                            logger.info("Moving files to storage")
                            shutil.move(filename, __SAVE_DIR__ + filename)
                            shutil.move(annotated_image_filename, __SAVE_DIR__ + annotated_image_filename)
                            shutil.move(text_filename, __SAVE_DIR__ + text_filename)
                        else:
                            logger.info("Deleting temp files {} and {} and {}".format(filename, annotated_image_filename, text_filename))
                            os.remove(filename)
                            os.remove(annotated_image_filename)
                            os.remove(text_filename)
                    except Exception:
                        logging.exception("Something went wrong")
                        bot.send_message(channel, "Something went wrong")
            time.sleep(READ_WEBSOCKET_DELAY)

def setup_logger():
    logger = logging.getLogger(__LOGGER_NAME__)
    logger.setLevel(logging.DEBUG)
    # create console handler with a log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(ch)
    return logger

if __name__ == "__main__":
    main()