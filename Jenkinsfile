
pipeline {
    agent any

    stages {
        stage('Verify Python') {
            steps {
                bat 'py --version'
                bat 'git --version'
            }
        }

        stage('Create CI Environment') {
            steps {
                bat 'if exist .venv-ci rmdir /s /q .venv-ci'
                bat 'py -m venv .venv-ci'
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
            echo 'SUCCESS: Version 1 tests passed.'
        }

        failure {
            echo 'FAILURE: Check the Jenkins Console Output.'
        }

        always {
            echo 'Version 1 CI pipeline execution completed.'
        }
    }
}
