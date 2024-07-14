pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        stage('Build Docker Image') {
            steps {
                script {
                    dockerImage = docker.build("joffe2001/playlist-app:${env.BRANCH_NAME}-${env.BUILD_ID}")
                }
            }
        }
        stage('Run Unit Tests') {
            steps {
                sh 'pytest tests/'
            }
        }
        stage('Build HELM Package') {
            steps {
                sh 'helm package your_helm_chart_directory'
            }
        }
        stage('Push Docker Image and HELM Package') {
            when {
                branch 'main'
            }
            steps {
                script {
                    docker.withRegistry('https://registry.hub.docker.com', 'dockerhub-credentials') {
                        dockerImage.push("${env.BRANCH_NAME}-${env.BUILD_ID}")
                    }
                }
                sh 'helm push your_helm_chart-*.tgz your_helm_repository'
            }
        }
    }

    post {
        failure {
            mail to: 'project-managers@example.com, developer@example.com',
                 subject: "FAILED: ${env.JOB_NAME} ${env.BUILD_NUMBER}",
                 body: "Something is wrong with ${env.JOB_NAME} ${env.BUILD_NUMBER}. Please check the build logs for more details."
        }
        success {
            script {
                if (env.BRANCH_NAME == 'main') {
                    mail to: 'project-managers@example.com, developer@example.com',
                         subject: "SUCCESS: ${env.JOB_NAME} ${env.BUILD_NUMBER}",
                         body: "The build for ${env.JOB_NAME} ${env.BUILD_NUMBER} was successful."
                }
            }
        }
    }
}