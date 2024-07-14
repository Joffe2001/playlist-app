pipeline {
    agent {
        kubernetes {
            yamlFile 'helm-chart/setup.yaml'
            defaultContainer 'builder'
        }
    }

    stages {
        stage('Checkout Code') {
            steps {
                checkout scm
            }
        }

        stage('Setup Environment') {
            steps {
                sh 'apk update && add py-pip'
                sh 'pip install --upgrade pip'
            }
        }

        stage('Setup Tests') {
            steps {
                dir('src') {
                    sh 'pip install -r requirements.txt'
                }
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
                    dockerImage = docker.build("joffe2001/playlist-app:${env.BRANCH_NAME}-${env.BUILD_ID}")
                }
            }
        }

        stage('Run Unit Tests') {
            steps {
                sh 'pytest tests/'
                sh 'helm package src/helm-chart/'
            }
        }

        stage('Create Pull Request') {
            when {
                branch 'issue-*'
            }
            steps {
                script {
                    def payload = [
                        title: "Automated Pull Request: ${env.BRANCH_NAME} -> main",
                        body: "Automated pull request created after successful tests on ${env.BRANCH_NAME}.",
                        head: env.BRANCH_NAME,
                        base: 'main'
                    ]

                    def response = httpRequest(
                        acceptType: 'APPLICATION_JSON',
                        contentType: 'APPLICATION_JSON',
                        httpMode: 'POST',
                        requestBody: groovy.json.JsonOutput.toJson(payload),
                        url: "https://api.github.com/repos/Joffe2001/playlist-app/pulls",
                        headers: [
                            Authorization: "token ${GITHUB_TOKEN}"
                        ]
                    )

                    echo "Created Pull Request: ${response.content}"
                }
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
                    sh 'helm repo index --url https://github.com/Joffe2001/playlist-app/tree/master/src/helm-chart/ --merge index.yaml src/helm-chart/'
                    sh 'helm push src/helm-chart-*.tgz https://github.com/Joffe2001/playlist-app/tree/master/src/helm-chart/'
                }
            }
        }
    }

    post {
        failure {
            mail to: 'project-idojoffenevo@gmail.com',
                 subject: "FAILED: ${env.JOB_NAME} ${env.BUILD_NUMBER}",
                 body: "Something is wrong with ${env.JOB_NAME} ${env.BUILD_NUMBER}. Please check the build logs for more details."
        }

        success {
            script {
                if (env.BRANCH_NAME == 'main') {
                    mail to: 'project-idojoffenevo@gmail.com',
                         subject: "SUCCESS: ${env.JOB_NAME} ${env.BUILD_NUMBER}",
                         body: "The build for ${env.JOB_NAME} ${env.BUILD_NUMBER} was successful."
                }
            }
        }
    }
}