from methods.aws_methods import get_credentials

def get_lambda(aws_profile, regions):
    """Get all load balancers (Afunction and Nfunction) in the specified region."""
    lambda_details = []

    for region in regions:
        lambda_client = get_credentials(aws_profile, region, service="lambda")
        paginator = lambda_client.get_paginator("list_functions")
        for page in paginator.paginate():
            for function in page['Functions']:
                print(function)
    #             row = [
    #                 region,
    #                 function['LoadBalancerName'],
    #                 function['DNSName'],
    #                 function['CreatedTime'],
    #                 function['Type'],
    #                 function['State']['Code'],
    #                 function.get('Tags', [])
    #             ]
    #             lambda_details.append(row)
    # return lambda_details    