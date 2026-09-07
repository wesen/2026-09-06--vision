import argparse
import uvicorn
from .app import create_app
p=argparse.ArgumentParser(description='Guided video component laboratory')
p.add_argument('--port',type=int,default=8780)
a=p.parse_args()
uvicorn.run(create_app(),host='127.0.0.1',port=a.port)
