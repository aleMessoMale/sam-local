""" Main code package """

import logging
import json
#import jenkins

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_override_jenkins_job_if_present(event):
    if "override_jenkins_job_if_present" in event:
        override_jenkins_job_if_present = bool(event['override_jenkins_job_if_present'])
    else:
        override_jenkins_job_if_present = False
    return override_jenkins_job_if_present