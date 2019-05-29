import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
from pprint import pformat

logging.basicConfig(level=logging.INFO)

def sync(obj, attachments):
    logging.info(f"Sync for parent:\n {pformat(obj)}")

    virtualhost = 'services.example.com'
    desired_attachments = []

    service_name = obj['metadata']['name']
    ns = obj['metadata']['namespace']
    path = f'/{service_name}.{ns}'

    # Ingress definition
    ingress = {
        'apiVersion': 'networking.k8s.io/v1beta1',
        'kind': 'Ingress',
        'metadata': {
            'name': service_name+'-autoingress',
            'namespace': ns,
            'annotations': {
                'nginx.ingress.kubernetes.io/rewrite-target': '/',
            },
        },
        'spec': {
            'rules': [{
                'host': virtualhost,
                'http': {
                    'paths': [{
                        'path': path,
                        'backend': {
                            'serviceName': service_name,
                            'servicePort': 80
                        }
                    }]
                }
            }]
        }
    }
    desired_attachments.append(ingress)
    
    result = {'labels': {}, 'annotations': {}, 'attachments': desired_attachments}
    logging.info(f"Sync result:\n {pformat(result)}")
    return result


class Controller(BaseHTTPRequestHandler):
    def do_POST(self):
        # Serve the sync() function as a JSON webhook.
        observed = json.loads(self.rfile.read(
            int(self.headers.get('content-length'))))
        desired = sync(observed['object'], observed['attachments'])
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(desired).encode())


if __name__ == '__main__':
    print("server starting...")
    HTTPServer(('', 80), Controller).serve_forever()
