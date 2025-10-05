FROM public.ecr.aws/lambda/python:3.9

COPY . ${LAMBDA_TASK_ROOT}
COPY requirements.txt .

RUN pip install -r requirements.txt

CMD ["lambda_function.lambda_handler"]