import json
import logging
import getpass
from urllib.parse import urlparse
from logging.handlers import HTTPHandler


class SlackHandler(HTTPHandler):
    def __init__(self, url, username=None, icon_url=None, icon_emoji=None, channel=None, project_name=None):
        o = urlparse(url)
        is_secure = o.scheme == 'https'
        HTTPHandler.__init__(self, o.netloc, o.path, method="POST", secure=is_secure)
        self.username = username
        self.icon_url = icon_url
        self.icon_emoji = icon_emoji
        self.channel = channel
        self.project_name = project_name

    def mapLogRecord(self, record):
        if isinstance(self.formatter, SlackFormatter):
            payload = {
                'attachments': [
                    self.format(record),
                ],
            }
        else:
            payload = {
                'text': self.format(record),
            }

        if self.username:
            payload['username'] = self.username
        if self.icon_url:
            payload['icon_url'] = self.icon_url
        if self.icon_emoji:
            payload['icon_emoji'] = self.icon_emoji
        if self.channel:
            payload['channel'] = self.channel
        if self.project_name:
            # append the project name to pretext
            print(self.project_name)
            pretext = payload['attachments'][0]['pretext']
            payload['attachments'][0]['pretext'] = '[{}] {}'.format(
                self.project_name, pretext
            )
        
        ret = {
            'payload': json.dumps(payload),
        }
        return ret


class SlackFormatter(logging.Formatter):
    def format(self, record):
        ret = {}
        codeReference = '{}: {}, line {}'.format( record.pathname, record.funcName, record.lineno)
        if record.levelname == 'INFO':
            ret['color'] = 'good'
        elif record.levelname == 'WARNING':
            ret['color'] = 'warning'
        elif record.levelname == 'ERROR':
            ret['color'] = '#E91E63'
        elif record.levelname == 'CRITICAL':
            ret['color'] = 'danger'
        
        ret['pretext'] = '{} Notification from {}'.format(record.levelname, getpass.getuser())
        ret['ts'] = record.created
        ret['text'] = '`{}`'.format(super(CustomSlackFormatter, self).format(record))
        ret['fields'] = [
          {
            'title': 'Code Reference',
            'value': codeReference,
            'short': False
          }
        ]
        ret['mrkdwn_in'] = ['text']
        return ret


class SlackLogFilter(logging.Filter):
    """
    Logging filter to decide when logging to Slack is requested, using
    the `extra` kwargs:

        `logger.info("...", extra={'notify_slack': True})`
    """

    def filter(self, record):
        return getattr(record, 'notify_slack', False)
