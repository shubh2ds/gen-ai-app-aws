# py
import boto3
import botocore.config
import json

from datetime import datetime
"""
{"modelId":"meta.llama3-2-1b-instruct-v1:0",
"contentType":"application/json",
"accept":"application/json",
"body":{"inputs":[[{"role":"user","content":"Tell me about Paris"},
{"role":"assistant","content":"Paris is a city in France."},{"role":"user","content":"Is it the biggest city in France?"}]],"parameters":{"max_new_tokens":512,"top_p":0.9,"temperature":0.6}}}
"""

"""
{"modelId":"meta.llama3-2-3b-instruct-v1:0","contentType":"application/json","accept":"application/json","body":{"inputs":[[{"role":"user","content":"Tell me about Paris"},{"role":"assistant","content":"Paris is a city in France."},{"role":"user","content":"Is it the biggest city in France?"}]],"parameters":{"max_new_tokens":512,"top_p":0.9,"temperature":0.6}}}
"""

#"meta.llama2-13b-chat-v1
def blog_generate_using_bedrock(blogtopic:str)-> str:
    prompt=f"""<s>[INST]Human: Write a 200 words blog on the topic {blogtopic}
    Assistant:[/INST]
    """

    body={
        "prompt":prompt,
        "max_gen_len":512,
        "temperature":0.5,
        "top_p":0.9
    }

    try:
        bedrock=boto3.client("bedrock-runtime",region_name="us-east-1",
                             config=botocore.config.Config(read_timeout=300,retries={'max_attempts':3}))
        response=bedrock.invoke_model(body=json.dumps(body),modelId="meta.llama3-2-3b-instruct-v1:0")

        response_content=response.get('body').read()
        response_data=json.loads(response_content)
        print(response_data)
        blog_details=response_data['generation']
        return blog_details
    except Exception as e:
        print(f"Error generating the blog:{e}")
        return ""

def save_blog_details_s3(s3_key,s3_bucket,generate_blog):
    s3=boto3.client('s3')
    try:
        s3.put_object(Bucket = s3_bucket, Key = s3_key, Body =generate_blog )
        print("Code saved to s3")

    except Exception as e:
        print("Error when saving the code to s3")



def lambda_handler(event, context):
    # TODO implement
    event=json.loads(event['body'])
    blogtopic=event['blog_topic']

    generate_blog=blog_generate_using_bedrock(blogtopic=blogtopic)

    if generate_blog:
        current_time=datetime.now().strftime('%H%M%S')
        s3_key=f"blog-output/{current_time}.txt"
        s3_bucket='awsbedrockbucket001'
        save_blog_details_s3(s3_key,s3_bucket,generate_blog)


    else:
        print("No blog was generated")

    return{
        'statusCode':200,
        'body':json.dumps('Blog Generation is completed')
    }

blogtopic = "cricket"
generate_blog=blog_generate_using_bedrock(blogtopic=blogtopic)
generate_blog