
pipeline {
    agent any

    environment {
        PYTHON = 'C:/Users/PRETHISH/AppData/Local/Programs/Python/Python314/python.exe'
        DOCKER = 'C:/Users/PRETHISH/AppData/Local/Programs/DockerDesktop/resources/bin/docker.exe'
        DOCKERHUB_REPOSITORY = 'prethish1601/time-tracker'
    }

    stages {
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
                bat '"%DOCKER%" build -t time-tracker:v2 .'
                bat '"%DOCKER%" tag time-tracker:v1 %DOCKERHUB_REPOSITORY%:v2'
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

                    bat '"%DOCKER%" push %DOCKERHUB_REPOSITORY%:v2'

                    bat '"%DOCKER%" logout'
                }
            }
        }
    }

    post {
        success {
            eecho 'SUCCESS: Tests passed, Docker image built, and v2 pushed to Docker Hub.'
        }

        failure {
            echo 'FAILURE: Check Console Output to identify the failed stage.'
        }

        always {
            echo 'Version 1 CI/CD pipeline execution completed.'
        }
    }
}
