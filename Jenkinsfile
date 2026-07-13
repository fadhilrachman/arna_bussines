pipeline {
  agent any

  environment {
    IMAGE_NAME = "arnatechid/arna-business-hub:${BUILD_NUMBER}"
  }

  stages {
    stage("Install") {
      steps {
        sh "python -m venv .venv"
        sh ". .venv/bin/activate && pip install -r requirements.txt"
      }
    }

    stage("Check") {
      steps {
        sh ". .venv/bin/activate && cd source && python manage.py check"
        sh ". .venv/bin/activate && pytest"
      }
    }

    stage("Build Image") {
      steps {
        sh "docker build -t ${IMAGE_NAME} ."
      }
    }
  }
}
