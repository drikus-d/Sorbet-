from lambda_function import lambda_handler

# Simulated test input
event = {
    "key1": "value1"  # whatever input your function expects
}
context = {}  # Can be empty or mocked if needed

# Run the lambda function
response = lambda_handler(event, context)

print(response)