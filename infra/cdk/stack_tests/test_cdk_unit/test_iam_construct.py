"""IAM Construct Testing"""
import unittest
from unittest.mock import patch, Mock, call
import aws_cdk.aws_iam as iam

from infra.cdk.stack_blueprints.iam_construct import IAMConstruct


class TestIAMConstruct(unittest.TestCase):
    """IAM Construct Testing Class."""
    
    def setUp(self) -> None:
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
            "app-name": "test-app",
            "region": "test-region",
            "awsAccount": "test-aws-account",
            "workgroup-arn": "test-workgroup-arn"
        }
        self.high_level_config = {"global": self.config}
        
    def test_create_role(self) -> None:
        IAMConstruct.create_role(
            self.mocked_stack,
            self.high_level_config,
            "testRole",
            [],
        )
        
        self.mocked_role.assert_called_once_with(
            self.mocked_stack,
            f"{self.config['appNameShort']}-testRole-role-id",
            role_name=f"{self.config['appNameShort']}testRole-role",
            assumed_by=iam.CompositePrincipal.return_value,
        )
        
    def test_create_managed_policy(self) -> None:
        expected_statements = self.mocked_policy_statement.return_value
        
        IAMConstruct.create_managed_policy(
            self.mocked_stack,
            self.high_level_config,
            "testPolicy",
            [expected_statements]
        )
        
        self.mocked_managed_policy.assert_called_once_with(
            self.mocked_stack,
            id=f"{self.config['app-name']}-testPolicy-policy-id",
            managed_policy_name=f"{self.config['app-name']}-testPolicy-policy",
            statements=expected_statements
        )
        