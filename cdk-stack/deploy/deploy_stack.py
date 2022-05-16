from aws_cdk import Stack
from constructs import Construct
import aws_cdk.aws_lambda as Lambda
import aws_cdk.aws_iam as iam
import aws_cdk.aws_secretsmanager as secretsmanager

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

        fn.add_to_role_policy(iam.PolicyStatement(
            actions=["secretsmanager:*"],
            resources=["arn:aws:secretsmanager:*:947331989401:secret:*"]
        ))

        secretsmanager.Secret(self, "auth_token_secret",
            secret_name="spotify_access_token",
            description="access token which the apps needs to perform its operations"
        )

        secretsmanager.Secret(self, "auth_refresh_token_secret",
            secret_name="spotify_access_refresh_token",
            description="refresh token which the apps needs to regenerate the access token when it expires"
        )
        
