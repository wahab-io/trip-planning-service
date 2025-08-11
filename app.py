#!/usr/bin/env python3
import os

import aws_cdk as cdk

from infrastructure.shared import Shared
from backend.component import Backend
from frontend.component import Frontend

app = cdk.App()
shared = Shared(app, "Shared")
backend = Backend(app, "Backend", cluster=shared.cluster)
frontend = Frontend(app, "Frontend", cluster=shared.cluster, backend_service=backend.backend_service)

app.synth()
