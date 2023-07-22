from src import config
import os
from pyngrok import ngrok, conf
from secrets_manager import NGROK_AUTH_TOKEN

def open_tunnel():
    
    # Enter your authtoken, which can be copied from https://dashboard.ngrok.com/auth
    conf.get_default().auth_token = NGROK_AUTH_TOKEN

    # Open a TCP ngrok tunnel to the SSH server
    connection_string = ngrok.connect(22, "tcp").public_url

    ssh_url, port = connection_string.strip("tcp://").split(":")
    print(f" * ngrok tunnel available, access with `ssh root@{ssh_url} -p{port}`")

    # Open a ngrok tunnel to the HTTP server
    public_url = ngrok.connect(config.PORT).public_url
    print(" * ngrok tunnel \"{}\" -> \"http://127.0.0.1:{}\"".format(public_url, config.PORT))
    
    return public_url