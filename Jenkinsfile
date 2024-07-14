pipeline {
    agent {
        label 'docker' 
    }

    environment {
        DOCKER_REGISTRY = 'hub.docker.com'
        DOCKER_IMAGE = 'joffe2001/playlist-app'
        HELM_REPO_URL = 'https://github.com/Joffe2001/playlist-app.git'
        HELM_CHART_PATH = 'helm-chart'
        GIT_CREDENTIALS_ID = '8cd550f2-e8f1-48d2-92c5-3ba53781d322'
        DOCKER_CREDENTIALS_ID = 'credential/docker-joffe-credential'
    }

    stages {
        stage('Checkout Code') {
            steps {
                checkout scm
            }
        }

        stage('Setup Tests') {
            steps {
                sh 'pip install -r requirements.txt'
            }
        }

        stage('Run Tests') {
            steps {
                sh 'pytest'
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    docker.build("${DOCKER_IMAGE}:${env.BRANCH_NAME}")
                }
            }
        }

        stage('Create Merge Requests') {
            when {
                branch 'issue-*'
            }
            steps {
                echo 'Creating merge request for issue branch'
                // Add your merge request creation logic here
            }
        }

        stage('Push Docker Image') {
            when {
                branch 'master'
            }
            steps {
                script {
                    docker.withRegistry("https://${DOCKER_REGISTRY}", "${DOCKER_CREDENTIALS_ID}") {
                        docker.image("${DOCKER_IMAGE}:${env.BRANCH_NAME}").push('latest')
                    }
                }
            }
        }

        stage('Clean Workspace') {
            when {
                branch 'master'
            }
            steps {
                cleanWs()
            }
        }

        stage('Checkout Helm Chart Repo') {
            when {
                branch 'master'
            }
            steps {
                dir('helm-chart') {
                    checkout([$class: 'GitSCM', branches: [[name: '*/master']],
                              userRemoteConfigs: [[url: "${HELM_REPO_URL}", credentialsId: "${GIT_CREDENTIALS_ID}"]]])
                }
            }
        }

        stage('Update Helm Charts') {
            when {
                branch 'master'
            }
            steps {
                dir('helm-chart') {
                    sh 'helm package .'
                    sh 'helm repo index . --url https://github.com/Joffe2001/playlist-app/helm-chart'
                }
            }
        }

        stage('Commit Changes to Chart Repo') {
            when {
                branch 'master'
            }
            steps {
                dir('helm-chart') {
                    sh '''
                       git config user.email "idojoffenevo@gmail.com"
                       git config user.name "Jenkins"
                       git add .
                       git commit -m "Update Helm charts"
                       git push origin master
                       '''
                }
            }
        }
    }

    post {
        failure {
            emailext (
                subject: "Failed Pipeline: ${env.JOB_NAME} ${env.BUILD_NUMBER}",
                body: "The Jenkins pipeline ${env.JOB_NAME} build ${env.BUILD_NUMBER} has failed. Please check the Jenkins console output for more details.",
                recipientProviders: [[$class: 'CulpritsRecipientProvider'], [$class: 'RequesterRecipientProvider']],
                to: 'idojoffenevo@gmail.com'
            )
        }

        success {
            script {
                if (currentBuild.previousBuild && currentBuild.previousBuild.result == 'FAILURE') {
                    emailext (
                        subject: "Pipeline Success After Failure: ${env.JOB_NAME} ${env.BUILD_NUMBER}",
                        body: "The Jenkins pipeline ${env.JOB_NAME} build ${env.BUILD_NUMBER} has succeeded after a previous failure.",
                        recipientProviders: [[$class: 'CulpritsRecipientProvider'], [$class: 'RequesterRecipientProvider']],
                        to: 'idojoffenevo@gmail.com'
                    )
                }
            }
        }
    }
}