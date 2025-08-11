FROM codercom/code-server:latest

# Install additional tools if needed
USER root
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

USER coder

# Set working directory
WORKDIR /home/coder/project

# Expose the port
EXPOSE 8080

# Start code-server
CMD ["code-server", "--bind-addr", "0.0.0.0:8080", "--auth", "none", "/home/coder/project"]