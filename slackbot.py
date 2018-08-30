import requests
import logging
import sys
from slackclient import SlackClient
import os
import io
import tempfile

class Slackbot():
    
    def __init__(self, SLACK_BOT_TOKEN, SLACK_BOT_NAME):
        self.token = SLACK_BOT_TOKEN
        self.slack_client = SlackClient(self.token)
        if not self.slack_client:
            sys.exit("Could not instantiate slack client. Wrong Token?")

        self.BOT_NAME = SLACK_BOT_NAME

        self.BOT_ID = self.get_user_id(self.BOT_NAME)
        logging.info("BOT_ID is {}".format(self.BOT_ID))
        self.AT_BOT = "<@" + self.BOT_ID + ">"

    def get_user_id(self, user_name):
        """
            Identify the user ID assigned to the bot so we can identify messages.
        :return: The user id of the bot example: U79Q3RS22
        """
        api_call = self.slack_client.api_call("users.list")
        if api_call.get('ok'):
            # retrieve all users so we can find our bot
            users = api_call.get('members')
            for user in users:
                if 'name' in user and user.get('name') == user_name:
                    return user.get('id')

    def get_user_name(self, user_id):
        api_call = self.slack_client.api_call("users.list")
        if api_call.get('ok'):
            # retrieve all users so we can find our bot
            users = api_call.get('members')
            for user in users:
                if 'id' in user and user.get('id') == user_id:
                    return user.get('real_name')

    def parse_slack_output(self,slack_rtm_output):
        """
            The Slack Real Time Messaging API is an events firehose.
            this parsing function returns None unless a message is
            directed at the Bot, based on its ID.
        """
        output_list = slack_rtm_output
        if output_list and len(output_list) > 0:
            for output in output_list:
                if output and 'text' in output and self.AT_BOT in output['text']:
                    # return text after the @ mention, whitespace removed
                    if "files" in output and len(output["files"]) > 0:
                        url_private_download = output["files"][0]["url_private_download"]
                        permalink = output["files"][0]["permalink"]
                    else:
                        url_private_download = None
                        permalink = None
                    return output['text'].split(self.AT_BOT)[1].strip().lower(), \
                           output['channel'], output['user'], True, url_private_download, permalink
                else:
                    if output and 'channel' in output and not isinstance(output['channel'],dict) \
                    and 'type' in output and output['type'] == 'message' \
                    and 'user' in output and output['user'] != self.BOT_ID:
                        if "files" in output and len(output["files"]) > 0:
                            url_private_download = output["files"][0]["url_private_download"]
                            permalink = output["files"][0]["permalink"]
                        else:
                            url_private_download = None
                            permalink = None
                        return output['text'], output['channel'], output['user'], False, url_private_download, permalink

        return None, None, None, None, None, None

    def send_message(self, message, channel):
        self.slack_client.api_call("chat.postMessage", channel=channel, text=message, as_user=True)

    def send_file(self, channel, file):
        with open(file, "rb") as file_content:
            self.slack_client.api_call(
                "files.upload",
                channels=channel,
                file=file_content,
                title=file
            )

    def downloadFile(self, filename, url):
        response = requests.get(url, headers={'Authorization': 'Bearer %s' % self.token})
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk: 
                    f.write(chunk)
        return f