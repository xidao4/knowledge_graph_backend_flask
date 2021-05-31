pipeline {
    agent none
    environment {
        registryUrl= "registry.cn-hangzhou.aliyuncs.com"
        registryUrlVpc = "registry-vpc.cn-hangzhou.aliyuncs.com"
        registry_user= "ykxixi01"
        registry_pass= "1368xixideRegis"
        namespace="super-sec3"
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
                sh "docker build . -t ${image_name}:${BUILD_ID}"
            }
        }
        stage('Image Push'){
            agent{
                label 'master'
            }
            steps{
                echo 'Image Push Stage'
                sh 'docker login  --username=${registry_user} --password=${registry_pass} ${registryUrl}'
                sh "docker tag ${image_name}:${BUILD_ID} ${registryUrl}/${namespace}/${image_name}:${BUILD_ID}"
                sh "docker push ${registryUrl}/${namespace}/${image_name}:${BUILD_ID}"
            }
        }
        stage('deploy'){
            agent{
                label 'ydlServer'
            }
            steps{
                sh 'docker login  --username=${registry_user} --password=${registry_pass} ${registryUrl}'
                sh 'docker pull ${registryUrlVpc}/${namespace}/${image_name}:${BUILD_ID}'
                sh "if (ps -ef| grep java|grep ${container_name}) then (docker stop ${container_name} && docker rm ${container_name}) fi"
                sh "docker run -p 5000:5000 --name ${container_name} -v /log:/log -d ${registryUrlVpc}/${namespace}/${image_name}:${BUILD_ID}"
            }
        }
    }
}