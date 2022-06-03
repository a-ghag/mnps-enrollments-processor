from datetime import datetime
from zipfile import ZipFile
import logging

import pandas as pd
from enrollments import conclude_enrollments, get_enrollments

from upload_canvas_sis_import import upload_sis_import_file
from webhook import notify_enrollment_updates

logging.basicConfig(level=logging.INFO, force=True)
logging.info('Start!!')

# Change the folder name when you have new enrollments
# the folder should contain an enrollments.csv with first_name,last_name,email,user_id,course_id

source_folder = 'mnps_20220602/'
enrollments_csv = source_folder + 'enrollments.csv'

enrollments_df = pd.read_csv(enrollments_csv)

logins_column_names = ['user_id', 'email']
logins_df = enrollments_df[logins_column_names].copy()

enrollments_df['user_id'] = 'mnps-' + enrollments_df['user_id'].astype(str)

users_column_names = ['user_id', 'first_name', 'last_name', 'email']
users_df = enrollments_df[users_column_names].copy()
users_df['login_id'] = users_df['email']
users_df['status'] = 'active'
users_df.to_csv('users.csv', index=False)

logins_column_names = ['user_id', 'email']
logins_df['login_id'] = logins_df['email']
logins_df['existing_user_id'] = 'mnps-' + logins_df['user_id'].astype(str)
logins_df['user_id'] = 'mnps-microsoft-' + logins_df['user_id'].astype(str)
logins_df['authentication_provider_id'] = 'microsoft'
logins_df.to_csv('logins.csv', index=False)

enrollment_column_names = ['user_id', 'course_id']
enrollments_df = enrollments_df[enrollment_column_names]
enrollments_df['role'] = 'student'
enrollments_df['status'] = 'active'
enrollments_df.to_csv('enrollments.csv', index=False)

# Create a zip file the contains 'users.csv', 'logins.csv', 'enrollments.csv' to upload to Canvas
files_to_compress = ['users.csv', 'logins.csv', 'enrollments.csv']

time = datetime.today().strftime('%Y-%m-%d-%H-%M-%S')
canvas_upload_file = 'mnps_canvas_upload_' + time + '.zip'
with ZipFile(canvas_upload_file, mode='w') as zf:
    for f in files_to_compress:
        zf.write(f)

upload_sis_import_file(canvas_upload_file)

# Get current enrollments from Canvas and compare them to the enrollments that we just received. Conclude enrollments
# that no longer exists in the new enrollments file
for sis_course_id in enrollments_df['course_id'].unique():
    canvas_active_enrollments = get_enrollments(str(sis_course_id))
    if len(canvas_active_enrollments) == 0:
        continue
    canvas_active_enrollments_df = pd.json_normalize(canvas_active_enrollments)
    # only look at active students
    canvas_active_enrollments_df = canvas_active_enrollments_df[canvas_active_enrollments_df['enrollment_state'] == 'active']
    
    concluded_enrollments_df = pd.merge(canvas_active_enrollments_df, enrollments_df, how="outer", left_on="sis_user_id", right_on="user_id", 
                        indicator=True).query('_merge=="left_only"')
    concluded_enrollments_df['id'] = concluded_enrollments_df['id'].astype('int64')
    
    for enrollmentId in concluded_enrollments_df['id']:
        logging.info('Concluding enrollment ' + str(enrollmentId) + ' in course ' + str(sis_course_id))
        conclude_enrollments('sis_course_id:' + str(sis_course_id), enrollmentId)

# Notify Yaizy that enrollments have been updated
notify_enrollment_updates([114,115])

print('End!!')
