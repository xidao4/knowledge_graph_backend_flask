FROM python:3.7
MAINTAINER ykxixi
EXPOSE 5000
COPY ./src /app/src
COPY ./data /app/data
COPY ./start.sh /app/start.sh
COPY ./requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
ENTRYPOINT ["sh","start.sh"]