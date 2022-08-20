"""IAM Construct Testing"""
import unittest
from unittest.mock import patch, Mock, call
import aws_cdk.aws_iam as iam

from infra.cdk.stack_blueprints.iam_construct import IAMConstruct


class TestIAMConstruct(unittest.TestCase):
    """IAM Construct Testing Class."""
    
    def setup(self):
        self.addCleanup(patch.stopall)
        self.mocked_stack = Mock()
        
        self.mocked_role = patch("aws_cdk.aws_iam.Role", spec=True).start()
        self.mocked_principal = patch(
            "aws_cdk.aws_iam.CompositePrincipal", spec=True
        ).start()
        self.mocked_managed_policy = patch(
            "aws_cdk.aws_iam.ManagedPolicy", spec=True
        ).start()
        self.mocked_policy_statement = patch(
            "aws_cdk.aws_iam.PolicyStatement", spec=True
        ).start()
        self.mocked_effect = patch(
            "aws_cdk.aws_iam.Effect", spec=True
        ).start()
        
        self.config = {
            "env": "test",
            "appNameShort": "test-app",
            "region": "test-region",
            "awsAccount": "test-aws-account",
            "workgroup-arn": "test-workgroup-arn"
        }
        self.high_level_config = {"test": self.config}
        
    def test_create_role(self):
        IAMConstruct.create_role(
            self.mocked_stack,
            self.config["env"],
            self.high_level_config,
            "testRole",
            []
        )
        
        self.mocked_role.assert_called_once_with(
            self.mocked_stack,
            f"{self.config['appNameShort']}-testRole-role-id",
            role_name=f"{self.config['appNameShort']}-testRole-role",
            assumed_by=iam.CompositePrincipal.return_value
        )
        