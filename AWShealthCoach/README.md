Deployment steps

Make changes, save your code, then run these two commands:

$ sam build
$ sam deploy --guided --parameter-overrides OpenAIApiKey=<your_openai_api_key_here>

Get the open api key from your .env.
AWS SAM does not allow the use of variables from in the .env.