# import json
# import boto3

# client = boto3.client('ssm')

# def lambda_handler(event, context):
#     parameter = client.get_parameter(Name='gh_pat', WithDecryption=True)
#     print(parameter)
#     return parameter ['Parameter']['Value']

import requests
import argparse
import json

parser = argparse.ArgumentParser()

parser.add_argument("-t", "--token", help="OAuth token from GitHub", required=True)
args = parser.parse_args()

authToken = args.token


url = 'https://api.github.com/'
headers = {
    "Accept": "application/vnd.github.v3+json",
    "Authorization": "Bearer " + authToken
}

protections_payload = {
    "required_pull_request_reviews" : {
        "required_approving_review_count" : 1
    },
    "required_status_checks" : {
        "strict" : True,
        "contexts": [
         "contexts"
    ]
    },
    "enforce_admins" : None,
    "restrictions" : None
}

protections_payload = json.dumps(protections_payload)

protections_added = """
- Require Pull Reviewers
- Require Status Checks"""

def get_repo_branches(owner, repository):
    query = url + 'repos/' + owner + '/' + repository + '/branches'
    #print(query)
    res = requests.get(query, headers = {'Authorization': 'Bearer ' + authToken})
    branches = res.json()
    print("Get Branches Status Code: " + str(res.status_code))
    #print(branches)
    return branches

def protect_branches(owner, repository, branch):
    query = url + 'repos/' + owner + '/' + repository + '/branches/' + branch + '/protection'
    #print(query)
    res = requests.put(query, headers = headers, data=protections_payload)
    protect_status_code = res.status_code
    print("Protect Branches Status Code: " + str(res.status_code))
    #print(protect_response)
    return protect_status_code

def create_issue(owner, repository, message):
    query = url + 'repos/' + owner + '/' + repository + '/issues'
    res = requests.post(query, headers = headers, data=json.dumps({"title" : "Branch Protections" , "body" : message }))
    print(query)
    print("Create Issues Status Code: " + str(res.status_code))
    #print(res.json())

def create_issue_message(owner, branch_protections):
    message = "Hi :wave: @" + owner + "\n The following branch protections where added to your repo" + branch_protections
    return message


# Get payload from Json File (for test)
jFile = open('payload.json')
payload = json.load(jFile)

# Get values for payload
repo_payload = payload["repository"]
owner_payload = repo_payload["owner"]
repo_name = repo_payload["name"]
owner_login = owner_payload["login"]

repo_branches = get_repo_branches(owner_login, repo_name)

for branch_data in repo_branches:
    branch = branch_data['name']
    print(branch)
    if branch == 'main' :
        status_code = protect_branches(owner_login, repo_name, branch)
        #print(status_code)
        if status_code == 200:
            issue_message = create_issue_message(owner_login, protections_added)
            issue_status_code = create_issue(owner_login, repo_name, issue_message)
            if issue_status_code == 201:
                print("Branch Protections and Issue Succesfully created")
            else:
                print("Unable to create issue")
                print("Error, check that you have the right access to the repo to create branch protections and issues")
        else:
            print("Unable to create Branch Protections")
            print("Error, check that you have the right access to the repo to create branch protections and issues")



