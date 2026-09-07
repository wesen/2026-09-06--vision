"""Serve on explicit local interfaces; repeat --host for loopback and Tailscale."""
import argparse
import socket
import uvicorn
from .app import create_app
p=argparse.ArgumentParser(description='Guided video component laboratory')
p.add_argument('--port',type=int,default=8780)
p.add_argument('--host',action='append',help='Explicit IPv4 bind address; repeat for multiple interfaces')
a=p.parse_args()
sockets=[]
try:
    for host in a.host or ['127.0.0.1']:
        sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        sock.bind((host,a.port));sock.listen(128);sockets.append(sock)
    uvicorn.Server(uvicorn.Config(create_app(),log_level='info')).run(sockets=sockets)
finally:
    for sock in sockets: sock.close()
