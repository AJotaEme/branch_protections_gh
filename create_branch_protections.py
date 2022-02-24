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
lowerlimit=10
upperlimit=100
# headers = {
#     "Accept" : "application/vnd.github.v3+json",
#     "Authorization" : 'Bearer' + authToken
# }

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
#print(protections_payload)

def get_repo_branches(owner, repository):
    query = url + 'repos/' + owner + '/' + repository + '/branches'
    #print(query)
    res = requests.get(query, headers = {'Authorization': 'Bearer ' + authToken})
    branches = res.json()
    #print(branches)
    return branches
    
    #     if res.status_code == 200:

def protect_branches(owner, repository, branch):
    query = url + 'repos/' + owner + '/' + repository + '/branches/' + branch + '/protection'
    print(query)
    res = requests.put(query, headers = {'Authorization': 'Bearer ' + authToken}, data=protections_payload)
    protect_status_code = res.status_code
    print(res.status_code)
    #print(protect_response)
    return protect_status_code

def create_issue(owner, repository):
    query = url + 'repos/' + owner + '/' + repository + '/issues'
    print(query)

testing = False
if testing:
    res = type('res', (object,), {})()
    print("testing is true")
    res.status_code = 200
    jFile = open('example.json')
    users = json.load(jFile)
else:
    jFile = open('payload.json')
    payload = json.load(jFile)
    repo_payload = payload["repository"]
    owner_payload = repo_payload["owner"]
    repo_name = repo_payload["name"]
    owner_login = owner_payload["login"]
    get_repo_branches(owner_login, repo_name)

    repo_branches = get_repo_branches(owner_login, repo_name)

    for branch_data in repo_branches:
        branch = branch_data['name']
        print(branch)
        if branch == 'main' :
            status_code = protect_branches(owner_login, repo_name, branch)
            print(status_code)
           
    #protect_branches(owner_login, repo_name, "main")
    #create_issue(owner_login, repo_name)
    #print(repo_name)
    # f = open("users.txt", "a")
    # count = 0
    # for i in range (lowerlimit,upperlimit+1):
    #     url = 'https://api.github.com/api/v4/users?active=true&'
    #     url = url + 'page=' + str(i)
    #     print(url)
    #     res = requests.get(url, headers = {'Authorization': 'Bearer ' + authToken})
    #     users = res.json()
    #     #print(users) 
    #     if res.status_code == 200:
    #         #print(res.json())
    #         #print(users)
    #         for user in users:
    #             print(user.get('username'))
    #             f.write(user.get('username'))
    #             f.write("\n")
    #             #print(user.get('username'))
    #             count += 1
    
    #     else:
    #         print("there was an error getting users")
    # print("users processed: ", count) 
    # f.close()


