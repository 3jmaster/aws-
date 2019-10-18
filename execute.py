#!/bin/python

# Import the SDK
import boto3
import uuid
import assume_role
import vpc_flow_query
import time, datetime
import json

def execute(role_session, account_name, search_days_ago):
    sts_assumed_role = role_session.client('sts')
    account_number = sts_assumed_role.get_caller_identity()['Account']

    print('starting query')
    query_response = vpc_flow_query.start_query(role_session=role_session, days_ago=search_days_ago, debug=debug)
    if query_response==None:
        print('!!! No Flow Logs for '+ account_name + "!!!")
        return

    print('sleep for 5s')
    time.sleep(5)

    print('getting results')
    results = vpc_flow_query.get_query_results(role_session=role_session, query_id=query_response['queryId'], debug=debug)

    if debug:
        print(*results['results'], sep = "\n")

    unique_srcIP_set = set()
    unique_dstIP_set = set()

    for row in results['results']:
        for field in row:
            if field['field'] == 'srcAddr':
                if debug:
                    print(field['value'])
                unique_srcIP_set.add(field['value'])

            if field['field'] == 'dstAddr':
                if debug:
                    print(field['value'])
                unique_dstIP_set.add(field['value'])

    if debug:
        print(unique_srcIP_set)
        print(unique_dstIP_set)

    filename = account_name+"-"+account_number+"-inIP-" + current_time + ".txt"
    f = open(filename,"w+")
    for ip in unique_srcIP_set:
        f.write(ip)
        f.write('\n')
    f.close()
    print('Filename:')
    print(filename)

    filename = account_name+"-"+account_number+"-outIP-" + current_time + ".txt"
    f = open(filename,"w+")
    for ip in unique_dstIP_set:
        f.write(ip)
        f.write('\n')
    f.close()
    print('Filename:')
    print(filename)

# Change region accordingly but usually in Singapore
default_region  = 'ap-southeast-1'
current_time    = datetime.datetime.now().strftime("%Y-%m-%d--%H:%M")
search_days_ago = 7
debug           = 0

role_name       = 'admin-role'
account_file    = 'accounts.json'

# IAM first
iam_user_session = assume_role.get_iam_user_session(debug=debug)

with open(account_file) as json_file:
    data = json.load(json_file)
    if debug:
        print(data)
    for account_name in data:
        if debug:
            print(account_name)
            print(data[account_name])
        account_number = data[account_name]
        role_session = assume_role.get_assume_role(iam_user_session, account_number, role_name, debug=debug)
        execute(role_session, account_name, search_days_ago)
