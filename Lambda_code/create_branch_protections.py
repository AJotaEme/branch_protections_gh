import json
import boto3
import requests
client = boto3.client('ssm')

url = 'https://api.github.com/'

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
    
#Find a better way to accomplish this.
approver_count = protections_payload["required_pull_request_reviews"]["required_approving_review_count"]
required_status_checks = protections_payload["required_status_checks"]["strict"]
enforce_admins = protections_payload["enforce_admins"]
branch_restrictions = protections_payload["restrictions"]
protections_payload = json.dumps(protections_payload)
protections_added = f"""
- Num of Required Pull Request Reviewers: {approver_count}
- Require Status Checks: {required_status_checks}
- Enforce Admins: {enforce_admins}
- Restrictions: {branch_restrictions}"""

def get_repo_branches(owner, repository, headers):
    query = url + 'repos/' + owner + '/' + repository + '/branches'
    #print(query)
    res = requests.get(query, headers = headers)
    branches = res.json()
    print("Get Branches Status Code: " + str(res.status_code))
    #print(branches)
    return branches

def protect_branches(owner, repository, branch, headers):
    query = url + 'repos/' + owner + '/' + repository + '/branches/' + branch + '/protection'
    #print(query)
    res = requests.put(query, headers = headers, data=protections_payload)
    protect_status_code = res.status_code
    print("Protect Branches Status Code: " + str(res.status_code))
    #print(protect_response)
    return protect_status_code

def create_issue(owner, repository, message, headers):
    query = url + 'repos/' + owner + '/' + repository + '/issues'
    res = requests.post(query, headers = headers, data=json.dumps({"title" : "Branch Protections" , "body" : message }))
    print(query)
    print("Create Issues Status Code: " + str(res.status_code))
    return res.status_code#print(res.json())

def create_issue_message(owner, branch_protections):
    message = "Hi :wave: @" + owner + "\n The following branch protections where added to your repo" + branch_protections
    return message
    
def lambda_handler(event, context):
    
    ssmParameter = client.get_parameter(Name='gh_pat', WithDecryption=True)
    authToken = ssmParameter['Parameter']['Value']
    
    
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": "Bearer " + authToken
    }
    
    payload = event
    # Get values for payload
    repo_payload = payload["repository"]
    owner_payload = repo_payload["owner"]
    repo_name = repo_payload["name"]
    owner_login = owner_payload["login"]
    
    repo_branches = get_repo_branches(owner_login, repo_name, headers)
    
    for branch_data in repo_branches:
        branch = branch_data['name']
        print(branch)
        if branch == 'main' :
            status_code = protect_branches(owner_login, repo_name, branch, headers)
            #print(status_code)
            if status_code == 200:
                issue_message = create_issue_message(owner_login, protections_added)
                issue_status_code = create_issue(owner_login, repo_name, issue_message, headers)
                if issue_status_code == 201:
                    print("Branch Protections and Issue Succesfully created")
                    return {
                        'statusCode': issue_status_code,
                        'body': json.dumps('Branch Protections and Issue Succesfully created')
                    }
                else:
                    print("Unable to create issue")
                    print("Error, check that you have the right access to the repo to create branch protections and issues")
                    return {
                        'statusCode': issue_status_code,
                        'body': json.dumps('Error: Unable to create issue , check that you have the right access to the repo to create branch protections and issues')
                    }
            else:
                print("Unable to create Branch Protections")
                print("Error, check that you have the right access to the repo to create branch protections and issues")
                return {
                 'statusCode': status_code,
                  'body': json.dumps("Error: Unable to create Branch Protections , check that you have the right access to the repo to create branch protections and issues")
                }