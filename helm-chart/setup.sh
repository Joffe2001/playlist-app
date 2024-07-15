#!/bin/bash

# Start minikube cluster
minikube start

# Create namespaces
kubectl create namespace jenkins
kubectl create namespace argocd
kubectl create namespace observation

# Add Helm repositories
helm repo add jenkins https://charts.jenkins.io
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo add argo https://argoproj.github.io/argo-helm
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo add cowboysysop https://cowboysysop.github.io/charts/  # For mongo-express
helm repo update


# Install Helm charts with custom values files
helm install joffeapp . -n default -f values/joffeapp-values.yaml
helm install mongo-express cowboysysop/mongo-express -n default -f values/values.yaml
helm install mongodb bitnami/mongodb -n default -f values/mongodb-values.yaml
helm install jenkins jenkins/jenkins -n jenkins -f values/jenkins-values.yaml
helm install argocd argo/argo-cd -n argocd -f values/argocd-values.yaml
helm install prometheus prometheus-community/prometheus -n observation -f values/prometheus-values.yaml
helm install grafana grafana/grafana -n observation -f values/grafana-values.yaml

# Apply sanity-check for the application
kubectl apply -f templates/job.yaml

# Apply the service configuration
kubectl apply -f templates/service.yaml

# Port-forwarding commands for deployments
kubectl port-forward svc/mongo-express 8081:8081 -n defaultkubectl port-forward svc/mongodb 27017:27017 -n default  &
&
kubectl port-forward svc/joffeapp 5000:5000 -n default &
kubectl port-forward svc/jenkins 8080:8080 --namespace jenkins &
kubectl port-forward svc/argocd 443:443 --namespace argocd &
kubectl port-forward svc/grafana 3000:3000 --namespace observation &
kubectl port-forward svc/prometheus-server 80:80 --namespace observation &

# Wait for background processes to finish
wait

# Checking:
# kubectl get ns - Check that all the namespaces are present
# helm repo list - Check that all the repos are present
# kubectl get svc --all-namespaces - Check if all the services are up
# kubectl get pods --all-namespaces - Check if all the pods are up
# kubectl create secret generic mongodb --from-literal=mongodb-root-password=rootroot -n default --dry-run=client -o yaml | kubectl apply -f -