import os
import logging
import requests
import json
import random
import time
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

def create_oob_invitation(alias, type, id):    
    url = f'{acapy_admin_url}/out-of-band/create-invitation?auto_accept=true'
    data = {
        'accept': ['didcomm/aip2'],
        'protocol_version': '1.1',
        'alias': alias,
        'handshake_protocols': []
    }
    if id:
        data['attachments'] = [{'type': type, 'id': id}]

    logging.debug(f'oobdata={data}')
    response = requests.post(url, json=data, headers=headers)
    return json.loads(response.text)

def get_nonce():
    length = 10
    characters = '123456789'
    return ''.join(random.choice(characters) for i in range(length))

@api.route('/present-proof/create-request/transcript', methods=['GET'])
def get_transcript_proof_request():
    url = f'{acapy_admin_url}/present-proof/create-request'
    data = {
        'auto_verify': True,
        'comment': 'proof request example',
        'proof_request': {
            'version': '1.0',
            'name': 'Who are you?',
            'nonce': get_nonce(),
            'requested_attributes': {
                '성적 증명서의 이름': {
                    'names': ['name'],
                    'non_revoked': { 'to': int(time.time()) },
                    'restrictions': [{'cred_def_id': cred_def_id_1}]
                },
            },
            'requested_predicates': {
                '평점 3 이상':{
                    'name': 'score',
                    'p_type': '>=',
                    'p_value': 3,
                    'non_revoked': { 'to': int(time.time()) },
                    'restrictions': [{'cred_def_id': cred_def_id_1}]
                },
            },
        },
    }
    response = requests.post(url, json=data, headers=headers)
    offer = json.loads(response.text)
    id = offer['presentation_exchange_id']
    result = json.dumps(create_oob_invitation('Verifier', 'present-proof', id), indent=2)
    return result

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
