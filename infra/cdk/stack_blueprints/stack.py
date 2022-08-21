"""Main python file_key for adding resources to the application stack."""
from typing import Dict, Any
import aws_cdk
import aws_cdk.aws_iam as iam
import aws_cdk.aws_kms as kms
import aws_cdk.aws_s3 as s3
import aws_cdk.aws_lambda as _lambda
from constructs import Construct

from .iam_construct import IAMConstruct
from .kms_construct import KMSConstruct
from .s3_construct import S3Construct
from .lambda_construct import LambdaConstruct


class MainProjectStack(aws_cdk.Stack):
    """Build the app stacks and its resources."""
    def __init__(self, env_var: str, scope: Construct, 
                 app_id: str, config: dict, **kwargs: Dict[str, Any]) -> None:
        """Creates the cloudformation templates for the projects."""
        super().__init__(scope, app_id, **kwargs)
        self.env_var = env_var
        self.config = config
        MainProjectStack.create_stack(self, config=config, env=self.env_var)

    @staticmethod
    def create_stack(stack: aws_cdk.Stack, config: dict, env: str) -> None:
        """Create and add the resources to the application stack"""

        # KMS infra setup ------------------------------------------------------
        kms_pol_doc = IAMConstruct.get_kms_policy_document()

        kms_key = KMSConstruct.create_kms_key(
            stack=stack,
            config=config,
            policy_doc=kms_pol_doc
        )
        print(kms_key)

        # IAM Role Setup --------------------------------------------------------
        stack_role = MainProjectStack.create_stack_role(
            config=config,
            stack=stack,
            kms_key=kms_key
        )
        print(stack_role)

        # S3 Bucket Infra Setup --------------------------------------------------
        MainProjectStack.create_bucket(
            config=config,
            env=env,
            stack=stack
        )
  
        # Infra for Lambda function creation -------------------------------------
        MainProjectStack.create_lambda_functions(
            stack=stack,
            config=config,
            env=env,
            kms_key=kms_key
        )

    @staticmethod
    def create_stack_role(
        config: dict,
        stack: aws_cdk.Stack,
        kms_key: kms.Key
    ) -> iam.Role:
        """Create the IAM role."""

        stack_policy = IAMConstruct.create_managed_policy(
            stack=stack,
            config=config,
            policy_name="mainStack",
            statements=[
                KMSConstruct.get_kms_key_encrypt_decrypt_policy(
                    [kms_key.key_arn]
                ),
                S3Construct.get_s3_object_policy([config['global']['bucket_arn']]),
            ]
        )
        stack_role = IAMConstruct.create_role(
            stack=stack,
            config=config,
            role_name="mainStack",
            assumed_by=["s3", "lambda"]
        )
        stack_role.add_managed_policy(policy=stack_policy)
        return stack_role

    @staticmethod
    def create_bucket(
            config: dict,
            env: str,
            stack: aws_cdk.Stack) -> s3.Bucket:
        """Create an encrypted s3 bucket."""

        print(env)
        s3_bucket = S3Construct.create_bucket(
            stack=stack,
            bucket_id=f"moving-incoming-files-{config['global']['env']}",
            bucket_name=config['global']['bucket_name']
        )
        return s3_bucket

    @staticmethod
    def create_lambda_functions(
            stack: aws_cdk.Stack,
            config: dict,
            env: str,
            kms_key: kms.Key) -> Dict[str, _lambda.Function]:
        """Create placeholder lambda function and roles."""
   
        lambdas = {}
   
        # Moving incoming files to S3 destination lambda.
        moving_incoming_files_policy = IAMConstruct.create_managed_policy(
            stack=stack,
            config=config,
            policy_name="moving_incoming_files",
            statements=[
                LambdaConstruct.get_cloudwatch_policy(
                    config['global']['moving_incoming_files_lambdaLogsArn']
                ),
                S3Construct.get_s3_object_policy(config['global']['bucket_arn']),
                S3Construct.get_s3_bucket_policy(config['global']['bucket_arn']),
                KMSConstruct.get_kms_key_encrypt_decrypt_policy([kms_key.key_arn])
            ]
        )

        moving_incoming_files_role = IAMConstruct.create_role(
            stack=stack,
            env=env,
            config=config,
            role_name="moving_incoming_files",
            assumed_by=["lambda", "s3"]   
        )
 
        moving_incoming_files_role.add_managed_policy(moving_incoming_files_policy)

        lambdas["moving_incoming_files_lambda"] = LambdaConstruct.create_lambda(
            stack=stack,
            env=env,
            config=config,
            lambda_name="moving_incoming_files_lambda",
            role=moving_incoming_files_role,
            duration=aws_cdk.Duration.minutes(15)
        )