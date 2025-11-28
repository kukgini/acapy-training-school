import os
import logging
import requests
import json
import random
import string
import dotenv

logging.basicConfig(level = logging.DEBUG)

acapy_admin_url="http://acapy:8001"

def create_multitenancy_holder():
    url = f'{acapy_admin_url}/multitenancy/wallet'
    data = {
        "image_url": "https://robohash.org/holder",
        "label": "Holder",
        "wallet_name": "Holder",
        "wallet_webhook_urls": [ "http://holder/webhook" ],
        "wallet_type": "askar",
        "wallet_dispatch_type": "default",
        "wallet_key_derivation": "RAW",
        "wallet_key": "BGiQz6MbFnw12D3UM8SPehtkoXLMj2BiDx85oxoUQ4L1",
        "key_management_mode": "managed"
    }
    response = requests.post(url, json=data)
    try:
        tenant_info = response.json()
        tenant_token = tenant_info["token"]
        return tenant_token
    except BaseException as err:
        raise Exception(f"Failed to create holder tenant. {response.text}")

def create_multitenancy_verifier():
    url = f'{acapy_admin_url}/multitenancy/wallet'
    data = {
        "image_url": "https://robohash.org/verifier",
        "label": "Varifier",
        "wallet_name": "Verifier",
        "wallet_webhook_urls": [ "http://verifier/webhook" ],
        "wallet_type": "askar",
        "wallet_dispatch_type": "default",
        "wallet_key_derivation": "RAW",
        "wallet_key": "BGiQz6MbFnw12D3UM8SPehtkoXLMj2BiDx85oxoUQ4L1",
        "key_management_mode": "managed"
    }
    response = requests.post(url, json=data)
    try:
        tenant_info = response.json()
        tenant_token = tenant_info["token"]
        return tenant_token
    except BaseException as err:
        raise Exception(f"Failed to create verifier tenant. {response.text}")

def create_multitenancy_issuer():
    url = f'{acapy_admin_url}/multitenancy/wallet'
    data = {
        "image_url": "https://robohash.org/issuer",
        "label": "Issuer",
        "wallet_name": "Issuer",
        "wallet_webhook_urls": [ "http://issuer/webhook" ],
        "wallet_type": "askar",
        "wallet_dispatch_type": "default",
        "wallet_key_derivation": "RAW",
        "wallet_key": "BGiQz6MbFnw12D3UM8SPehtkoXLMj2BiDx85oxoUQ4L1",
        "key_management_mode": "managed"
    }
    response = requests.post(url, json=data)
    try:
        tenant_info = response.json()
        tenant_token = tenant_info["token"]
        return tenant_token
    except BaseException as err:
        raise Exception(f"Failed to create issuer tenant. {response.text}")

def create_issuer_did(issuer_token, issuer_public_did_seed):
    url = f"{acapy_admin_url}/wallet/did/create"
    headers = {
        'Authorization': f'Bearer {issuer_token}',
    }
    data = {
        'seed': f"{issuer_public_did_seed}",
    }
    response = requests.post(url, json=data, headers=headers)
    try:
        j = response.json()
        return j['result']['did']
    except BaseException as err:
        raise Exception(f"Failed to create issuer DID. {response.text}")
    
def accept_taa(issuer_token):
    url1 = f"{acapy_admin_url}/ledger/taa"
    headers = {
        'Authorization': f'Bearer {issuer_token}',
    }
    res1 = requests.get(url1, headers=headers)
    try:
        taa = res1.json()
        taa_text = taa["result"]["taa_record"]["text"]
        taa_version = taa["result"]["taa_record"]["version"]
    except BaseException as err:
        raise Exception(f"Failed to get TAA. {res1.text}")
    
    url2 = f"{acapy_admin_url}/ledger/taa/accept"
    data = {
        'mechanism': 'on_file',
        'text': taa_text,
        'version': taa_version,
    }
    res2 = requests.post(url2, json=data, headers=headers)
    try:
        j = res2.json()
    except BaseException as err:
        raise Exception(f"Failed to accept TAA. {res2.text}")


def assign_issuer_did_public(issuer_token, did):
    url = f"{acapy_admin_url}/wallet/did/public?did={did}"
    headers = {
        'Authorization': f'Bearer {issuer_token}',
    }
    response = requests.post(url, headers=headers)
    try:
        j = response.json()
        return j
    except BaseException as err:
        raise Exception(f"Failed to assign public DID. {response.text}")

