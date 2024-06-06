import json



def lambda_handler(event, context):

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "I remember you was conflicted, misusing your influence, sometimes I did the same, abusing my power full of resentment, resentment that turned into a deep depression, found myself screaming in the hotel room, I didn't wanna self destruct, the evils of Lucy was all around me, so I went running for answers",

        }),
    }
