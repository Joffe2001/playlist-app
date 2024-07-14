pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "joffe2001/playlist-app:${env.BRANCH_NAME}-${env.BUILD_NUMBER}"
        DOCKER_REGISTRY = 'https://registry.hub.docker.com'
        DOCKER_CREDENTIALS_ID = 'dockerhub-credentials'
        GITHUB_REPO = 'https://github.com/Joffe2001/helm-charts.git'
        GITHUB_CREDENTIALS_ID = 'github-credentials' 
        RECIPIENTS = 'project-idojoffenevo@gmail.com'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        stage('Build Docker Image') {
            steps {
                script {
                    dockerImage = docker.build("${DOCKER_IMAGE}")
                }
            }
        }
        stage('Run Unit Tests') {
            steps {
                dir('src') {
                    sh 'pytest tests/'
                }
            }
        }
        stage('Build HELM Package') {
            steps {
                dir('helm-chart') {
                    sh 'helm package .'
                }
            }
        }
        stage('Push Docker Image and HELM Package') {
            steps {
                script {
                    docker.withRegistry("${DOCKER_REGISTRY}", "${DOCKER_CREDENTIALS_ID}") {
                        dockerImage.push()
                    }
                }
                script {
                    sh "git clone ${GITHUB_REPO} helm-repo"
                    dir('helm-repo') {
                        sh "cp ../helm-chart/*.tgz ."
                        sh "helm repo index --url https://Joffe2001.github.io/helm-charts/ ."
                        sh "git config user.email 'idojoffenevo@gmail.com'"
                        sh "git config user.name 'Joffe'"
                        sh "git add ."
                        sh "git commit -m 'Update Helm chart'"
                        sh "git push"
                    }
                }
            }
        }
        stage('Merge to Master') {
            steps {
                script {
                    sh 'git config user.email "idojoffenevo@gmail.com"'
                    sh 'git config user.name "Joffe"'
                    sh 'git checkout master'
                    sh 'git merge ${env.BRANCH_NAME}'
                    sh 'git push origin master'
                }
            }
        }
        stage('Deploy with Helm') {
            agent {
                docker {
                    image 'alpine/helm:3.5.2'
                    args '-v /var/run/docker.sock:/var/run/docker.sock'
                }
            }
            steps {
                docker.image('alpine/helm:3.5.2').inside('-v /var/run/docker.sock:/var/run/docker.sock') {
                    dir('helm-chart') {
                        sh "helm upgrade --install joffeapp . -n default -f values/joffeapp-values.yaml"
                    }
                }
            }
        }
    }

    post {
        failure {
            mail to: "${RECIPIENTS}",
                 subject: "FAILED: ${env.JOB_NAME} ${env.BUILD_NUMBER}",
                 body: "Something is wrong with ${env.JOB_NAME} ${env.BUILD_NUMBER}. Please check the build logs for more details."
        }
        success {
            mail to: "${RECIPIENTS}",
                 subject: "SUCCESS: ${env.JOB_NAME} ${env.BUILD_NUMBER}",
                 body: "The build for ${env.JOB_NAME} ${env.BUILD_NUMBER} was successful and the Docker image has been pushed."
        }
    }
}