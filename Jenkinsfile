pipeline {
    agent {
        kubernetes {
            yaml '''
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: sonar-scanner
    image: sonarsource/sonar-scanner-cli
    command: ["cat"]
    tty: true

  - name: kubectl
    image: bitnami/kubectl:latest
    command: ["cat"]
    tty: true
    securityContext:
      runAsUser: 0
      readOnlyRootFilesystem: false
    env:
    - name: KUBECONFIG
      value: /kube/config
    volumeMounts:
    - name: kubeconfig-secret
      mountPath: /kube/config
      subPath: kubeconfig

  - name: dind
    image: docker:dind
    securityContext:
      privileged: true
    env:
    - name: DOCKER_TLS_CERTDIR
      value: ""
    volumeMounts:
    - name: docker-config
      mountPath: /etc/docker/daemon.json
      subPath: daemon.json

  volumes:
  - name: docker-config
    configMap:
      name: docker-daemon-config

  - name: kubeconfig-secret
    secret:
      secretName: kubeconfig-secret
'''
        }
    }

    stages {

        stage('Build Backend & Frontend Image') {
            steps {
                container('dind') {
                    sh '''
                        echo "Building Docker image (Django Backend + HTML Frontend)..."
                        sleep 10
                        docker build -t fraudbuster:latest .
                        docker image ls
                    '''
                }
            }
        }

        stage('SonarQube Analysis') {
            steps {
                container('sonar-scanner') {
                    withCredentials([string(credentialsId: 'FraudBuster', variable: 'sqb_b10899b4a8e30cc3051eeb8fac5751c8a925172e')]) {
                        sh '''
                            sonar-scanner \
                                -Dsonar.projectKey=fraudbuster \
                                -Dsonar.host.url=http://my-sonarqube-sonarqube.sonarqube.svc.cluster.local:9000 \
                                -Dsonar.login=$SONAR_TOKEN \
                                -Dsonar.sources=./ \
                                -Dsonar.exclusions=**/venv/**,**/__pycache__/**,**/staticfiles/**,**/static/**
                        '''
                    }
                }
            }
        }

        stage('Login to Docker Registry') {
            steps {
                container('dind') {
                    sh '''
                        docker --version
                        sleep 10
                        docker login nexus-service-for-docker-hosted-registry.nexus.svc.cluster.local:8085 -u admin -p Changeme@2025
                    '''
                }
            }
        }

        stage('Tag & Push Image') {
            steps {
                container('dind') {
                    sh '''
                        echo "Tagging image..."
                        docker tag fraudbuster:latest nexus-service-for-docker-hosted-registry.nexus.svc.cluster.local:8085/anis-project/fraudbuster:latest

                        echo "Pushing image..."
                        docker push nexus-service-for-docker-hosted-registry.nexus.svc.cluster.local:8085/anis-project/fraudbuster:latest

                        docker image ls
                    '''
                }
            }
        }

        stage('Deploy FraudBuster Application') {
            steps {
                container('kubectl') {
                    script {
                        dir('k8s') {
                            sh '''
                                echo "Applying Kubernetes deployment..."
                                kubectl apply -f fraudbuster-deployment.yaml
                                kubectl apply -f fraudbuster-service.yaml
                                kubectl apply -f ingress.yaml
                            '''
                        }
                    }
                }
            }
        }
    }
}
