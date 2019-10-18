#!/bin/python

import boto3
import uuid
import json
import time
from datetime import datetime, date, timedelta

def start_query(role_session, query_string='stats avg(bytes), min(bytes), max(bytes) by srcAddr, dstAddr', days_ago=7, debug=0):
    """aws logs start-query --"""
    log_group_names = []

    ec2_client = role_session.client('ec2')

    # filter out success flow logs && LogDestinationType==cloud-watch-logs
    # flow_logs_response = ec2client.describe_flow_logs(Filters=[
    #         {
    #             'Name': 'deliver-log-status',
    #             'Values': ['success']
    #         },
    #     ])

    flow_logs_response = ec2_client.describe_flow_logs()

    if debug:
        print('flow_logs_response:')
        print(flow_logs_response)

    if len(flow_logs_response['FlowLogs']) == 0:
        return

    for flowLog in flow_logs_response['FlowLogs']:
        if debug:
            print(flowLog)
        if flowLog['LogDestinationType']=='cloud-watch-logs':
            log_group_names.append(flowLog['LogGroupName'])


    logs_client = role_session.client('logs')
    t = timedelta(days = days_ago, hours = 0, seconds = 0, microseconds = 0)

    end_query_time=int(time.time())
    start_query_time=int(time.time()-t.total_seconds())

    log_group_names = list(set(log_group_names)) # make unique list
    if debug:
        print(log_group_names)

    logs_response = logs_client.start_query(
        logGroupNames=log_group_names,
        startTime=start_query_time,
        endTime=end_query_time,
        queryString=query_string
    )

    print('QueryId: '+logs_response['queryId'])

    return logs_response

def get_query_results(role_session, query_id, debug=0):
    logs_client = role_session.client('logs')

    query_response = logs_client.get_query_results(
        queryId=query_id
    )

    if debug:
        print(query_response)

    return query_response
