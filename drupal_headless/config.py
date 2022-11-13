import sys
def getConfigurations():
  response = {
    "instance_name" : "drupal-headless",
    "instance_type" : "t2.micro",
    "ami_name" : "drupal_2022-10-22",
    "vpc_name" : "vpc-0979616b4b28f01e9",
    "security_group" : "ec2-sec-grp",
    "repository_name" : "DrupalHeadlessRepository",
    "pipeline_name" : "drupal-headless-pipeline",
    "branch_name" : "main",
    "userdata": "sudo apt-get update;sudo apt-get install ruby;sudo apt-get install wget;sudo wget -P /home/ubuntu https://aws-codedeploy-us-east-2.s3.us-east-2.amazonaws.com/latest/install;sudo chmod +x /home/ubuntu/install;sudo /home/ubuntu/install auto > /tmp/logfile;sudo service codedeploy-agent start"
    # "userdata" : [
    #   "sudo apt-get update",
    #   "sudo apt-get install ruby",
    #   "sudo apt-get install wget",
    #   "sudo wget -P /home/ubuntu https://aws-codedeploy-us-east-2.s3.us-east-2.amazonaws.com/latest/install",
    #   "sudo chmod +x /home/ubuntu/install",
    #   "sudo /home/ubuntu/install auto > /tmp/logfile",
    #   "sudo service codedeploy-agent start"
    # ]
  }
  return response