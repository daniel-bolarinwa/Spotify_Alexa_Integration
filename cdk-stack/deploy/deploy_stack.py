from aws_cdk import Stack
from constructs import Construct
import aws_cdk.aws_lambda as Lambda
import aws_cdk.aws_iam as iam

class DeployStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        fn = Lambda.Function(self, "Spotify_Alexa_Function",
            runtime=Lambda.Runtime.PYTHON_3_8,
            handler="run.lambda_handler",
            code=Lambda.Code.from_asset("../spotify-service")
        )

        fn.add_permission('alexa-invocation-trigger',
            principal=iam.ServicePrincipal('alexa-appkit.amazon.com'),
            action='lambda:InvokeFunction'
        )
        
