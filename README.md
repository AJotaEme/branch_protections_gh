# Automatic Branch Protection for New Repos

This repository stores the code on how to create branch protections for new repos and it will also mention the repo creator in an issue with the Branch protections created.

There are two versions of the code

1. [Local version](#local-version)
  - Good to test locally, and quick
2. [AWS Lambda Function](#aws-lambda-function)
  - More setup, secure and automated once setup with [GitHub webhooks](https://docs.github.com/en/developers/webhooks-and-events/webhooks/webhook-events-and-payloads)

This repo will go over how to setup both of them. 

If you'd like to see the Table of Contents of this README, click on the left-hand side menu icon.

## Python Script

The Python script(both versions) Consists of leveraging the [GitHub Rest API](https://docs.github.com/en/rest).

Mainly it consists of 3 API calls
1. [Get Repository Branches](https://docs.github.com/en/rest/reference/branches) / We could also use [Get Repository Branch](https://docs.github.com/en/rest/reference/branches#get-a-branch) if we are targeting a specific branch
2. [Update a Branch Protection](https://docs.github.com/en/rest/reference/branches#update-branch-protection)
3. [Create an issue](https://docs.github.com/en/rest/reference/issues#create-an-issue)

We have three different function in the script were the API called is being formed:

- `get_repo_branches()`*
- `protect_branches()`
- `create_issue()`


>* Even though we are getting all branches, currently the script is checking for the `main` branch to protect only, to keep the demo simple.

## Local Version

What you will need for to run the Local Version:
- Create a [GitHub Token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token) with repo permissions.
- Install [Python](https://www.python.org/downloads/) locally
- [Local version](./Local_version) code

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

This setup requires a little bit more knowledge on AWS Lambda and API Gateway but it provides a full end to end automated way for a [GitHub Organization](https://docs.github.com/en/organizations/collaborating-with-groups-in-organizations/about-organizations) to automatically add branch protections once a repo gets created with a `main` branch.

What you will need for this setup:

- [GitHub Organization](https://github.com/account/organizations/new?plan=free&ref_cta=Create%2520a%2520free%2520organization&ref_loc=cards&ref_page=%2Fpricing) *You can create one for free
- An [AWS Account](https://aws.amazon.com/free/?all-free-tier.sort-by=item.additionalFields.SortRank&all-free-tier.sort-order=asc&awsf.Free%20Tier%20Types=*all&awsf.Free%20Tier%20Categories=*all) *you can get one for free
  - Knowledge on AWS Lambda and API Gateway will be a plus
  - Python knowledge will be a plus
- A [GitHub Token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token). Please copy and save this in a temporary space as we will use it again.

### Create the Lambda Function

First we'll start by creating a [Lambda Function](https://console.aws.amazon.com/lambda/home?region=us-east-1#/functions). You can learn more on how to create a Lambda Function [here](https://docs.aws.amazon.com/lambda/latest/dg/lambda-python.html)

1. In the Lambda Home page, hit `Create a function`
- Select Author from Scratch
- Name your function (e.g. NewRepoProtection)
- Select Python 3.9 for Runtime
- Architecture x86_64
- For default executtion role select `Create a new role`
- Hit Create

2. Once you are in the Function You can upload the code.
- In this repo you will find the `lambda_function.zip` where it includes the lambda code and it's dependencies.
    - `requests` is a python library that helps us make http requests. This had to be included as they don't come out of the box in AWS. You can read more [here](https://medium.com/@cziegler_99189/using-the-requests-library-in-aws-lambda-with-screenshots-fa36c4630d82)
- Upload from -> zip -> Select zip file.

3. Create an API Gateway
- We will need to create an API Gateway with Custom Headers in order to retrieve values from the GitHub Webhook. You can follow this [instructions](https://aws.amazon.com/premiumsupport/knowledge-center/custom-headers-api-gateway-lambda/) to create it.
> Please disregard the first step in the blog and jump to the **Create an API Gateway REST API** part.

- Very Important instead the `mapping templates` step, in the Integration Request page and check the `Use Lambda Proxy Integration`.
- Follow the Instruction to [Deploy API](https://docs.aws.amazon.com/apigateway/latest/developerguide/how-to-deploy-api-with-console.html#how-to-deploy-api-console)

- After Creating your Stage copy the Invoke URL, that is what we will use to call our Lambda Function.
- We will test our setup later.
- Back in Resources, select Actions and select -> Deploy API.

OPTIONAL: Create an API Key
- You can create an API Key from the API Console or you can create your own key with a password generator, this will be needed to secure the communication between our GitHub webhook and the Lambda Function

- If you are creating it in the API Gateway
- Select -> API Keys -> Actions -> Create API key -> give it a name -> auto generate
  - Copy and save this in a temporary space as we will need it in the next step.

4. Create SSM Parameters

- Let's go to the [SSM Parameter Console](https://console.aws.amazon.com/systems-manager/parameters/?region=us-east-1&tab=Table). Here we will create two Secrete Parameters.
  - One named `gh_pat` that is where you will store your GitHub Token
  - One named `webhook_secret` where we will store the API key generated.
- Hit Create Parameter -> Enter Name (either `gh_pat` or `webhook_secret` ) -> Select `SecureString`
  - Paste the GitHub Token or the API Key according to the Parameter name.

5. Modify IAM permissions

The Lambda will need certain permissions to access the secrets we just created.

- Got to [IAM Role Console](https://console.aws.amazon.com/iamv2/home#/roles)
- Select the IAM Role that is related to your Lambda (it will start with the Lambda Name)
- Select the Permissions -> Edit Policy -> JSON and you will paste the following code (only update your account number and don't forget the comman)

```json
,
        {
            "Effect": "Allow",
            "Action": [
                "ssm:GetParameter"
            ],
            "Resource": [
                "arn:aws:ssm:us-east-1:<ACCOUNT_NUMBER>:parameter/gh_pat",
                "arn:aws:ssm:us-east-1:<ACCOUNT_NUMBER>:parameter/webhook_secret"
            ]
        }
```
- Select Review and Select Next


## Create GitHub Webhook

The last part is what will trigger our Lambda Function to protect our branches everytime a new repo with a default branch gets created.

GitHub webhooks allows us to build and set up integrations between events in GitHub, like a repo creation, and a webhook listener(our labmda function).

Now, let's [create a webhook](https://docs.github.com/en/developers/webhooks-and-events/webhooks/creating-webhooks) and we will select how to Create an [Organization Webhook](https://docs.github.com/en/rest/reference/orgs#webhooks)

GitHub offers many different [events](https://docs.github.com/en/developers/webhooks-and-events/webhooks/webhook-events-and-payloads) that can trigger a webhook, for our case we will select the [repository webhook](https://docs.github.com/en/developers/webhooks-and-events/webhooks/webhook-events-and-payloads#repository)

### Create the Webhook

1. Go to your Organization settings
- On the left hand side menu you will see under Code, Planning, and automation. Select `Webhooks`
- Select Add a Webhook
  - Paste the `invoke url` from the API Gateway. It should looks something like: https://r4nd0mid.execute-api.us-east-1.amazonaws.com/yourstagename
  - Select `application/json`
  - Paste your webhook Secret (i.e. the API Key / `webhook_secret`)
  - For this demo we will disable SSL, although it is not recommended.
  - Select an individual event -> Uncheck the `pushes` and check the `Repositories` events.
- Hit Add webhook

2. Create a Repo to test the Webhook
- Create a Repo, Make sure it is public (Free Organization don't have protected branches) and select the README so that the first branch is created automatically.
- Wait for the Lambda to come back and protect your branches and create an issue.