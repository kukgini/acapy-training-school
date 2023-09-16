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
python3 setpy.py
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
# this will issue a credential through oob with attachment
curl http://localhost:8002/issue-credential/1
curl http://localhost:8002/credentials
curl http://localhost:8002/connections

# in issuer side, there will be a connection with holder.
# this connection can be reused because it has public DID in further usecases.
curl http://localhost:8003/connections
```

present proof
```
# this will present a proof through connection-less present proof
curl http://localhost:8002/present-proof/1

# verifier has no connection because it was connection-less
# verifier got a present-proof record
curl http://localhost:8004/connections
curl http://localhost:8004/present-proof/records
```

cleanup all
```
curl http://localhost:8002/all/clear
curl http://localhost:8003/all/clear
curl http://localhost:8004/all/clear
```










