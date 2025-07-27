#!/usr/bin/env python3
import os

import aws_cdk as cdk

from backend.component import Backend
from frontend.component import Frontend

app = cdk.App()
backend = Backend(app, "Backend")
frontend = Frontend(app, "Frontend")

app.synth()
