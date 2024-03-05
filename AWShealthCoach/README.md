Deployment steps

Make changes, save your code, then run these two commands:

$ sam build
$ sam deploy


NOTE: the open ai api key in template.yaml is expired. Please use your valid API key from the .env for deployment
DO NOT PUSH templat.yaml TO GITHUB WITH A VALID OPENAI API KEY IN IT

This can be fixed with sam variables in deployment, but it wasn't working for me so we'll leave it for now.