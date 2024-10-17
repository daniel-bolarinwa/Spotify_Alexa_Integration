from aws_cdk import Stack
import aws_cdk
from constructs import Construct
import aws_cdk.aws_lambda as Lambda
import aws_cdk.aws_iam as iam
import aws_cdk.aws_ssm as ssm
import aws_cdk.aws_secretsmanager as secretsmanager

class DeployStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        alexa_skill_id = ssm.StringParameter.from_string_parameter_name(self, "Alexa Skill ID",
            string_parameter_name="alexa_skill_id"
        ).string_value

        fnLayer = Lambda.LayerVersion(self, "External Packages Layer",
            compatible_runtimes=[Lambda.Runtime.PYTHON_3_8],
            description="Layer that houses the requests and ask-sdk-core packages",
            code=Lambda.Code.from_asset("../spotify-service/alexa_spotify_app/layers")
        )

        fn = Lambda.Function(self, "Spotify_Alexa_Function",
            runtime=Lambda.Runtime.PYTHON_3_8,
            handler="lambda_function.lambda_handler",
            code=Lambda.Code.from_asset("../spotify-service/alexa_spotify_app/src"),
            layers=[fnLayer],
            timeout=aws_cdk.Duration.seconds(45)
        )

        fn.add_permission('alexa-invocation-trigger',
            principal=iam.ServicePrincipal('alexa-appkit.amazon.com'),
            action='lambda:InvokeFunction',
            event_source_token=alexa_skill_id
        )

        fn.add_to_role_policy(iam.PolicyStatement(
            actions=["secretsmanager:*"],
            resources=[f"arn:aws:secretsmanager:*:{self.account}:secret:*"]
        ))

        secretsmanager.Secret(self, "auth_token_secret",
            secret_name="spotify_access_token",
            description="access token which the apps needs to perform its operations"
        )

        secretsmanager.Secret(self, "auth_refresh_token_secret",
            secret_name="spotify_access_refresh_token",
            description="refresh token which the apps needs to regenerate the access token when it expires"
        )     
