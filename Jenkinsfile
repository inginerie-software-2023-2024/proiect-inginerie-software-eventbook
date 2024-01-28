pipeline {
    agent any
    stages {
        stage('Checkout') {
            steps {
                checkout([$class: 'GitSCM', branches: [[name: '*/test']],
                         userRemoteConfigs: [[url: 'https://github.com/inginerie-software-2023-2024/proiect-inginerie-software-eventbook',
                         credentialsId: '123']]])
            }
        }
        // Other stages...
    }
}
