pipeline {
    agent any

    environment {
        DOCKERHUB_USER = 'jaipal9669'
        IMAGE_NAME = 'metal-price-app'
    }

    stages {
        stage('Clone Repository') {
            steps {
                git branch: 'master', url: 'https://github.com/jaipalreddyp1072/metal-app.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                echo '🐳 Building Docker image...'
                script {
                    sh 'docker build -t ${DOCKERHUB_USER}/${IMAGE_NAME}:latest .'
                }
            }
        }

        stage('Login to Docker Hub') {
            steps {
                echo '🔐 Logging in to Docker Hub...'
                withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', usernameVariable: 'USERNAME', passwordVariable: 'PASSWORD')]) {
                    sh 'echo $PASSWORD | docker login -u $USERNAME --password-stdin'
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                echo '📤 Pushing image to Docker Hub...'
                sh 'docker push ${DOCKERHUB_USER}/${IMAGE_NAME}:latest'
            }
        }

        stage('Deploy on Same VM') {
            steps {
                echo '🚀 Deploying container on same VM...'
                script {
                    sh """
                        docker run -d -p 5000:5000 --name metal-price-app ${DOCKERHUB_USER}/${IMAGE_NAME}:latest || true
                    """
                }
            }
        }
    }

    post {
        success {
            echo '✅ Deployment successful!'
        }
        failure {
            echo '❌ Build or deployment failed.'
        }
    }
}
