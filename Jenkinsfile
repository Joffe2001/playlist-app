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
    }

    stages {
        stage('Checkout Code') {
            steps {
                checkout scm
                sh 'git config --global --add safe.directory ${WORKSPACE}'
            }
        }

        stage('Setup Environment') {
            steps {
                sh 'apk update'
                sh 'apk add py3-pip'
                sh 'pip install --upgrade pip'
                dir('src') {
                    sh 'pip install -r requirements.txt'
                }
            }
        }

        stage('Run Tests') {
            steps {
                sh 'pytest src/'
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    def version = "v1.${env.BUILD_NUMBER}"
                    dockerImage = docker.build("joffe2001/playlist-app:${version}", "-f ./src/Dockerfile ./src")
                }
            }
        }

        stage('Create or Find Pull Request') {
            when {
                branch 'issue'
            }
            steps {
                script {
                    withCredentials([string(credentialsId: 'github-token', variable: 'GITHUB_TOKEN')]) {
                        def authHeader = "token ${GITHUB_TOKEN}"
                        
                        // Check if the issue branch exists
                        def branchExists = sh(
                            script: "git ls-remote --heads origin ${env.BRANCH_NAME}",
                            returnStatus: true
                        )

                        if (branchExists != 0) {
                            error "Branch ${env.BRANCH_NAME} does not exist on remote."
                        }

                        // Check if there are changes between issue and master
                        def changes = sh(
                            script: """
                            git diff --name-only origin/${env.MASTER_BRANCH} -- origin/${env.BRANCH_NAME}
                            """,
                            returnStdout: true
                        ).trim()

                        if (changes) {
                            // Check for existing pull request
                            def existingPRResponse = sh(
                                script: """
                                curl -sS -H 'Authorization: ${authHeader}' \
                                -H 'Content-Type: application/json' \
                                https://api.github.com/repos/${GITHUB_REPO}/pulls?head=Joffe2001:${env.BRANCH_NAME}&base=${env.MASTER_BRANCH}
                                """,
                                returnStdout: true
                            ).trim()

                            echo "Existing PR Response: ${existingPRResponse}"

                            def existingPR = readJSON text: existingPRResponse
                            def prNumber = null

                            if (existingPR.size() > 0) {
                                prNumber = existingPR[0].number
                                echo "Found existing PR: ${prNumber}"
                            } else {
                                // Create Pull Request payload
                                def payload = [
                                    title: "Automated Pull Request: ${env.BRANCH_NAME} -> ${env.MASTER_BRANCH}",
                                    body: "Automated pull request created after successful tests on ${env.BRANCH_NAME}.",
                                    head: env.BRANCH_NAME,
                                    base: env.MASTER_BRANCH
                                ]

                                // Send POST request to create pull request
                                def createPRResponse = sh(
                                    script: """
                                    curl -sS -X POST \
                                    -H 'Authorization: ${authHeader}' \
                                    -H 'Content-Type: application/json' \
                                    -d '${groovy.json.JsonOutput.toJson(payload)}' \
                                    https://api.github.com/repos/${GITHUB_REPO}/pulls
                                    """,
                                    returnStdout: true
                                ).trim()

                                echo "Created Pull Request: ${createPRResponse}"

                                // Check for errors in the response
                                if (createPRResponse.contains('"message":')) {
                                    error "Failed to create pull request: ${createPRResponse}"
                                }

                                // Extract pull request number
                                prNumber = sh(script: "echo ${createPRResponse} | grep -oP '\"number\":\\s*\\K\\d+'", returnStdout: true).trim()
                                prNumber = prNumber ?: error("Failed to retrieve pull request number.")
                            }

                            // Merge Pull Request payload
                            def mergePayload = [
                                commit_title: "Merge Pull Request",
                                merge_method: "merge"
                            ]

                            // Send POST request to merge pull request
                            def mergePRResponse = sh(
                                script: """
                                curl -sS -X POST \
                                -H 'Authorization: ${authHeader}' \
                                -H 'Content-Type: application/json' \
                                -d '${groovy.json.JsonOutput.toJson(mergePayload)}' \
                                https://api.github.com/repos/${GITHUB_REPO}/pulls/${prNumber}/merge
                                """,
                                returnStdout: true
                            ).trim()

                            echo "Merged Pull Request: ${mergePRResponse}"

                            // Check for merge errors in the response
                            if (mergePRResponse.contains('"message": "Not Found"')) {
                                error "Failed to merge pull request. Check GitHub repository URL or permissions."
                            }
                        } else {
                            echo "No changes between ${env.BRANCH_NAME} and ${env.MASTER_BRANCH}. Skipping pull request creation."
                        }
                    }
                }
            }
        }

        stage('Push Docker Image and HELM Package') {
            when {
                anyOf {
                    branch 'master'
                    changeset "branches: [${MASTER_BRANCH}]"
                }
            }
            steps {
                script {
                    def version = "v1.${env.BUILD_NUMBER}"
                    docker.withRegistry('https://registry.hub.docker.com', 'docker-joffe-credential') {
                        dockerImage.push(version)
                    }
                    sh "helm package src/helm-chart/ --version ${version}"
                    sh "helm repo index --url https://github.com/${GITHUB_REPO}/tree/master/src/helm-chart/ --merge src/helm-chart/index.yaml"
                    sh "helm push src/helm-chart-${version}.tgz https://github.com/${GITHUB_REPO}/tree/master/src/helm-chart/"
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
                if (env.BRANCH_NAME == env.MASTER_BRANCH) {
                    mail to: 'project-idojoffenevo@gmail.com',
                         subject: "SUCCESS: ${env.JOB_NAME} ${env.BUILD_NUMBER}",
                         body: "The build for ${env.JOB_NAME} ${env.BUILD_NUMBER} was successful."
                }
            }
        }
    }
}