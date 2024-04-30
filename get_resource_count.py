from datetime import datetime, timezone
import boto3
import argparse
import json
import os

# os.environ['AWS_ACCESS_KEY_ID'] = 'ASIA4VTBU4V6STVFTXAF'
# os.environ['AWS_SECRET_ACCESS_KEY'] = 'rZVkqUIwK59BnFs+aVoVj/xx/PwBSUYE1LWR3xe+'
# os.environ['AWS_SESSION_TOKEN'] = 'IQoJb3JpZ2luX2VjEBAaCXVzLXdlc3QtMiJHMEUCIQCDyCOAbOFbbqMsfyeDuxa1FUviEPsfGd1XzB+L94UDzgIgXP05rYoLPNTo9sLsTlqyxYiLzdCbkjdE55j/WJXe4kAq7QQISRAAGgw4NzEwMDk0MTI0NzciDI1EvDwm4OkKqUoPFSrKBOMRSqgiSd1PAYXjo5zxop4wGpMuh5t7r+mMSg0rXrRaCudXOiuCxRCg0jnwDE6lWenV9ttCFZ5Jz7jmZcjMyU67gVV/7XeRtefv+PX5tGZCZ5YyALdb/QOjGjq0nbVQmGlwqlFuzhYkFpV9n02nb2SclpBg+hQd05a/reG3N/BexDsHckPxRA7cB3BzU2KbrqumRNDPahUNdMwQWAhnLnK/KSxPZbVMBXrqmuDcx2TumURi/RemP32N5zss6z2CZK1BbdeieQSYR7WGZ5nHD/MMBjSMmzUQMekaZPtbo0NeHhmUVAuX0Rd3bP28IK+XpkuvUieawp9Uog+yn3zCLTcnsD2Zm5Wvdt/I1Q/+deqOW+nPINholFo7nkat/6w1p8bYonIftIMWt5pmVrm8DuZ9rdqpDhEZVuFGhAfbdAIx/9IHeIeYojzNF9MnKG1NRIm5+TmNJSSy58Xxy7rqzF5YOZN2gHvbKhz15CM897tyQIWcBQPmfO+yKI7e2uATDVnhJ


aws_access_key_id = os.environ['AWS_ACCESS_KEY_ID']
aws_secret_access_key = os.environ['AWS_SECRET_ACCESS_KEY']
aws_session_token = os.environ['AWS_SESSION_TOKEN']

session = boto3.Session(aws_access_key_id, aws_secret_access_key, aws_session_token)

now = datetime.now(timezone.utc)

def check_age(obj, max_age):
    last_modified = obj.last_modified
    delta = now - last_modified
    return delta.days <= int(max_age) # i think thisis wrong, simplify return line and call argparse properly

def print_summary(rum_sum):

    # # Initialize variables for subtotal and grand total
    # org_subtotal = {'billable_resources': 0, 'managed_resources': 0, 'data_resources': 0, 'total_resources': 0}
    # grand_total = {'billable_resources': 0, 'managed_resources': 0, 'data_resources': 0, 'total_resources': 0}

    # for org in rum_sum:
    #     for ws in org['workspaces']:
    #         # Accumulate subtotal for the organization
    #         org_subtotal['billable_resources'] += ws['billable_resources']
    #         org_subtotal['data_resources'] += ws['data_resources']
    #         org_subtotal['managed_resources'] += ws['managed_resources']
    #         org_subtotal['total_resources'] += ws['total_resources']

    #         # Accumulate grand total
    #         grand_total['billable_resources'] += ws['billable_resources']
    #         grand_total['managed_resources'] += ws['managed_resources']
    #         grand_total['data_resources'] += ws['data_resources']
    #         grand_total['total_resources'] += ws['total_resources']

    #     org.update({'organization_total_resources': org_subtotal['total_resources'], 
    #                 'organization_managed_resources': org_subtotal['managed_resources'], 
    #                 'organization_data_resources': org_subtotal['data_resources'], 
    #                 'organization_billable_rum': org_subtotal['billable_resources']})
    #     org_subtotal = {'billable_resources': 0, 'managed_resources': 0, 'data_resources': 0, 'total_resources': 0}

    print(json.dumps(rum_sum))

def get_tf_state_s3(max_age):
    s3 = session.resource('s3')
    bucket = s3.Bucket('lo-pinterest-state')
    resources = []
    rum_sum = []
    for obj in bucket.objects.all():
        if check_age(obj, max_age):
            data = obj.get()['Body'].read().decode('utf-8')
            json_data = json.loads(data)
            resources += json_data['resources']
            rs_sum = {'billable_resources': 0, 'managed_resources': 0, 'data_resources': 0, 'total_resources': 0}
            rs_sum = get_resources(resources)
            rum_sum.append(rs_sum)
        return rum_sum
            # with open('resources.json', 'w') as f:
            #     json.dump(resources, f)
            # for r in json_data['resources']:
            #     print(r['type'])

def get_resources(resources):
    rum = 0
    null_rs = 0
    data_rs = 0
    total = 0
    
    type_counts = {}
    provider_type_counts = {}
    for rs in resources:
        if rs['type'] not in type_counts:
            type_counts[rs['type']] = 0
        type_counts[rs['type']] += 
          

        if rs['provider'] not in provider_type_counts:
          provider_type_counts[rs['provider']] = 0
        provider_type_counts[rs['provider']] += rs['count']

        if rs['provider'] == 'provider[\"registry.terraform.io/hashicorp/null\"]':
            null_rs += rs['count']
        elif rs['type'].startswith("data") or rs['type'] == "terraform_data":
            data_rs += rs['count']
        else:
            rum += rs['count']
    
    return {'billable_resources': rum , 'data_resources': data_rs, 'managed_resources': rum+null_rs, 'total_resources':rum+null_rs+data_rs, 'resource_summary': { 'providers': type_counts, 'provider_types':provider_type_counts}}    


# # def get_tf_state_azure():
# #     pass    # TODO

# # def get_tf_state_gcp():
# #     pass    # TODO  

# # def get_tf_state_local():
# #     pass    # TODO
            


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Script to output basic RUM count."
    )

    parser.add_argument(
        "--max_age",
        default="365",
        help="Set the maximum age of the state files to be considered in days. Default is 365 days.",
    )
    return parser.parse_args()


args = parse_arguments()

rum_sum = get_tf_state_s3(args.max_age)

print_summary(rum_sum)
