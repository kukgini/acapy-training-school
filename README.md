Although there is a demo project provided in aries-cloudagent-python, it was not easy for me to understand the relationship between the agent and agent controller for the actual service. Therefore, I made this practice environment for educational / excercise purposes. Hopefully, this repository will be helpful to beginners, especially in the context of multitenancy.

# setup guide

## register an endorser DID

register an endorser DID with seed on test.bcovin.vonx.io and remember that seed.

## setup environment variables

Copy env.template to .env
```bash
cp env.template .env
```

Edit .env
```bash
vi .env
```
You need only two options to edit.
* ISSUER_PUBLIC_DID_SEED='seed for a endorser that already registered above'
* SCHEMA_VERSION='whatever you want in semver format'

# build docker images

```bash
docker-compose build
```

# run base containers

```bash
docker-compose up postgres tails acapy -d
```

# run setup.py

```bash
# this will setup 3 tenant (issuer / holder / verifier) in multi-tenancy acapy
# and for the issuer, issuer public DID, schema and cred_def also setup. 

# prepare python environment to run setup
python3 -m venv venv
source venv/bin/activate
pip3 install requests python-dotenv

# run setup. this will fill in remaining .env variables.
python3 setup.py

# clean up python environment
deactivate
rm -rf venv
```

# run remain containers

```bash
docker-compose up -d
```

practice environment is ready now.

# how to use

## ports explained

* port 8000 multi tenent agency itself
* port 8001 multi tenant controller api service
* port 8002 holder agent controller
* port 8003 issuer agent controller
* port 8004 verifier agent controller

## issue credential

```bash
# this will issue a credential through oob with attachment.
# nomally, holder should be received oob invitation in other ways.
# for example, holder could receives oob invitation from qr code.
# anyway, this is a simple demonstration of the issuance flow.

# this api will receive and accept a oob invitation from issuer.
# credential offer is attached in that invitation.
# being process that invitation, holder receives a credential from issuer. 
curl http://localhost:8002/issue-credential/1
curl http://localhost:8002/credentials
curl http://localhost:8002/connections

# in issuer side, there is a credential exchange record with no connection.
# this is because isser made a oob invitation without handshake_protocols.
curl http://localhost:8003/credential-exchange/records
curl http://localhost:8003/connections
```

## present proof

```bash
# this will present a proof through connection-less present proof

# this api will receive and accept a oob invitation from verifier.
# presentation request is attached in that invitation.
# holder build a proof of that request and send it to verifier.
curl http://localhost:8002/present-proof/1

# verifier has no connection because it was connection-less present proof
# while verifier got a present-proof record.
curl http://localhost:8004/proof-exchange/records
curl http://localhost:8004/connections
```

cleanup all
```bash
curl http://localhost:8002/all/clear
curl http://localhost:8003/all/clear
curl http://localhost:8004/all/clear
```










