#!/usr/bin/python
import sys
import requests
import logging
import os

base_url = 'https://api.yaizy.io/canvas/webhook_notification'
header = {
    'Content-Type': 'application/json'
}


def notify_enrollment_updates(course_ids):
    try:
        data = { 'course_id': course_ids }
        response = requests.post(base_url, headers=header, json=data)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        logging.exception(err)
    except Exception as e:
        logging.exception(e)
        sys.exit()


# notify_enrollment_updates([114,115])