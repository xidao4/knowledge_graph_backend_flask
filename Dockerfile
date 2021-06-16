FROM python:3.7
MAINTAINER ykxixi
EXPOSE 5000
COPY ./requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install pip -U
RUN pip config set global.index-url https://pypi.mirrors.ustc.edu.cn/simple
#RUN pip3 install -r requirements.txt
RUN pip install py2neo==4.3.0
RUN pip install pandas
RUN pip install Flask
RUN pip install jieba
RUN pip install scikit_learn
RUN pip install kanren
COPY ./src /app/src
COPY ./data /app/data
COPY ./start.sh /app/src/start.sh
WORKDIR /app/src
ENTRYPOINT ["sh","start.sh"]