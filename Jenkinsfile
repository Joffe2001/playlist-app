pipeline {
    agent {
        kubernetes {
            yamlFile 'helm-chart/setup.yaml'
            defaultContainer 'builder'
        }
    }

    environment {
        DOCKER_REGISTRY = 'https://registry.hub.docker.com'
        GITHUB_REPO = 'Joffe2001/playlist-app'
        MASTER_BRANCH = 'master'
        GITHUB_TOKEN = credentials('github-token')
    }

    stages {
        stage('Checkout Code') {
            steps {
                checkout scm
            }
        }

        stage('Setup Environment') {
            steps {
                sh 'apk update'
                sh 'apk add py3-pip'
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
                    def version = "v1.${env.BUILD_NUMBER}"
                    def dockerImage = docker.build("joffe2001/playlist-app:${version}", "-f ./src/Dockerfile ./src")
                }
            }
        }

        stage('Run Unit Tests') {
            steps {
                sh 'pytest src/tests/'
                sh 'helm package helm-chart/'
            }
        }

        stage('Create Pull Request') {
            when {
                branch 'issue'
            }
            steps {
                script {
                    def payload = [
                        title: "Automated Pull Request: ${env.BRANCH_NAME} -> ${MASTER_BRANCH}",
                        body: "Automated pull request created after successful tests on ${env.BRANCH_NAME}.",
                        head: env.BRANCH_NAME,
                        base: MASTER_BRANCH
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

                    def prNumber = response.data.number 
                    httpRequest(
                        acceptType: 'APPLICATION_JSON',
                        contentType: 'APPLICATION_JSON',
                        httpMode: 'POST',
                        requestBody: groovy.json.JsonOutput.toJson([]),
                        url: "https://api.github.com/repos/Joffe2001/playlist-app/pulls/${prNumber}/merge",
                        headers: [
                            Authorization: "token ${GITHUB_TOKEN}"
                        ]
                    )
                }
            }
        }

        stage('Push Docker Image and HELM Package') {
            when {
                beforeAgent true
                changeset "branches: [${MASTER_BRANCH}]"
            }
            steps {
                script {
                    def version = "v1.${env.BUILD_NUMBER}"
                    docker.withRegistry('https://registry.hub.docker.com', 'dockerhub-credentials') {
                        dockerImage.push(version)
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
                if (env.BRANCH_NAME == MASTER_BRANCH) {
                    mail to: 'project-idojoffenevo@gmail.com',
                         subject: "SUCCESS: ${env.JOB_NAME} ${env.BUILD_NUMBER}",
                         body: "The build for ${env.JOB_NAME} ${env.BUILD_NUMBER} was successful."
                }
            }
        }
    }
}