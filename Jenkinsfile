
pipeline {
    agent any

    environment {
        PYTHON = 'C:/Users/PRETHISH/AppData/Local/Programs/Python/Python314/python.exe'
    }

    stages {
        stage('Verify Python and Git') {
            steps {
                bat '"%PYTHON%" --version'
                bat 'git --version'
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
    }

    post {
        success {
            echo 'SUCCESS: All Version 1 tests passed.'
        }

        failure {
            echo 'FAILURE: Check the Console Output for the error.'
        }

        always {
            echo 'Version 1 CI pipeline execution completed.'
        }
    }
}
