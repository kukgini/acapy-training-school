import os
import logging
import requests
import json
import random
import string
from flask import Flask, json, request

logging.basicConfig(level = logging.DEBUG)

api = Flask(__name__)

acapy_admin_url=os.environ['ACAPY_ADMIN_URL']
headers = {
    'Authorization': f'Bearer {os.environ["ACAPY_WALLET_TOKEN"]}',
}
cred_def_id_1 = os.environ["CRED_DEF_ID_1"]

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

@api.route('/schemas', methods=['GET'])
def get_schemas_created():
    url = f'{acapy_admin_url}/schemas/created'
    response = requests.get(url, headers=headers)
    return json.dumps(json.loads(response.text), indent=2)

@api.route('/credential-definitions', methods=['GET'])
def get_credential_definitions_created():
    url = f'{acapy_admin_url}/credential-definitions/created'
    response = requests.get(url, headers=headers)
    return json.dumps(json.loads(response.text), indent=2)

@api.route('/credential-definitions/<id>', methods=['GET'])
def get_credential_definitions(id):
    url = f'{acapy_admin_url}/credential-definitions/{id}'
    response = requests.get(url, headers=headers)
    return json.dumps(json.loads(response.text), indent=2)

@api.route('/credential-definitions/<id>/write_record', methods=['GET'])
def get_credential_definitions_write_record(id):
    url = f'{acapy_admin_url}/credential-definitions/{id}/write_record'
    response = requests.post(url, headers=headers)
    return json.dumps(json.loads(response.text), indent=2)

@api.route('/revocation/registries', methods=['GET'])
def get_revocation_registry_created():
    url = f'{acapy_admin_url}/revocation/registries/created'
    response = requests.get(url, headers=headers)
    return json.dumps(json.loads(response.text), indent=2)

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

def create_oob_invitation(type, id):    
    data = {
        'accept': ['didcomm/aip2'],
        'alias': 'Issuer',
        # 'handshake_protocols': ['https://didcomm.org/didexchange/1.1'],
        'handshake_protocols': [],
        'protocol_version': '1.1',
        # 'use_did_method': 'did:peer:4',
        'use_public_did': False,
    }
    if id:
        url = f'{acapy_admin_url}/out-of-band/create-invitation?auto_accept=true&multi_use=false'
        data['attachments'] = [{'type': type, 'id': id}]
    else:
        url = f'{acapy_admin_url}/out-of-band/create-invitation?auto_accept=true&multi_use=true'

    logging.debug(f'oobdata={data}')
    response = requests.post(url, json=data, headers=headers)
    return json.loads(response.text)

@api.route('/issue-credential/credential-offer/transcript', methods=['GET'])
def get_oob_invitation_for_transcript_credential_offer():
    url = f'{acapy_admin_url}/issue-credential/create-offer'
    data = {
        'auto_issue': True,
        'comment': 'made by app for oob issue credential test',
        'cred_def_id': cred_def_id_1,
        'credential_preview': {
            '@type': 'issue-credential/1.0/credential-preview',
            'attributes': [
                {'name': 'name', 'value': 'Alice'},
                {'name': 'score', 'value': '87'},
                {'name': 'birthdate_dateint', 'value': '19850101'},
                {'name': 'date', 'value': '20230101'},
                {'name': 'timestamp', 'value': '120101'},
            ]
        }
    }
    response = requests.post(url, json=data, headers=headers)
    offer = json.loads(response.text)
    id = offer['credential_exchange_id']
    result = json.dumps(create_oob_invitation('credential-offer', id), indent=2)
    return result

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
        requests.delete(f'{acapy_admin_url}/credentials/{credential_id}', headers=headers)
        response.append(f'credential={credential_id}')

    json4 = json.loads(requests.get(f'{acapy_admin_url}/connections', headers=headers).text)
    for conn in json4['results']:
        connection_id = conn['connection_id']
        requests.delete(f'{acapy_admin_url}/connections/{connection_id}', headers=headers)
        response.append(f'connection_id={connection_id}')

    return json.dumps(response, indent=2)
   
if __name__ == '__main__':
    api.run(port=80, host='0.0.0.0')
