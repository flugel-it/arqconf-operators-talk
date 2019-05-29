install_metacontroller:
	# Create metacontroller namespace.
	kubectl create namespace metacontroller --dry-run -o yaml | kubectl apply -f -
	# Create metacontroller service account and role/binding.
	kubectl apply -f metacontroller-rbac.yaml
	# Create CRDs for Metacontroller APIs, and the Metacontroller StatefulSet.
	kubectl apply -f metacontroller.yaml

remove_all:
		kubectl delete -f metacontroller.yaml
		kubectl delete -f metacontroller-rbac.yaml
		kubectl delete namespace metacontroller