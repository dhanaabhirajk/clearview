from src import config
from dotenv import load_dotenv
import os
from pyngrok import ngrok, conf

def open_tunnel():
    load_dotenv()
    
    # Enter your authtoken, which can be copied from https://dashboard.ngrok.com/auth
    conf.get_default().auth_token = os.environ['NGROK_AUTH_TOKEN']

    # Open a TCP ngrok tunnel to the SSH server
    connection_string = ngrok.connect(22, "tcp").public_url

    ssh_url, port = connection_string.strip("tcp://").split(":")
    print(f" * ngrok tunnel available, access with `ssh root@{ssh_url} -p{port}`")

    # Open a ngrok tunnel to the HTTP server
    public_url = ngrok.connect(config.port).public_url
    print(" * ngrok tunnel \"{}\" -> \"http://127.0.0.1:{}\"".format(public_url, config.port))
    
    return public_url