def create_schema_1(issuer_token, issuer_did, schema_version):
    url = f'{acapy_admin_url}/schemas'
    headers = {
        'Authorization': f'Bearer {issuer_token}',
    }
    data = {
        'attributes': ['name','score','date','birthdate_dateint','timestamp'],
        'schema_name': 'transcript',
        'schema_version': schema_version,
    }
    response = requests.post(url, json=data, headers=headers)
    try:
        schema = response.json()
        return schema["sent"]["schema_id"]
    except BaseException as err:
        raise Exception(f"Failed to create schema. {response.text}")
    

def create_credential_definition_non_revoc(issuer_token, issuer_did, schema_id):
    url = f'{acapy_admin_url}/credential-definitions'
    headers = {
        'Authorization': f'Bearer {issuer_token}',
    }
    data = {
        'schema_id': schema_id,
        'tag': 'non-revoc',
        'support_revocation': False,
    }
    response = requests.post(url, json=data, headers=headers)
    try:
        j = response.json()
        return j["sent"]["credential_definition_id"]
    except BaseException as err:
        raise Exception(f"Failed to create credential definition. {response.text}")
    

def create_credential_definition_1_revocable_1k(issuer_token, issuer_did, schema_id):
    url = f'{acapy_admin_url}/credential-definitions'
    headers = {
        'Authorization': f'Bearer {issuer_token}',
    }
    data = {
        'schema_id': schema_id,
        'tag': 'revocable1k',
        'support_revocation': True,
        'revocation_registry_size': 1000,
    }
    response = requests.post(url, json=data, headers=headers)
    try:
        j = response.json()
        return j["sent"]["credential_definition_id"]
    except BaseException as err:
        raise Exception(f"Failed to create credential definition. {response.text}")
    
if __name__ == '__main__':
    try:
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
        
        # SETUP issuer step 0, !!! MANUAL STEP !!!, register issuer DID as endorser role.
        # register new DID into indy ledger with endorser role.
        # you can use this UI http://test.bcovrin.vonx.io

        # for the other indy-networks, you may need following roles.
        # only steward can register a DID as endorser role.
        # only trustee can register a DID as steward role.
        
        # SETUP issuer step 1, create new DID 
        issuer_did = create_issuer_did(issuer_token, issuer_public_did_seed)
        os.environ["ISSUER_PUBLIC_DID"] = issuer_did
        dotenv.set_key(dotenv_file, "ISSUER_PUBLIC_DID", os.environ["ISSUER_PUBLIC_DID"])

        # SETUP issuer step 2, !!!OPTIONAL!!! transaction author agreement
        # some ledger requires to accept TAA before sending transactions. (e.g. Indicio)
        # accept_taa(issuer_token)

        # SETUP issuer step 3, set created new DID as a public DID
        issuer_did = os.environ["ISSUER_PUBLIC_DID"]
        assign_issuer_did_public(issuer_token, issuer_did)

        # SETUP issuer step 4, create schema.
        schema_id_1 = create_schema_1(issuer_token, issuer_did, schema_version)
        os.environ["SCHEMA_ID_1"] = schema_id_1
        dotenv.set_key(dotenv_file, "SCHEMA_ID_1", os.environ["SCHEMA_ID_1"])

        # SETUP issuer step 5, create non revocable credential definition.
        schema_id_1 = os.environ["SCHEMA_ID_1"]
        cred_def_1_non_revoc = create_credential_definition_non_revoc(issuer_token, issuer_did, schema_id_1)
        os.environ["CRED_DEF_ID_1_NON_REVOC"] = cred_def_1_non_revoc
        dotenv.set_key(dotenv_file, "CRED_DEF_ID_1_NON_REVOC", os.environ["CRED_DEF_ID_1_NON_REVOC"])

        # SETUP issuer step 6, create revicable credential definition. (default issue type)
        cred_def_1_revocable1k = create_credential_definition_1_revocable_1k(issuer_token, issuer_did, schema_id_1)
        os.environ["CRED_DEF_ID_1_REVOCABLE_1K"] = cred_def_1_revocable1k
        dotenv.set_key(dotenv_file, "CRED_DEF_ID_1_REVOCABLE_1K", os.environ["CRED_DEF_ID_1_REVOCABLE_1K"])
        dotenv.set_key(dotenv_file, "CRED_DEF_ID_1", os.environ["CRED_DEF_ID_1_NON_REVOC"])

    except Exception as err:
        logging.error(f"Oops! setup failed. {err=}")
