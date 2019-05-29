import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
from pprint import pformat

logging.basicConfig(level=logging.INFO)

def sync(parent, children):
    logging.info(f"Sync for parent:\n {pformat(parent)}")

    # Compute status based on observed state.
    desired_status = {}


    # Get customer name from CustomerApp.spec
    customer = parent['spec']['customer']
    logging.info(f"Customer is: {customer}")

    # Calculated values
    ns = customer+'-ns'
    logging.info(f"NS is: {ns}")
    virtualhost = customer+'.example.com'
    logging.info(f"Virtual host: {virtualhost}")

    desired_children = []

    # Namespace definition
    namespace = {
        'apiVersion': 'v1',
        'kind': 'Namespace',
        'metadata': {
            'name': ns,
        },
    }
    desired_children.append(namespace)

    # Configmap definition
    configmap = {
        'kind': 'ConfigMap',
        'apiVersion': 'v1',
        'metadata': {
            'name': 'app-static-files',
            'namespace': ns
        },
        'data': {
            'index.html': f"""<!doctype html>
                <html>
                    <head><meta charset="utf-8">
                        <title>Customer homepage</title>
                    </head>
                    <body>
                        <h1>Example page for {customer}</h1>
                    </body>
                </html>"""
        }
    }
    desired_children.append(configmap)
    # Deployment definition
    deployment = {
        'apiVersion': 'apps/v1',
        'kind': 'Deployment',
        'metadata': {
            'name': 'app-deployment',
            'namespace': ns
        },
        'spec': {
            'replicas': 1,
            'selector': {
                'matchLabels': {
                    'app': 'app',
                }
            },
            'template': {
                'metadata': {
                    'labels': {'app': 'app'}
                },
                'spec': {
                    'containers': [{
                        'name': 'app',
                        'image': 'nginx:1.15.12',
                        'ports': [{'name': 'http-port', 'containerPort': 80}],
                        'volumeMounts': [{
                            'readOnly': True,
                            'mountPath': '/usr/share/nginx/html',
                            'name': 'html-files'
                        }]
                    }],
                    'volumes': [{
                        'name': 'html-files',
                        'configMap': {'name': 'app-static-files'}
                    }]
                }
            }
        }
    }
    desired_children.append(deployment)

    # Service definition
    service = {
        'apiVersion': 'v1',
        'kind': 'Service',
        'metadata': {
            'name': 'app-service',
            'namespace': ns
        },
        'spec': {
            'type': 'NodePort',
            'ports': [{
                'port': 80,
                'targetPort': 80,
                'protocol': 'TCP',
                'name': 'http'
            }],
            'selector': {'app': 'app'}
        }
    }
    desired_children.append(service)

    # Ingress definition
    ingress = {
        'apiVersion': 'networking.k8s.io/v1beta1',
        'kind': 'Ingress',
        'metadata': {
            'name': 'app-rules',
            'namespace': ns
        },
        'spec': {
            'rules': [{
                'host': virtualhost,
                'http': {
                    'paths': [{
                        'path': '/',
                        'backend': {
                            'serviceName': 'app-service',
                            'servicePort': 80
                        }
                    }]
                }
            }]
        }
    }
    desired_children.append(ingress)
    
    result = {'status': desired_status, 'children': desired_children}
    logging.info(f"Sync result:\n {pformat(result)}")
    return result


class Controller(BaseHTTPRequestHandler):
    def do_POST(self):
        # Serve the sync() function as a JSON webhook.
        observed = json.loads(self.rfile.read(
            int(self.headers.get('content-length'))))
        desired = sync(observed['parent'], observed['children'])
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(desired).encode())


if __name__ == '__main__':
    print("server starting...")
    HTTPServer(('', 80), Controller).serve_forever()
