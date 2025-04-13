# thebathroomwall
Serverless Anonymous Message Wall. 

This is my attempt at capturing the magic of latrinalia (bathroom graffiti) using AWS Lambda, API Gateway, S3, DynamoDB, CloudFront, and SAM. The frontend lives in a private S3 bucket and is served securely via CloudFront/OAC. The backend is powered by three Lambda functions (post message, get message, and a cleanup function) and three DynamoDB tables (one storing the messages, an index table for scalability, and a table that integrates with the post message Lambda to handle rate limiting). This project demonstrates best practices in modern cloud architectures and showcases my ability to design, deploy, optimize, and troubleshoot production-grade serverless solutions.

To Use:
  1) Deploy the infrastructure with SAM.
  2) Run the deploy_frontend.sh script to inject correct endpoints into the html and upload to the S3 bucket.
  3) Set up your DNS if you want.
  4) Have fun.

A cron job runs nightly to get rid of naughty messages. 

TODO: 
There are a few things I need to still do with this. Namely, for some reason I designed the python message function to accept and remove naughty words but it would make more sense just to not take them at all.

This can be better scaled by decoupling the Lambda and the DynamoDBs with SQS.

