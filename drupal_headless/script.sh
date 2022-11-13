#!/bin/bash
sudo mkdir home/ubuntu/akshay;
sudo apt-get update;
sudo apt-get install ruby;
sudo apt-get install wget;
sudo wget -P /home/ubuntu https://aws-codedeploy-us-east-2.s3.us-east-2.amazonaws.com/latest/install;
sudo chmod +x /home/ubuntu/install;
sudo /home/ubuntu/install auto > /tmp/logfile;
sudo service codedeploy-agent start;
sudo mkdir home/ubuntu/akshay2;
