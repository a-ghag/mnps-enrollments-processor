#!/usr/bin/python
import sys
import requests
import logging
import os

base_url = os.environ.get("CANVAS_API_URL")
token = os.environ.get("TOKEN")
header = {
    'Authorization': 'Bearer ' + str(token)
}


def get_enrollments(sisCourseId):
    try:
        enrollments = []
        response = requests.get(base_url + "courses/sis_course_id:" + str(sisCourseId) + "/enrollments?type[]=StudentEnrollment", headers=header)
        response.raise_for_status()
        enrollments.extend(response.json())

        while response.links.get('next'):
            response = requests.get(response.links['next']['url'], headers=header)
            enrollments.extend(response.json())

        return enrollments
    except requests.exceptions.HTTPError as err:
        logging.exception(err)
        return enrollments
    except Exception as e:
        logging.exception(e)
        sys.exit()

def conclude_enrollments(sisCourseId, enrollmentId):
    try:
        params = {}
        params['task'] = 'conclude'
        response = requests.delete(base_url + "courses/" + str(sisCourseId) + "/enrollments/" + str(enrollmentId), headers=header)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        logging.exception(err)
    except Exception as e:
        logging.exception(e)

# test code
# import pandas as pd
# from datetime import datetime, timedelta
# canvas_active_enrollments = get_enrollments('tps-39700')
# canvas_active_enrollments_df = pd.json_normalize(canvas_active_enrollments)
# print(canvas_active_enrollments_df)
# # only look at active students
# canvas_active_enrollments_df = canvas_active_enrollments_df[canvas_active_enrollments_df['enrollment_state'] == 'active']
# # only look at students who have not been active for more than 7 days
# print(canvas_active_enrollments_df)
# canvas_active_enrollments_df['last_activity_at'] = canvas_active_enrollments_df['last_activity_at'].astype('datetime64')
# canvas_active_enrollments_df = canvas_active_enrollments_df[(canvas_active_enrollments_df['last_activity_at'] < datetime.today() - timedelta(days=7)) 
#     | (canvas_active_enrollments_df['last_activity_at'].isnull())]
# print(canvas_active_enrollments_df)