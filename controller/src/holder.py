
import os
import logging
import requests
import json
import random
import string
from flask import Flask, json, request

logging.basicConfig(level = logging.DEBUG)

api = Flask(__name__)

issuer_endpoint=os.environ['ISSUER_ENDPOINT']
verifier_endpoint=os.environ['VERIFIER_ENDPOINT']

acapy_admin_url=os.environ['ACAPY_ADMIN_URL']
headers = {
    'Authorization': f'Bearer {os.environ["ACAPY_WALLET_TOKEN"]}',
}

@api.route('/webhook/topic/<topic>/', methods=['POST'])
def webhook_handler(topic):
    payload = request.get_json()
    if topic == 'connections':
        id = payload['connection_id']
        state = payload["state"]
        logging.info(f'topic={topic}, id={id}, state={state}')
    if topic == 'connection_reuse_accepted':
        logging.info(f'topic={topic}, payload={json.dumps(payload, indent=2)}')
    elif topic == 'out_of_band':
        state = payload["state"]
        logging.info(f'topic={topic}, state={state}, payload={json.dumps(payload, indent=2)}')
    elif topic == 'issue_credential':
        id = payload['credential_exchange_id']
        state = payload["state"]
        logging.info(f'topic={topic}, id={id}, state={state}')
    elif topic == 'present_proof':
        id = payload['presentation_exchange_id']
        state = payload["state"]
        logging.info(f'topic={topic}, id={id}, state={state}')
    else:
        logging.info(f'topic={topic}')
    return ('', 204)

@api.route('/connections', methods=['GET'])
def get_connections():
    url = f'{acapy_admin_url}/connections'
    response = requests.get(url, headers=headers)
    j = json.loads(response.text)

    results = []
    for conn in j["results"]:
        result = f'id={conn["connection_id"]}, state={conn["state"]}'
        results.append(result)
    
    return json.dumps(results, indent=2)

@api.route('/credentials', methods=['GET'])
def get_credentials():
    url = f'{acapy_admin_url}/credentials'
    response = requests.get(url,  headers=headers)
    j = json.loads(response.text)
    credentials = j["results"]
    credential_ids = []
    for credential in credentials:
        credential_ids.append(credential["referent"])
    return json.dumps(credentials, indent=2)

@api.route('/issue-credential/transcript', methods=['GET'])
def issue_credential_1():
    # receive_invitation(get_oob_invitation_for_connection_from_issuer())
    receive_invitation(get_oob_invitation_for_issue_credential_from_issuer())
    return ('', 204)

@api.route('/present-proof/transcript', methods=['GET'])
def present_proof_1():
    receive_invitation(get_oob_invitation_for_present_proof_from_verifier())
    return ('', 204)

@api.route('/issue-credential/records', methods=['GET'])
def get_issue_credential_records():
    url = f'{acapy_admin_url}/issue-credential/records'
    response = requests.get(url, headers=headers)
    records = json.loads(response.text)

    results = []
    for record in records["results"]:
        results.append(
            f'credential_exchange_id={record.get("credential_exchange_id")} '
            f'updated_at={record.get("updated_at")} '
            f'state={record.get("state")} '
            )

    return json.dumps(results, indent=2)

@api.route('/present-proof/records', methods=['GET'])
def get_present_proof_records():
    url = f'{acapy_admin_url}/present-proof/records'
    response = requests.get(url, headers=headers)
    present_proof_records = json.loads(response.text)

    results = []
    for record in present_proof_records["results"]:
        results.append(
            f'presentation_exchange_id={record.get("presentation_exchange_id")} '
            f'updated_at={record.get("updated_at")} '
            f'state={record.get("state")} '
            f'verified={record.get("verified")}'
            )

    return json.dumps(results, indent=2)

def get_oob_invitation_for_issue_credential_from_issuer():
    url = f'{issuer_endpoint}/issue-credential/credential-offer/transcript'
    response = requests.get(url,  headers=headers)
    oob = json.loads(response.text)
    invitation = oob['invitation']
    logging.info(f'invitation={invitation}')
    return invitation

def get_oob_invitation_for_present_proof_from_verifier():
    url = f'{verifier_endpoint}/present-proof/create-request/transcript'
    response = requests.get(url,  headers=headers)
    oob = json.loads(response.text)
    invitation = oob['invitation']
    logging.info(f'invitation={invitation}')
    return invitation

def receive_invitation(invitation):
    url = f'{acapy_admin_url}/out-of-band/receive-invitation?auto_accept=true&use_existing_connection=true'
    response = requests.post(url, json=invitation, headers=headers)
    return json.dumps(response.text, indent=2)

@api.route('/cleanup', methods=['GET'])
def all_clear():
    response = []

    json1 = json.loads(requests.get(f'{acapy_admin_url}/issue-credential/records', headers=headers).text)
    for cred_ex in json1['results']:
        cred_ex_id = cred_ex['credential_exchange_id']
        requests.delete(f'{acapy_admin_url}/issue-credential/records/{cred_ex_id}', headers=headers)
        response.append(f'cred_ex_id={cred_ex_id}')

    json2 = json.loads(requests.get(f'{acapy_admin_url}/present-proof/records', headers=headers).text)
    for pres_ex in json2['results']:
        pres_ex_id = pres_ex['presentation_exchange_id']
        requests.delete(f'{acapy_admin_url}/present-proof/records/{pres_ex_id}', headers=headers)
        response.append(f'pres_ex_id={pres_ex_id}')

    json3 = json.loads(requests.get(f'{acapy_admin_url}/credentials', headers=headers).text)
    for credential in json3['results']:
        credential_id = credential['referent']
        requests.delete(f'{acapy_admin_url}/credential/{credential_id}', headers=headers)
        response.append(f'credential={credential_id}')

    json4 = json.loads(requests.get(f'{acapy_admin_url}/connections', headers=headers).text)
    for conn in json4['results']:
        connection_id = conn['connection_id']
        requests.delete(f'{acapy_admin_url}/connections/{connection_id}', headers=headers)
        response.append(f'connection_id={connection_id}')

    return json.dumps(response, indent=2)

if __name__ == '__main__':
    api.run(port=80, host='0.0.0.0')
