""" Main code package """

import logging
import json
#import jenkins

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_numeric_value_from_jenkins_job_or_zero_if_not_present(server, job_url, kv_to_find):
    """ Safely retrieve the number of jobs """
    logger.info("")
    if server.get_job_info(job_url)[kv_to_find] is not None:
        return int(str(server.get_job_info(job_url)[kv_to_find]['number']))
    return 0

def return_last_jenkins_job_status_or_wait_until_is_not_terminated(server, job_url, event):
    url_components = job_url.split("/")
    logger.info(url_components)
    logger.info(url_components[len(url_components)-1])

    job_name = url_components[len(url_components)-1]

    last_build_number = get_numeric_value_from_jenkins_job_or_zero_if_not_present(server, job_url, 'lastBuild')
    last_successful_build_number = get_numeric_value_from_jenkins_job_or_zero_if_not_present(server, job_url, 'lastSuccessfulBuild')
    last_unsuccessful_build_number = get_numeric_value_from_jenkins_job_or_zero_if_not_present(server, job_url, 'lastUnsuccessfulBuild')
    last_completed_build_number = get_numeric_value_from_jenkins_job_or_zero_if_not_present(server, job_url, 'lastCompletedBuild')

    logger.info("%s %s %s %s",
                last_build_number, last_successful_build_number,
                last_unsuccessful_build_number, last_completed_build_number)

    # wait until the last build is not completed
    if last_build_number == last_completed_build_number and last_build_number != 0:
        if last_build_number == last_successful_build_number:
            logger.info('Jenkins Job %s Created and Built with number %s',
                        job_name, last_build_number)
            event['status'] = 'SUCCEEDED'
            event['statusCode'] = 200
            return event
        if last_build_number == last_unsuccessful_build_number:
            logger.error(
                'Last Jenkins Job %s was not successful', job_name)
            event['status'] = 'FAILED'
            event['statusCode'] = 400
            return event
    else:
        logger.info("waiting for the last build to complete")
        event['status'] = 'WAIT'
        event['statusCode'] = 200
        return event

def create_jenkins_job(server, job_url, configxml, event, override_jenkins_job_if_present):
    """ Create Jenkins Job. If override is true, redefine according to xml passed, skip elsewhere if found """
    url_components = job_url.split("/")

    job_name = url_components[len(url_components)-1]
    job_folder_name = url_components[len(url_components)-2]

    job_folder_and_name = job_folder_name+'/'+job_name
    job_is_already_present = False

    if not server.job_exists(job_folder_and_name):
        logger.info("Creating Job {} in folder {}".format(job_name, job_folder_name))
        server.create_job(job_folder_and_name, configxml)
        logger.info("Jenkins job {} created".format(job_name))
    else:
        if override_jenkins_job_if_present:
            logger.info("Job {} already exists in folder {}. Reconfiguring it".format(job_name, job_folder_name))
            server.reconfig_job(job_folder_and_name, configxml)
            logger.info("job {} reconfigured".format(job_name))
        else:
            print(str(server.get_job_info(job_folder_and_name)))
            logger.info("Job {} already exists in folder {}. Proceeding".format(job_name, job_folder_name))
            job_is_already_present = True

    if job_is_already_present:
        event['status'] = json.dumps('Jenkins Job Already Exists! Proceeding')
    else:
        event['status'] = json.dumps('Jenkins Job Created')
    event['statusCode'] = 200
    return event