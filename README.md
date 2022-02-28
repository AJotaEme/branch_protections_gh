# Automatic Branch Protection for New Repos

This repository stores the code on how to create branch protections for new repos and it will also mention the repo creator in an issue with the Branch protections created.

There are two versions of the code

1. [Local version](./Local_version)
  - Good to test locally, and quick
2. [AWS Lambda Function](./Lambda_code/)
  - More setup, secure and automated once setup with [GitHub webhooks](https://docs.github.com/en/developers/webhooks-and-events/webhooks/webhook-events-and-payloads)

This repo will go over how to setup both of them. 

If you'd like to see the Table of Contents of this README, click on the left-hand side menu icon.

## Local Version

What you will need for to run the Local Version:
- Create a [GitHub Token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token) with repo permissions.
- Install [Python](https://www.python.org/downloads/) locally

This script version is meant to emulate a GitHub Webook and how to process a json payload. In [this](./Local_version/) repo folder you will find the python script and a json payload example.

### Setup Payload

Take a look at the [payload](./Local_version/payload.json) example. Here you will need to modify a few lines in order to work with the repositories that you have control of.

Please update: 
- Repository name: (line 6 in the file)
- The Owner of the repo: (line 9 in the file)
- The Creator of the repo: (line 111 in the file)

Once this values has been updated you can run the python script. And the script will
- Pull the branches from the account and repository you added
- Create branch protections that are instantiated in the parameter `protections_payload`
- Create an issue in the account and repository you added witht he permissions added.

### Run the Scripts
The `create_branch_protections.py` script takes a GitHub Token as paremeter in order to succesfully make the API calls.

```bash
python ./create_branch_protections.py -t <YOUR_GITHUB_TOKEN>
```

If you run the above, the script will execute and if the token has access to the account/repo, the script should add the branch protection and create an issue.

## AWS Lambda Function
