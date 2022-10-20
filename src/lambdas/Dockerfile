FROM amazon/aws-lambda-python:3.8

ARG FUNCTION_DIR="/var/task"

RUN mkdir -p ${FUNCTION_DIR}

# Copy function code
COPY app/ ${FUNCTION_DIR}/app
COPY lambdas/handler.py ${FUNCTION_DIR}

# Copy requirements
COPY lambdas/requirements.txt ${FUNCTION_DIR}

# Install the function's dependencies using file requirements.txt
# from your project folder.
RUN pip3 install --upgrade pip
RUN pip3 install -r ${FUNCTION_DIR}/requirements.txt

CMD [ "handler.main" ]