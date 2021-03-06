import json
import os
import time
import logging
import smtoolkit as vcsm

# Set logging 
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def lambda_handler(event, context):
    try:
        logger.debug('event.'+ os.environ['AWS_LAMBDA_FUNCTION_NAME'] + '.trigger={}'.format(json.dumps(event)))
        
        ### Message Payload
        newevent = {}
        newevent.update(event['PreviousStateOutput'])
        event.pop('PreviousStateOutput', None)
        newevent.update(event)
        event = newevent
        result = {}
        
        # Clean up Payload related to previous token
        if 'HostNotification' in event:
            event.pop('HostNotification', None)
        
        if event['Activity'] == 'HostResponse':
            time.sleep(5)
            token = vcsm.get_activitiy_token(os.environ['ActivityHostResponseArn'])
            result['HostNotification'] = {} #vcsm.send_sns(token,os.environ['SNSTopic'])
            now_response = os.environ['ResponseUrl'] + "?"+ vcsm.generate_params('now_response',token)
            soon_response = os.environ['ResponseUrl'] + "?"+ vcsm.generate_params('soon_response',token)
            result['HostNotification']['Token'] = token
            result['HostNotification']['ResponseOption'] = {}
            result['HostNotification']['ResponseOption']['now_response'] = now_response
            result['HostNotification']['ResponseOption']['soon_response'] = soon_response

            # msg = """ 
            # ===============================================
            # You have a guest !
            # Please click on one of the response link below.
            # ===============================================
            # Coming out now = {}
            # Coming out soon = {}
            # """.format(now_response,soon_response)
            
            msg = event
            
            vcsm.update_session(event['Visitor']['FaceId'],'HostNotificationToken',token,os.environ['sessiontable'])
            vcsm.send_sns(msg,os.environ['SNSTopic'])

        if event['Activity'] == 'HostArrival':
            time.sleep(5)
            token = vcsm.get_activitiy_token(os.environ['ActivityHostArrivalArn'])
            result['HostArrival'] = {} #vcsm.send_sns(token,os.environ['SNSTopic'])
            arrived = os.environ['ResponseUrl'] + "?"+ vcsm.generate_params('arrived',token)
            cancelled = os.environ['ResponseUrl'] + "?"+ vcsm.generate_params('cancelled',token)
            result['HostArrival']['Token'] = token
            result['HostArrival']['ArrivalOption'] = {}
            result['HostArrival']['ArrivalOption']['arrived'] = arrived
            result['HostArrival']['ArrivalOption']['cancelled'] = cancelled
            vcsm.update_session(event['Visitor']['FaceId'],'HostArrivalToken',token,os.environ['sessiontable'])
        
        event.pop('Activity', None)
        result.update(event)
        logger.debug('event.'+ os.environ['AWS_LAMBDA_FUNCTION_NAME'] + '.result={}'.format(json.dumps(result)))
        return result
    except Exception as e:
        print(e)
        print("Error while sending SNS")
        raise e
