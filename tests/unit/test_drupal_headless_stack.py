import aws_cdk as core
import aws_cdk.assertions as assertions

from drupal_headless.drupal_headless_stack import DrupalHeadlessStack

# example tests. To run these tests, uncomment this file along with the example
# resource in drupal_headless/drupal_headless_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = DrupalHeadlessStack(app, "drupal-headless")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
