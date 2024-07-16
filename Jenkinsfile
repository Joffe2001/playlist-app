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
                sh 'apk add py3-pip jq'
                sh 'jq --version'
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
                branch 'feature' 
            }
            steps {
                script {
                    withCredentials([string(credentialsId: 'github-token', variable: 'GITHUB_TOKEN')]) {
                        def authHeader = "Authorization: token ${GITHUB_TOKEN}"

                        // Check if the feature branch exists
                        def branchExists = sh(
                            script: "git ls-remote --heads origin ${env.BRANCH_NAME}",
                            returnStatus: true
                        )

                        if (branchExists != 0) {
                            error "Branch ${env.BRANCH_NAME} does not exist on remote."
                        }

                        // Check if there are changes between feature and master
                        def changes = sh(
                            script: """
                            git fetch origin
                            git diff --name-only origin/${env.MASTER_BRANCH}..origin/${env.BRANCH_NAME}
                            """,
                            returnStdout: true
                        ).trim()

                        echo "Changes:\n${changes}"

                        if (changes) {
                            // Check for existing pull request
                            def existingPRResponse = sh(
                                script: """
                                curl -sS -H "$authHeader" \
                                -H "Content-Type: application/json" \
                                "https://api.github.com/repos/${GITHUB_REPO}/pulls?head=Joffe2001:${env.BRANCH_NAME}&base=${env.MASTER_BRANCH}"
                                """,
                                returnStdout: true
                            ).trim()

                            echo "Existing PR Response: ${existingPRResponse}"

                            def existingPR = []
                            if (existingPRResponse) {
                                try {
                                    existingPR = new groovy.json.JsonSlurper().parseText(existingPRResponse)
                                } catch (Exception e) {
                                    error "Failed to parse existing PR response: ${e.message}\nResponse: ${existingPRResponse}"
                                }
                            } else {
                                echo "No existing pull request found."
                            }
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

                                def payloadJson = groovy.json.JsonOutput.toJson(payload)

                                // Send POST request to create pull request
                                def createPRResponse = sh(
                                    script: """
                                    curl -sS -X POST \
                                    -H "$authHeader" \
                                    -H "Content-Type: application/json" \
                                    -d '${payloadJson}' \
                                    "https://api.github.com/repos/${GITHUB_REPO}/pulls"
                                    """,
                                    returnStdout: true
                                ).trim()

                                echo "Create PR Response: ${createPRResponse}"

                                def createdPR = null
                                try {
                                    createdPR = new groovy.json.JsonSlurper().parseText(createPRResponse)
                                } catch (Exception e) {
                                    error "Failed to parse create PR response: ${e.message}\nResponse: ${createPRResponse}"
                                }

                                if (createdPR?.message == "Validation Failed") {
                                    def errorMessage = createdPR.errors?.find { it.message }?.message
                                    if (errorMessage?.contains("A pull request already exists")) {
                                        def prInfoResponse = sh(
                                            script: """
                                            curl -sS -H "$authHeader" \
                                            -H "Content-Type: application/json" \
                                            "https://api.github.com/repos/${GITHUB_REPO}/pulls?head=Joffe2001:${env.BRANCH_NAME}&base=${env.MASTER_BRANCH}"
                                            """,
                                            returnStdout: true
                                        ).trim()

                                        def prInfo = new groovy.json.JsonSlurper().parseText(prInfoResponse)
                                        prNumber = prInfo[0].number
                                        echo "PR already exists: ${prNumber}"
                                    } else {
                                        error "Failed to create pull request: ${createdPR.message}"
                                    }
                                } else {
                                    prNumber = createdPR?.number
                                    if (!prNumber) {
                                        error "Failed to retrieve pull request number from response: ${createPRResponse}"
                                    }
                                    echo "Created Pull Request: ${prNumber}"
                                }
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
                beforeAgent true
                changeset "branches: [${MASTER_BRANCH}]"
                branch MASTER_BRANCH
            }
            steps {
                script {
                    def version = "v1.${env.BUILD_NUMBER}"
                    sh "helm package helm-chart/ --version ${version}"
                    sh "helm repo index --url https://github.com/${GITHUB_REPO}/tree/master/helm-chart/ --merge helm-chart/index.yaml"
                    sh "helm push helm-chart-${version}.tgz https://github.com/${GITHUB_REPO}/tree/master/helm-chart/"
                    docker.withRegistry('https://registry.hub.docker.com', 'dockerhub-credentials') {
                        sh "helm package helm-chart/ --version ${version}"
                        sh "helm repo index --url https://github.com/${GITHUB_REPO}/tree/master/helm-chart/ --merge helm-chart/index.yaml"
                        sh "helm push helm-chart-${version}.tgz https://github.com/${GITHUB_REPO}/tree/master/helm-chart/"
                    }
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