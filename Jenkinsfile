
pipeline {
    agent any

    options {
        skipDefaultCheckout(true)
    }

    parameters {
        choice(
            name: 'VERSION',
            choices: ['v1', 'v2', 'v3'],
            description: 'Select the Time Tracker version to build'
        )
    }

    environment {
        PYTHON = 'C:/Users/PRETHISH/AppData/Local/Programs/Python/Python314/python.exe'
        DOCKER = 'C:/Users/PRETHISH/AppData/Local/Programs/DockerDesktop/resources/bin/docker.exe'
        DOCKERHUB_REPOSITORY = 'prethish1601/time-tracker'
    }

    stages {
        stage('Checkout Selected Version') {
            steps {
                script {
                    def sourceBranch =
                        params.VERSION == 'v1' ? 'main' : params.VERSION

                    echo "Building ${params.VERSION} from branch ${sourceBranch}"

                    deleteDir()

                    checkout([
                        $class: 'GitSCM',
                        branches: [[name: "*/${sourceBranch}"]],
                        userRemoteConfigs: [[
                            url: 'https://github.com/Prethish16/time_tracker'
                        ]]
                    ])
                }
            }
        }

        stage('Verify Tools') {
            steps {
                bat '"%PYTHON%" --version'
                bat 'git --version'
                bat '"%DOCKER%" --version'
                bat '"%DOCKER%" info'
            }
        }

        stage('Create CI Environment') {
            steps {
                bat 'if exist .venv-ci rmdir /s /q .venv-ci'
                bat '"%PYTHON%" -m venv .venv-ci'
                bat '.venv-ci\\Scripts\\python.exe -m pip install --upgrade pip'
                bat '.venv-ci\\Scripts\\python.exe -m pip install -r requirements.txt'
            }
        }

        stage('Run Automated Tests') {
            steps {
                bat '.venv-ci\\Scripts\\python.exe -m pytest -v'
            }
        }

        stage('Build Docker Image') {
            steps {
                bat '"%DOCKER%" build -t time-tracker:%VERSION% .'
                bat '"%DOCKER%" tag time-tracker:%VERSION% %DOCKERHUB_REPOSITORY%:%VERSION%'
            }
        }

        stage('Push to Docker Hub') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-creds',
                        usernameVariable: 'DOCKERHUB_USERNAME',
                        passwordVariable: 'DOCKERHUB_PASSWORD'
                    )
                ]) {
                    bat 'powershell -NoProfile -NonInteractive -ExecutionPolicy Bypass -Command "$env:DOCKERHUB_PASSWORD | & $env:DOCKER login --username $env:DOCKERHUB_USERNAME --password-stdin"'

                    bat '"%DOCKER%" push %DOCKERHUB_REPOSITORY%:%VERSION%'

                    bat '"%DOCKER%" logout'
                }
            }
        }
    }

    post {
        success {
            echo "SUCCESS: ${params.VERSION} tests passed and Docker image was pushed."
        }

        failure {
            echo 'FAILURE: Check the failed stage in Console Output.'
        }

        always {
            echo 'Time Tracker CI/CD pipeline execution completed.'
        }
    }
}
