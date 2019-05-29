# ARQCONF May 2019 Operators Talk

## Code Examples

Build using [Metacontroller](https://metacontroller.app/)


### autoingress-operator

Automatically create an ingress rule to expose services that have the annotation "autoingress.flugel.it".

Port 80 of the service is exposed in the virtual host services.example.com/{SERVICE_NAME}.{SERVICE_NAMESPACE}.

* Uses DecoratorController

### customer-app-operator

Automatically populates:

* Deployment
* Service
* Ingress rule
* ConfigMap
* Namespace

From a CDR containing just the customer id. This is a very simple approach to provide isolated instances for non-multitenant applications.

* Uses CompositeController