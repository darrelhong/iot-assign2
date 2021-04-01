## Run

Main program
```
sudo python3 edge-main.py --rpi --ser --cloudhost=
```

Edge server
```
FLASK_APP=edge_server FLASK_ENV=development FLASK_RUN_HOST=0.0.0.0 flask run
```

Cloud server
```
FLASK_APP=cloud_server FLASK_ENV=development FLASK_RUN_HOST=0.0.0.0 FLASK_RUN_PORT=5001
```

## Devices
CE:E5:E1:2F:81:3E `vepag`

F0:8A:89:C0:09:45 `gigez`

D8:8F:C6:74:32:B0 `pituz`
