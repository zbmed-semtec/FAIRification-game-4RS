Python script to convert software artefacts listed on [https://bio.tools](https://bio.tools) into a a csv table

## Arguments

```bash
$ python biotool_extraction.py --help
usage: crawl.py [-h] [--dry_run DRY_RUN] [--max_entries MAX_ENTRIES] [--output_file_name OUTPUT_FILE_NAME]
                [--use_gpt USE_GPT] [--collection_id COLLECTION_ID]

parse biotools projects and convert them into csv table entries

options:
  -h, --help            show this help message and exit
  --dry_run DRY_RUN     dont write the output file if False
  --max_entries MAX_ENTRIES
                        Max number of entries to convert
  --output_file_name OUTPUT_FILE_NAME
                        Max number of entries to convert
  --use_gpt USE_GPT     wether to use chat_gpt to create input and output descriptions
  --collection_id COLLECTION_ID
                        collection_id for the biotools query
```


## Output

the script creates a *csv* file called *{output_file_name}.csv*. If *dry_run* is set, no output file is produced. If *use_gpt* is set, a chatgpt api key has to be provided in *gpt_api_key*
