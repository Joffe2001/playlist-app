# Ido's DevOps project

This is my final DevOps project, a web server written in python and HTML (And using js and css) for sharing playlists.
In this README I'll explain how I created a Pipeline that detect a change in the Github repository, run tests and then change the Cluster based on the last commit.

## Prerequisites
Ensure you have the following installed:
- Helm
- Python3
- pip

## Cluser setup (Using Docker Desktop)
1. Install Docker Desktop
2. Enable Kubernetes in Docker Desktop
3. Ensure kubectl is configured to communicate with your Docker Desktop Kubernetes cluster:
   ```bash
   kubectl config view
   kubectl get nodes
4. **Clone the Repository**
   ```bash
   git clone https://github.com/Joffe2001/playlist-app/
   cd playlist-app
5. Create the namespaces: 
   ```bash
   kubectl create namespace jenkins
   kubectl create namespace argocd
   kubectl create namespace monitoring
6. Add the helm repositories:
   ```bash
   helm repo add jenkins https://charts.jenkins.io
   helm repo add bitnami https://charts.bitnami.com/bitnami #For mongodb
   helm repo add argo https://argoproj.github.io/argo-helm
   helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
   helm repo add grafana https://grafana.github.io/helm-charts
   helm repo update
7. Install Helm charts with custom values files:
   ```bash
   helm install joffeapp . -n default -f values/joffeapp-values.yaml
   helm install mongodb bitnami/mongodb -n default -f values/mongodb-values.yaml
   helm install jenkins jenkins/jenkins -n jenkins -f values/jenkins-values.yaml
   helm install argocd argo/argo-cd -n argocd
   helm install prometheus prometheus-community/prometheus -n monitoring
   helm install prometheus prometheus-community/kube-prometheus-stack -n monitoring

## App setup
   ```bash
   kubectl port-forward svc/joffeapp 5000:5000 -n default
   kubectl port-forward svc/mongodb 27017:27017 -n default

## Jenkins Setup
   ```bash
   kubectl port-forward svc/jenkins 8080:8080 --namespace jenkins
1. You'll have to create the following credentials for the project:
- Docker login data (Using Username and Password): To ensure that Jenkins can push the Docker image to Dockerhub
- Github token (Using secret text): To detect the data from the Github repository and be for it to push and create pull requests
2. Insure your Email in configured in the Jenkins system for it to be able to send you a confirmation email.
3. Create a multibranch Pipline for the project, Jenkins will detect the Jenkinsfile in the repository.

## ArgoCD Setup
   ```bash
   kubectl apply -f argo/application-argo.yaml
   kubectl apply -f argo/secret-argo.yaml
   kubectl port-forward svc/argocd 443:443 --namespace argocd

## Prometheus and Grafana setup
   ```bash
   kubectl apply -f prometheus/prometheus-rules.yaml
   kubectl apply -f prometheus/serviceconfig.yaml



