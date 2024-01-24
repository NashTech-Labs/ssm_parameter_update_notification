import json    
import boto3   

def lambda_handler(event, context):
    client_sns = boto3.client('sns')
    client_ssm = boto3.client('ssm') 
    client_cloudtrail = boto3.client('cloudtrail')
    
    date = event['time']
    account = event['account']
    user_name = event["detail"]['userIdentity']['principalId'].split(":")[1]
    region = event['detail']['awsRegion']
    operation = event["detail"]["eventName"] 
    
    if event["detail"]["eventName"].lower() == "DeleteParameters".lower():   
        parameter_name = event["detail"]['requestParameters']['names'][0]  
        msg = "The SSM parameter : '{}' of the account {} in the region {} has undergone the operation '{}'.".format(parameter_name,account,region,"DELETE")
        msg +=  "\n"
        msg +=  "\n"
        msg += "This deletion has been done by {} on '{}'.".format(user_name,date)    
        final_msg = ""
        final_msg += "\n"   
        final_msg += msg       
        response = client_sns.publish(
        TopicArn='arn:aws:sns:ap-south-1:322971359654:AutomationStopStart',
        Message=final_msg,
        Subject='SSM Parameter Deleted')         
        
    elif event["detail"]["eventName"].lower() == 'PutParameter'.lower(): 
        
        parameter_name = event["detail"]['requestParameters']['name']       
        response1 = client_ssm.describe_parameters(
        Filters=[
            {
                'Key': 'Name',
                'Values': [parameter_name]     
            }]) 
        history = client_ssm.get_parameter(        
            Name = parameter_name     
            )          
        print(response1)    
        print(history)          
         
        current_value=history['Parameter']['Value']
        current_version = history['Parameter']['Version']        
        
        if str(current_version) == '1' :
            
            msg = "The SSM parameter : '{}' of the account {} in the region {} has undergone the operation '{}'. ".format(parameter_name,account,region,"CREATE")    
            msg +=  "\n"
            msg +=  "\n"   
            msg += "The new value is '{}' and this modification has been done by {} on '{}'.".format(current_value,user_name,date) 
            msg +=  "\n"    
            msg +=  "\n"
            final_msg = ""
            final_msg += "\n"
            final_msg += msg
            response = client_sns.publish(
            TopicArn='',
            Message=final_msg,
            Subject='SSM Parameter Created')      
        
        else :  
            previous_version = int(current_version)-2  
            api_for_previous_value = client_ssm.get_parameter_history(        
            Name = parameter_name
            )  
            
            previous_value = api_for_previous_value['Parameters'][previous_version]['Value']                
    
            
            # print(api_for_previous_value)           
            msg = "The SSM parameter : '{}' of the account {} in the region {} has undergone the operation '{}'.".format(parameter_name,account,region,"UPDATE")
            msg +=  "\n"
            msg +=  "\n"
            msg += "The previous Value is '{}' and the new updated value is '{}'.".format(previous_value,current_value)
            msg +=  "\n"
            msg += "This modification has been done by {} on '{}'.".format(user_name,date)        
            msg +=  "\n"    
            msg +=  "\n"
            final_msg = ""
            final_msg += "\n"
            final_msg += msg
            response = client_sns.publish(
            TopicArn='',
            Message=final_msg,
            Subject='SSM Parameter Updated')     
            
        
