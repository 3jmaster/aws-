#!/bin/python
# https://docs.aws.amazon.com/code-samples/latest/catalog/python-sts-assume_role.py.html
# python assume_role.py

# Copyright 2010-2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
# http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.

import boto3
from boto3.session import Session
import json

def get_iam_user_session(debug=0):
    # Create IAM client
    sts_default_provider_chain = boto3.client('sts')
    control_arn=sts_default_provider_chain.get_caller_identity()['Arn']
    control_account=sts_default_provider_chain.get_caller_identity()['Account']
    control_username=control_arn.split('user/',1)[1]

    print('Default Provider Identity (control plane): ' + control_arn)
    mfa_serial = 'arn:aws:iam::'+control_account+':mfa/'+control_username

    if debug:
        print(mfa_serial)

    mfa_token = input("MFA: ")

    iam_user_response = sts_default_provider_chain.get_session_token(
        DurationSeconds=43200,
        SerialNumber=mfa_serial,
        TokenCode=mfa_token
    )

    if debug:
        print(iam_user_response)

    iam_user_session = Session(aws_access_key_id=iam_user_response['Credentials']['AccessKeyId'],
                      aws_secret_access_key=iam_user_response['Credentials']['SecretAccessKey'],
                      aws_session_token=iam_user_response['Credentials']['SessionToken'])

    return iam_user_session

def get_assume_role(iam_user_session, acct_number_to_assume, role_name, debug=0):
    """aws sts assume-role --role-arn arn:aws:iam::00000000000000:role/example-role --role-session-name example-role"""

    iam_user_client = iam_user_session.client('sts')

    role_to_assume_arn = 'arn:aws:iam::'+ acct_number_to_assume +':role/' + role_name
    role_session_name  = 'AssumedFromGdsControlPlane'

    role_response=iam_user_client.assume_role(
        RoleArn=role_to_assume_arn,
        RoleSessionName=role_session_name
    )

    role_session = Session(aws_access_key_id=role_response['Credentials']['AccessKeyId'],
                      aws_secret_access_key=role_response['Credentials']['SecretAccessKey'],
                      aws_session_token=role_response['Credentials']['SessionToken'])

    if debug:
        print(role_session)

    sts_assumed_role = role_session.client('sts')

    print('AssumedRole Identity: ' + sts_assumed_role.get_caller_identity()['Arn'])
    return role_session
