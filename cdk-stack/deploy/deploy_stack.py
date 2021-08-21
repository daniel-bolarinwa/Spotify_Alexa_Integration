from aws_cdk import Stack
from constructs import Construct
import aws_cdk.aws_lambda as Lambda
import aws_cdk.aws_iam as iam

class DeployStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        fn = Lambda.Function(self, "Spotify_Alexa_Function",
            runtime=Lambda.Runtime.PYTHON_3_8,
            handler="index.handler",
            code=Lambda.Code.from_asset(path.join(__dirname, "lambda-handler"))
        )
        
