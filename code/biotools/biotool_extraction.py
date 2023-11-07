import requests
import os
import csv
import json
from openai import OpenAI
import argparse

parser = argparse.ArgumentParser(description='parse biotools projects and convert them into csv table entries')
parser.add_argument('--dry_run', type=bool, default=False, help='dont write the output file if False')
parser.add_argument('--max_entries', type=int, default=None, help='Max number of entries to convert')
parser.add_argument('--output_file_name', type=str, default="test", help='Max number of entries to convert')
parser.add_argument('--use_gpt', type=bool, default=True, help='wether to use chat_gpt to create input and output descriptions')
parser.add_argument('--gpt_api_key', type=str, default="", help='valid chat_gpt api key that can use gpt3_turbo')
parser.add_argument('--collection_id', type=str, default="Rare Disease", help='collection_id for the biotools query')

args = parser.parse_args()

url = "https://bio.tools/api/t/"

output_file_name = args.output_file_name + ".csv"

use_gpt = args.use_gpt

dry_run = args.dry_run

gpt_api_key = args.gpt_api_key

max_entries = 10000
if max_entries is not None:
    max_entries = args.max_entries

openai = OpenAI(
        api_key=gpt_api_key
)

def promt_a(content, io):
    return f"Given this information: \"{content}\" can you create a {io} description  (1-3 not too long sentences)   of the described application. Write nothing else then the description itself"


def openai_query(content, io):
    msg = promt_a(content, io)
    chat_completion = openai.chat.completions.create(
    messages=[
            {
                "role": "user",
                "content": msg
            }
        ],
        model="gpt-3.5-turbo",
    )

    result = chat_completion.choices[0].message.content
    return result


if os.path.exists(output_file_name) and not dry_run:
    print(f"deleting old output file {output_file_name}")
    os.remove(output_file_name)

headers = {
    'Accept': 'application/json',  # Tells the server that the client expects JSON
}

params = {
    'collectionID': args.collection_id
}

github_counter = 0

csv_headers = ["name", "URL", "description", "Task", "Input Nature", "Output Nature", "license", "Topic","Input Format", "Output Format","Input Description", "Output Description"]

def processs_json_entry(json_item):
    operations = []
    inputs = []
    input_formats = []
    output_formats = []
    outputs = []
    topic = []

    if 'topic' in json_item:
        topic.extend([op['term'] for op in json_item['topic'] if 'term' in op])

    # Extract the operations if they exist.
    if 'function' in json_item:
        for function in json_item['function']:
            if 'operation' in function:
                operations.extend([op['term'] for op in function['operation'] if 'term' in op])
            
            # Extract the inputs if they exist.
            if 'input' in function:
                inputs.extend([inp['data']['term'] for inp in function['input'] if 'data' in inp and 'term' in inp['data']])
                input_formats.extend([inp['format'][0]['term'] for inp in function['input'] if 'format' in inp and len(inp['format']) > 0 and 'term' in inp['format'][0]])
            
            # Extract the outputs if they exist.
            if 'output' in function:
                outputs.extend([out['data']['term'] for out in function['output'] if 'data' in out and 'term' in out['data']])
                output_formats.extend([out['format'][0]['term'] for out in function['input'] if 'format' in out and len(out['format']) > 0 and 'format' in out['format'][0]])
    
    # If lists are empty, set them to None.
    operations = "\n".join(operations) if operations else None
    inputs = "\n".join(inputs) if inputs else None
    input_formats = "\n".join(input_formats) if input_formats else None
    output_formats = "\n".join(output_formats) if output_formats else None
    outputs = "\n".join(outputs) if outputs else None
    topic = topic[0] if topic and len(topic) > 0 else None
    
    url = json_item.get('homepage', '')
    if 'download' in json_item and len(json_item['download']) > 0:
        url = json_item.get('download', '')[0].get('url','')

    name = json_item.get('name', '')
    description = json_item.get('description', '')
    license = json_item.get('license', '')

    input_description = ""
    output_description = ""
    desc = f"name = {name} ; description = {description} ; input = {inputs} ; output = {outputs} ; task = {operations}"
    if use_gpt:
        input_description = openai_query(desc, "input")
        output_description = openai_query(desc, "output")


    result = {
        'name': name,
        'URL': url,
        'description': description,
        'license': license,
        'Input Nature': inputs,
        'Output Nature': outputs,
        'Input Format': input_formats,
        'Output Format': output_formats,
        'Task': operations,
        'Topic': topic,
        'Input Description' : input_description,
        'Output Description' : output_description,
    }

    return result

converted_counter = 0
with open(output_file_name, mode='w', newline='', encoding='utf-8') as file:
    if not dry_run:
        csv_writer = csv.DictWriter(file, fieldnames=csv_headers)
        csv_writer.writeheader()
    done = False
    while not done:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            try:
                data = response.json()
        
                
                if 'list' in data and len(data['list']) > 0:
                        for item in data['list']:
                            # print(f"process entry {converted_counter}")
                            csv_entry = processs_json_entry(item)
                            if not dry_run:
                                csv_writer.writerow(csv_entry)
                            converted_counter = converted_counter + 1
                            if converted_counter == max_entries:
                                print(f"reached desired amount of {converted_counter} entries")
                                done = True
                                break
        
                # Break out of the loop if there is no "next" page.
                if 'next' not in data or not data['next']:
                    done = True
                else: 
                    next_page_url = data['next']
                    if next_page_url.startswith('?'):
                        url = "https://bio.tools/api/tool/" + next_page_url
                        print(f"going to page {next_page_url}")
                    else:
                        url = next_page_url
            
                
               
                
            except json.JSONDecodeError as e:
                
                print("JSON Decode Error: ", e)
                print("Response content: ", response.text)
        else:
            print(f"Failed to retrieve data: {response.status_code}")
