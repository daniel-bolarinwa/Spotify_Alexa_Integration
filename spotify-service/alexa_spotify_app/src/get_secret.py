import boto3
from botocore.exceptions import ClientError
import json
import logging

def get_creds(secret_name):
    logging.info('setting region to eu-west-2')
    region_name = "eu-west-2"

    # Create a Secrets Manager client
    logging.debug('creating aws session')
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    logging.debug('attempting to retrieve credentials for spotify authentication from secrets manager')
    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
            # Deal with the exception here, and/or rethrow at your discretion.
            logging.exception('exception occured!')
            raise e
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            # An error occurred on the server side.
            # Deal with the exception here, and/or rethrow at your discretion.
            logging.exception('exception occured!')
            raise e
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            # You provided an invalid value for a parameter.
            # Deal with the exception here, and/or rethrow at your discretion.
            logging.exception('exception occured!')
            raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            # You provided a parameter value that is not valid for the current state of the resource.
            # Deal with the exception here, and/or rethrow at your discretion.
            logging.exception('exception occured!')
            raise e
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            # We can't find the resource that you asked for.
            # Deal with the exception here, and/or rethrow at your discretion.
            logging.exception('exception occured!')
            raise e
        elif e.response['Error']['Code'] == 'AccessDeniedException':
            # We don't have permissions to perform the get secret operation
            # Deal with exception here, and/or rethrow at your discretion
            logging.exception('exception occured!')
            raise e
    else:
        # Decrypt secret using the associated KMS key.
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
        logging.debug('attempt to retrieve spotify authentication credentials from secrets manager was successful: will proceed to decrypt the secret!')
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
            if secret_name == "client-credentials":
                logging.info('converting the retrieved secret string value to json key-value pairs in order to access individual values')        
                converted_to_json_object = json.loads(secret)
                
                client_id = converted_to_json_object['client_id']
                client_secret = converted_to_json_object['client_secret']
                logging.info('secret has been successfully decrypted and extracted')
                secret_values = [client_id, client_secret]
                return secret_values
            else:
                return secret
        else:
            logging.info('retrieved incorrect secret key type!')

def store_token(auth_token, refresh_token):
    logging.info('setting region to eu-west-2')
    region_name = "eu-west-2"

    # Create a Secrets Manager client
    logging.debug('creating aws session')
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    logging.debug('attempting to retrieve credentials for spotify authentication from secrets manager')
    try:
        client.update_secret(
            SecretId="spotify_access_token",
            SecretString=auth_token
        )

        client.update_secret(
            SecretId="spotify_access_refresh_token",
            SecretString=refresh_token
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'InternalServiceErrorException':
            # An error occurred on the server side.
            # Deal with the exception here, and/or rethrow at your discretion.
            logging.exception('exception occured!')
            raise e
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            # You provided an invalid value for a parameter.
            # Deal with the exception here, and/or rethrow at your discretion.
            logging.exception('exception occured!')
            raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            # You provided a parameter value that is not valid for the current state of the resource.
            # Deal with the exception here, and/or rethrow at your discretion.
            logging.exception('exception occured!')
            raise e
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            # We can't find the resource that you asked for.
            # Deal with the exception here, and/or rethrow at your discretion.
            logging.exception('exception occured!')
            raise e
        elif e.response['Error']['Code'] == 'AccessDeniedException':
            # We don't have permissions to perform the get secret operation
            # Deal with exception here, and/or rethrow at your discretion
            logging.exception('exception occured!')
            raise e
    else:
        logging.debug('attempt to store spotify authorisation token in secrets manager was successful!')
