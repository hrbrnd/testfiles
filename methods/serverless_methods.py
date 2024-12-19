from methods.aws_methods import get_credentials

def get_all_lambda_functions(aws_profile, regions):


    lambda_details = []

    for region in regions:
        lambda_client = get_credentials(aws_profile, region, service= "lambda")
        paginator = lambda_client.get_paginator('list_functions')
        
        page_iterator = paginator.paginate()
        
        for page in page_iterator:
            for function in page['Functions']:
                function_arn = function['FunctionArn']
                function_details = lambda_client.get_function(FunctionName=function_arn)
                
                tags = lambda_client.list_tags(Resource=function_arn).get('Tags', {})
                
                row = {
                    region,
                    function['FunctionName'],
                    function['Runtime'],
                    function['Handler'],
                    function['Role'],
                    function['CodeSize'],
                    function.get('Description', 'N/A'),
                    function['Timeout'],
                    function['MemorySize'],
                    function['LastModified'],
                    tags
                }
                
                lambda_details.append(row)
    
    return lambda_details