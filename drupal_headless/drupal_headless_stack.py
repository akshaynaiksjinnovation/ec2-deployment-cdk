from argparse import Action
import imp
from aws_cdk import (
    # Duration,
    Stack,
    Stage,
    aws_ec2,
    pipelines,
    aws_codecommit,
    CfnOutput,
    aws_codedeploy,
    aws_iam,
)
from constructs import Construct
import drupal_headless.config as configFunc
import os
from deployment.deployment_stack import MyOutputStage
class DrupalHeadlessStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        configData = configFunc.getConfigurations()

        #Creating roles for Deployment
        ec2_role = aws_iam.Role(
            self,
            "ec2role",
            role_name="ec2role",
            managed_policies=[
                aws_iam.ManagedPolicy.from_managed_policy_arn(self,
                    id="AmazonEC2RoleforAWSCodeDeploy",
                    managed_policy_arn="arn:aws:iam::aws:policy/service-role/AmazonEC2RoleforAWSCodeDeploy"
                )
            ],
            assumed_by= aws_iam.ServicePrincipal("ec2.amazonaws.com")
        )

        deployment_group_role = aws_iam.Role(
            self,
            "deploymentgrouprole",
            role_name="deploymentgrouprole",
            managed_policies=[
                aws_iam.ManagedPolicy.from_aws_managed_policy_name(
                    managed_policy_name="AmazonS3FullAccess"
                ),
                aws_iam.ManagedPolicy.from_aws_managed_policy_name(
                    managed_policy_name="AmazonS3ReadOnlyAccess"
                ),
                aws_iam.ManagedPolicy.from_managed_policy_arn(self,
                    id="AWSCodeDeployRole",
                    managed_policy_arn="arn:aws:iam::aws:policy/service-role/AWSCodeDeployRole"
                )
            ],
            assumed_by= aws_iam.ServicePrincipal("codedeploy.amazonaws.com")
        )
        
        #role for code pipeline
        pipeline_role = aws_iam.Role(
            self,
            "pipelinerole",
            role_name="pipelinerole",
            managed_policies=[
                aws_iam.ManagedPolicy.from_managed_policy_arn(self,
                    id="AWSCodeDeployDeployerAccess",
                    managed_policy_arn="arn:aws:iam::aws:policy/AWSCodeDeployDeployerAccess"
                )
            ],
            assumed_by= aws_iam.ServicePrincipal("codepipeline.amazonaws.com")
        )

        print ("Looking for AMI ")
        ami_image = aws_ec2.MachineImage().lookup(name=configData['ami_name'])
        if not ami_image :
            print ("Ami not found")
            return 
        print(os.getcwd())
        file = open('drupal_headless/script.sh', 'r')
        #file = open(filename, mode='r')
        print (f'Looking up instance type: {configData["instance_type"]}')
        instance_type = aws_ec2.InstanceType(configData["instance_type"])
        if not instance_type:
            print ('Failed finding instance')
            return

        print (f'Using VPC: {configData["vpc_name"]}')
        vpc = aws_ec2.Vpc.from_lookup(self, 'vpc', vpc_id=configData["vpc_name"])
        if not vpc:
            print ('Failed finding VPC')
            return
        
        print ('Creating security group')
        sec_grp= aws_ec2.SecurityGroup(self, configData["security_group"], vpc=vpc, allow_all_outbound=True)
        if not sec_grp:
            print ('Failed finding security group')
            return

        print ('Creating inbound firewall rule')
        sec_grp.add_ingress_rule(
            peer=aws_ec2.Peer.ipv4('0.0.0.0/0'), 
            description='inbound SSH', 
            connection=aws_ec2.Port.tcp(22))

        sec_grp.add_ingress_rule(
            peer=aws_ec2.Peer.ipv4('0.0.0.0/0'), 
            description='inbound web traffic', 
            connection=aws_ec2.Port.tcp(80))
        if not sec_grp:
            print ('Failed creating security group')
            return

        

        #userdata = aws_ec2.UserData.for_linux()
        #userdata.add_commands(configData["userdata"])
        #userdata.add_execute_file_command(file_path='script.sh')
        
        ami_name = aws_ec2.MachineImage.lookup(name=configData["ami_name"])
        print (f'Creating EC2 Instance: {configData["instance_name"]} using {configData["instance_type"]} with ami: {configData["ami_name"]}')
        ec2_inst = aws_ec2.Instance(
            self, 'ec2_inst', 
            instance_name=configData["instance_name"],
            instance_type=instance_type,
            machine_image=ami_name,
            vpc=vpc,
            role=ec2_role,
            # user_data=userdata,
            key_name='id_rsa',
            security_group=sec_grp)

        elastic_ip = aws_ec2.CfnEIP(self,'drupal-headless',instance_id=ec2_inst.instance_id)
        ec2_inst.add_user_data(file.read())
        if not ec2_inst:
            print ('Failed creating ec2 instance')
            return
        #repository =  aws_codecommit.Repository
        
        repository = aws_codecommit.Repository(self, configData["repository_name"],
            repository_name=configData["repository_name"],
            code=aws_codecommit.Code.from_directory(directory_path= "drupal_headless/FirstCommit",branch="main")
        )
        repolink = repository.repository_clone_url_http
        application = aws_codedeploy.ServerApplication(self,id="Drupal-Headless-Application",application_name="Drupal-Headless-Application")
        
        deploymentgroup = aws_codedeploy.ServerDeploymentGroup(
            self,
            "Drupal-headless-deployment-group",
            application=application,
            deployment_group_name="Drupal-headless-deployment-group",
            ec2_instance_tags=aws_codedeploy.InstanceTagSet({
            "Name":["drupal-headless"]
            }),
            role=deployment_group_role
            )


        modern_pipeline = pipelines.CodePipeline(self, configData["pipeline_name"],
            self_mutation=False,
            synth=pipelines.ShellStep("deploy",
                input=pipelines.CodePipelineSource.code_commit(repository=repository,branch=configData["branch_name"]),
                commands=[]
                
            ),
            role=pipeline_role,
            
            
            
        )
        
        # lb_app = MyOutputStage(self, "MyApp")
        # modern_pipeline.add_stage(lb_app,
        #     post=[
        #         pipelines.ShellStep("HitEndpoint",
        #             env_from_cfn_outputs={
        #                 # Make the load balancer address available as $URL inside the commands
        #                 "URL": lb_app.load_balancer_address
        #             },
        #             commands=["curl -Ssf $URL"]
        #         )
        #     ]
        # )
        #modern_pipeline.add_stage()
        CfnOutput(self,'Repository link',value=repolink)
        CfnOutput(self,'Instance Id',value=ec2_inst.instance_id)
        CfnOutput(self,'Security Group',value=sec_grp.security_group_id)