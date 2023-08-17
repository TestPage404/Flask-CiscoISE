FROM python:3.11-slim
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt --trusted-host pypi.org --trusted-host files.pythonhosted.org
EXPOSE 5000
CMD python ./main.py