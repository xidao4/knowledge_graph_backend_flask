FROM python:3.7
MAINTAINER ykxixi
EXPOSE 5000
COPY ./src /app/src
COPY ./data /app/data
COPY ./start.sh /app/start.sh
COPY ./requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install pip -U
RUN pip config set global.index-url https://pypi.mirrors.ustc.edu.cn/simple
RUN pip3 install -r requirements.txt
ENTRYPOINT ["sh","start.sh"]