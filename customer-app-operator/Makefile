NAMESPACE=customerapp

install_all: create_namespace install_crds install_controller configmap webhook

create_namespace:
	kubectl create namespace ${NAMESPACE} --dry-run -o yaml | kubectl apply -f -

install_crds:
	kubectl apply -f config/crds.yaml

install_controller:	
	# Register the webhook in metacontroller to receive events about our custom resource and pods
	kubectl -n ${NAMESPACE} apply -f config/controller.yaml

configmap:
	# Install webhook code
	kubectl -n ${NAMESPACE} create configmap customerapp-controller --from-file=sync.py --dry-run -o yaml | kubectl apply -f -

webhook:
	# Install webhook deployment
	kubectl -n ${NAMESPACE} apply -f config/webhook.yaml

remove_all:
	kubectl -n ${NAMESPACE} delete configmap customerapp-controller
	kubectl -n ${NAMESPACE} delete -f config/webhook.yaml
	kubectl -n ${NAMESPACE} delete -f config/controller.yaml
	kubectl delete -f config/crds.yaml
	kubectl delete namespace ${NAMESPACE}

example:
	kubectl apply -f config/example-use.yaml

example_delete:
	kubectl delete -f config/example-use.yaml

