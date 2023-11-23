setup guide

register an endorser DID with seed on test.bcovin.vonx.io

copy env.template to .env
```
cp env.template .env
```

edit .env
```
vi .env
```
* ISSUER_PUBLIC_DID_SEED='seed for a endorser that already registered above'
* SCHEMA_VERSION='whatever you want in semver format'

build docker images
```
docker-compose build
```

run containers
```
docker-compose up postgres tails acapy -d
```

run setup.py
```
python3 -m venv venv
source venv/bin/activate
pip3 install requests python-dotenv
python3 setup.py
deactivate
rn -rf venv
```

stop containers and re-run
```
docker-compose down
docker-compose up -d
```

roles
* port 8002 holder
* port 8003 issuer
* port 8004 verifier

issue credential
```
curl http://localhost:8002/issue-credential/1
curl http://localhost:8002/credentials
curl http://localhost:8002/connections
curl http://localhost:8003/connections
```

present proof
```
curl http://localhost:8002/present-proof/1
curl http://localhost:8004/present-proof/records
```

cleanup all
```
curl http://localhost:8002/all/clear
curl http://localhost:8003/all/clear
curl http://localhost:8004/all/clear
```










