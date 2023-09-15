import os
import logging
import requests
import json
import random
import string
import dotenv

logging.basicConfig(level = logging.DEBUG)

acapy_admin_url="http://localhost:8001"

def create_multitenancy_holder():
    url = f'{acapy_admin_url}/multitenancy/wallet'
    data = {
        "image_url": "https://robohash.org/holder",
        "label": "Holder",
        "wallet_name": "Holder",
        "wallet_webhook_urls": [ "http://holder-controller/webhook" ],
        
        "wallet_dispatch_type": "default",
        "wallet_key_derivation": "RAW",
        "wallet_type": "askar",
        "key_management_mode": "managed"
    }
    response = requests.post(url, json=data)
    tenant_info = json.loads(response.text)
    return tenant_info["token"]

def create_multitenancy_verifier():
    url = f'{acapy_admin_url}/multitenancy/wallet'
    data = {
        "image_url": "https://robohash.org/verifier",
        "label": "Varifier",
        "wallet_name": "Verifier",
        "wallet_webhook_urls": [ "http://verifier-controller/webhook" ],
        
        "wallet_dispatch_type": "default",
        "wallet_key_derivation": "RAW",
        "wallet_type": "askar",
        "key_management_mode": "managed"
    }
    response = requests.post(url, json=data)
    tenant_info = json.loads(response.text)
    return tenant_info["token"]

def create_multitenancy_issuer():
    url = f'{acapy_admin_url}/multitenancy/wallet'
    data = {
        "image_url": "https://robohash.org/issuer",
        "label": "Issuer",
        "wallet_name": "Issuer",
        "wallet_webhook_urls": [ "http://issuer-controller/webhook" ],
        
        "wallet_dispatch_type": "default",
        "wallet_key_derivation": "RAW",
        "wallet_type": "askar",
        "key_management_mode": "managed"
    }
    response = requests.post(url, json=data)
    tenant_info = json.loads(response.text)
    return tenant_info["token"]

def create_issuer_did(issuer_token, issuer_public_did_seed):
    url = f"{acapy_admin_url}/wallet/did/create"
    headers = {
        'Authorization': f'Bearer {issuer_token}',
    }
    data = {
        'seed': f"{issuer_public_did_seed}",
    }
    response = requests.post(url, json=data, headers=headers)
    j = json.loads(response.text)
    return j['result']['did']

def assign_issuer_did_public(issuer_token, did):
    url = f"{acapy_admin_url}/wallet/did/public?did={did}"
    headers = {
        'Authorization': f'Bearer {issuer_token}',
    }
    response = requests.post(url, headers=headers)
    j = json.loads(response.text)
    return j

def create_schema_1(issuer_token, schema_version):
    url = f'{acapy_admin_url}/schemas'
    headers = {
        'Authorization': f'Bearer {issuer_token}',
    }
    data = {
        'schema_name': 'transcript',
        'schema_version': schema_version,
        'attributes': [
            'name',
            'score',
            'date',
            'birthdate_dateint',
            'timestamp',
        ]
    }
    response = requests.post(url, json=data, headers=headers)
    schema = json.loads(response.text)
    return schema["sent"]["schema_id"]

def create_credential_definition_non_revoc(issuer_token, schema_id):
    url = f'{acapy_admin_url}/credential-definitions'
    headers = {
        'Authorization': f'Bearer {issuer_token}',
    }
    data = {
        'schema_id': schema_id,
        'support_revocation': False,
        'tag': 'non-revoc',
    }
    response = requests.post(url, json=data, headers=headers)
    j = json.loads(response.text)
    return j["sent"]["credential_definition_id"]

def create_credential_definition_1_revocable_1k(issuer_token, schema_id):
    url = f'{acapy_admin_url}/credential-definitions'
    headers = {
        'Authorization': f'Bearer {issuer_token}',
    }
    data = {
        'schema_id': schema_id,
        'support_revocation': True,
        'revocation_registry_size': 1000,
        'tag': 'revocable1k',
    }
    response = requests.post(url, json=data, headers=headers)
    j = json.loads(response.text)
    return j["sent"]["credential_definition_id"]

if __name__ == '__main__':
    dotenv_file = dotenv.find_dotenv()
    dotenv.load_dotenv(dotenv_file)

    # SETUP tenants
    os.environ["HOLDER_WALLET_TOKEN"] = create_multitenancy_holder()
    os.environ["VERIFIER_WALLET_TOKEN"] = create_multitenancy_verifier()
    os.environ["ISSUER_WALLET_TOKEN"] = create_multitenancy_issuer()

    dotenv.set_key(dotenv_file, "HOLDER_WALLET_TOKEN", os.environ["HOLDER_WALLET_TOKEN"])
    dotenv.set_key(dotenv_file, "VERIFIER_WALLET_TOKEN", os.environ["VERIFIER_WALLET_TOKEN"])
    dotenv.set_key(dotenv_file, "ISSUER_WALLET_TOKEN", os.environ["ISSUER_WALLET_TOKEN"])

    issuer_token = os.environ["ISSUER_WALLET_TOKEN"]
    issuer_public_did_seed=os.environ['ISSUER_PUBLIC_DID_SEED']
    schema_version = os.environ["SCHEMA_VERSION"]
    
    # SETUP issuer step 1, create new DID 
    issuer_did = create_issuer_did(issuer_token, issuer_public_did_seed)
    os.environ["ISSUER_PUBLIC_DID"] = issuer_did
    dotenv.set_key(dotenv_file, "ISSUER_PUBLIC_DID", os.environ["ISSUER_PUBLIC_DID"])

    # SETUP issuer step 2, MANUAL STEP
    # register new DID into indy ledger with endorser role using indy-cli.
    # only steward can register a DID as endorser role.
    # only trustee can register a DID as steward role.

    # SETUP issuer step 3, set created new DID as a public DID
    issuer_did = os.environ["ISSUER_PUBLIC_DID"]
    assign_issuer_did_public(issuer_token, issuer_did)

    # SETUP issuer step 4, create schema.
    schema_id_1 = create_schema_1(issuer_token, schema_version)
    os.environ["SCHEMA_ID_1"] = schema_id_1
    dotenv.set_key(dotenv_file, "SCHEMA_ID_1", os.environ["SCHEMA_ID_1"])

    # SETUP issuer step 5, create credential definition. (non revoc)
    schema_id_1 = os.environ["SCHEMA_ID_1"]
    cred_def_1_non_revoc = create_credential_definition_non_revoc(issuer_token, schema_id_1)
    os.environ["CRED_DEF_ID_1_NON_REVOC"] = cred_def_1_non_revoc
    dotenv.set_key(dotenv_file, "CRED_DEF_ID_1_NON_REVOC", os.environ["CRED_DEF_ID_1_NON_REVOC"])

    # SETUP issuer step 5, create credential definition. (revocable)
    cred_def_1_revocable1k = create_credential_definition_1_revocable_1k(issuer_token, schema_id_1)
    os.environ["CRED_DEF_ID_1_REVOCABLE_1K"] = cred_def_1_revocable1k
    dotenv.set_key(dotenv_file, "CRED_DEF_ID_1_REVOCABLE_1K", os.environ["CRED_DEF_ID_1_REVOCABLE_1K"])
    dotenv.set_key(dotenv_file, "CRED_DEF_ID_1", os.environ["CRED_DEF_ID_1"])
