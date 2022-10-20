FROM amazon/aws-lambda-python:3.8

ARG FUNCTION_DIR="/var/task"

RUN mkdir -p ${FUNCTION_DIR}

# Copy function code
COPY src/ ${FUNCTION_DIR}/src
COPY products/products.py ${FUNCTION_DIR}

# Copy requirements
COPY requirements.txt ${FUNCTION_DIR}

# Install the function's dependencies using file requirements.txt
# from your project folder.
RUN pip3 install --upgrade pip
RUN pip3 install -r ${FUNCTION_DIR}/requirements.txt

CMD [ "products.main" ]