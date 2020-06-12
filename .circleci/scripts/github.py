#!/usr/bin/env python3

import os
import requests
import sys


WORKFLOW_ENDPOINT = 'https://circleci.com/api/v2/workflow/%s/job'
BUILD_ENDPOINT = 'https://circleci.com/api/v2/project/github/%s/%s/%s/tests'

'''
Returns value of the given environment variable
'''
def get_value_from_env(env_key):
        try:
                return os.environ[env_key]
        except KeyError:
                pass


'''
Returns a CircleCI workflow object
'''	
def get_workflow(workflow_id, headers):
	workflow_url = WORKFLOW_ENDPOINT % workflow_id
	print('Querying: ', workflow_url)

	response = requests.get(workflow_url, headers=headers)
	print('Response status code', response.status_code)

	return response.json() if response.status_code == 200 else None
	

CIRCLE_CI_BUILD_TYPE_KEY = 'build'
CIRCLE_CI_BUILD_STATUS_KEY = 'status'
CIRCLE_CI_BUILD_FAILED_KEY = 'failed'
CIRCLE_CI_JOB_NUMBER_KEY = 'job_number'
CIRCLE_CI_WORKFLOW_ITEMS_KEY = 'items'
'''
Returns a list of failed build numbers
'''
def get_failed_build_nums_from_workflow(workflow):
	if workflow is None:
		return None
	out = []
	for item in workflow.get(CIRCLE_CI_WORKFLOW_ITEMS_KEY, []):
		if CIRCLE_CI_BUILD_TYPE_KEY == item.get('type') and CIRCLE_CI_BUILD_FAILED_KEY == item.get(CIRCLE_CI_BUILD_STATUS_KEY):
			out.append(item.get(CIRCLE_CI_JOB_NUMBER_KEY))
	return out

'''
Return a CircleCI build object, given the build number
'''
def get_build(build_num, headers):
	project_username = get_value_from_env('CIRCLE_PROJECT_USERNAME')
	project_reponame = get_value_from_env('CIRCLE_PROJECT_REPONAME')

	# Remove after testing
	if project_username is None:
		project_username = 'open-telemetry'

	# Remove after testing
	if project_reponame is None:
		project_reponame = 'opentelemetry-collector'

	build_url = BUILD_ENDPOINT % (project_username, project_reponame, build_num)
	print('Querying: ', build_url)

	response = requests.get(build_url, headers=headers)
	print('Response status code', response.status_code)

	return response.json() if response.status_code == 200 else None
	

'''
Returns a list of CircleCI build objects
'''
def get_builds(build_nums, headers):
	out = []
	for build_num in build_nums:
		build = get_build(build_num, headers)
		out.append(build)
	return out


def main():
	workflow_id = get_value_from_env('CIRCLE_WORKFLOW_ID')
	circle_ci_token = get_value_from_env('CIRCLE_API_TOKEN')

	# Remove after testing
	if workflow_id is None:
		workflow_id = '4f8199ba-4547-4f04-9733-e5eec6ee4da4'
	
	# Remove after testing
	if circle_ci_token is None:
		circle_ci_token = ''

	if workflow_id is None:
		print('Failed to get CIRCLE_WORKFLOW_ID')
		sys.exit(1)
	if circle_ci_token is None:
                print('Failed to get CIRCLE_API_TOKEN')
                sys.exit(1)	

	headers = {'Circle-Token': circle_ci_token}
	
	# Get current workflow
	workflow = get_workflow(workflow_id, headers)

	print(workflow)

	failed_build_nums = get_failed_build_nums_from_workflow(workflow)
	print(failed_build_nums)

	if failed_build_nums is not None:
		failed_builds = get_builds(failed_build_nums, headers)
		for failed_build in failed_builds:
			print(failed_build)

main()

