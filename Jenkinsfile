pipeline {
    agent none
    environment {
        registryUrl= "registry.cn-hangzhou.aliyuncs.com"
        registry_user= "ykxixi01"
        repo_url="sec3"
        image_name = "backend-coin-flask"
        container_name = "backend-coin-flask"
    }

    stages {
        stage('Image Build'){
            agent{
                label 'master'
            }
            steps{
                echo 'Image Build Stage'
                sh "docker build . -t backend-coin-flask:${BUILD_ID}"
            }
        }
        stage('Image Push'){
            agent{
                label 'master'
            }
            steps{
                echo 'Image Push Stage'
                sh 'docker login  --username=${registry_user} ${registryUrl}'
                sh "docker tag backend-coin-flask:${BUILD_ID} ${registryUrl}/${repo_url}/${image_name}:${BUILD_ID}"
                sh "docker push ${registryUrl}/${repo_url}/${image_name}:${BUILD_ID}"
            }
        }
        stage('deploy'){
            agent{
                label 'ydlServer'
            }
            steps{
                sh 'docker login  --username=${registry_user} ${registryUrl}'
                sh 'docker pull ${registryUrl}/${repo_url}/${image_name}:${BUILD_ID}'
                sh "if (ps -ef| grep java|grep ${container_name}) then (docker stop ${container_name} && docker rm ${container_name}) fi"
                sh "docker run -p 5000:5000 --name ${container_name} -v /log:/log -d ${registryUrl}/${repo_url}/${image_name}:${BUILD_ID}"
            }
        }
    }
}