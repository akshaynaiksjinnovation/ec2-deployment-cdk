from aws_cdk import (
    Stage,
    CfnOutput,
)

class MyOutputStage(Stage):

    def __init__(self, scope, id, *, env=None, outdir=None):
        super().__init__(scope, id, env=env, outdir=outdir)
        self.load_balancer_address = CfnOutput(self, "Output", value="value")