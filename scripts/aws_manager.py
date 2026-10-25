#!/usr/bin/env python3
"""
Finlytics AI - AWS EC2 Instance Interactive Manager
Controls the lifecycle of your AWS EC2 instance:
- Always prompts for confirmation before starting or terminating to prevent accidental AWS costs.
- Automatically handles security groups, Docker installation, and deploying Finlytics AI.
"""

import sys
import os
import time
import json
import argparse
from pathlib import Path

# Load environment from .env.aws or .env if available
def load_env_file():
    for filename in [".env.aws", ".env"]:
        filepath = Path(filename)
        if filepath.exists():
            with open(filepath, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        k, v = k.strip(), v.strip().strip("'\"")
                        if k and not os.environ.get(k):
                            os.environ[k] = v

load_env_file()

# Ensure boto3 is installed
try:
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError
except ImportError:
    print("📦 'boto3' is required to interact with AWS.")
    print("Installing boto3 now...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "boto3"])
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError

INSTANCE_TAG = "FinlyticsAI"
SECURITY_GROUP_NAME = "finlytics-security-group"

def get_ec2_client():
    region = os.getenv("AWS_DEFAULT_REGION", os.getenv("AWS_REGION", "us-east-1"))
    try:
        return boto3.client("ec2", region_name=region), boto3.resource("ec2", region_name=region), region
    except NoCredentialsError:
        print("❌ AWS Credentials not found!")
        print("Please configure them via 'aws configure' or set in .env.aws:")
        print("  AWS_ACCESS_KEY_ID=...")
        print("  AWS_SECRET_ACCESS_KEY=...")
        print("  AWS_DEFAULT_REGION=us-east-1")
        sys.exit(1)

def find_finlytics_instance(ec2_client):
    """Finds the most recent Finlytics AI instance that is not terminated."""
    try:
        response = ec2_client.describe_instances(
            Filters=[
                {"Name": "tag:Project", "Values": [INSTANCE_TAG]},
                {"Name": "instance-state-name", "Values": ["pending", "running", "stopping", "stopped"]}
            ]
        )
        for reservation in response.get("Reservations", []):
            for inst in reservation.get("Instances", []):
                return inst
        return None
    except NoCredentialsError:
        print("\n❌ AWS Credentials not found!")
        print("To connect your AWS account, create or edit .env.aws with:")
        print("  AWS_ACCESS_KEY_ID=your_access_key")
        print("  AWS_SECRET_ACCESS_KEY=your_secret_key")
        print("  AWS_DEFAULT_REGION=us-east-1 (or your preferred region)")
        sys.exit(1)
    except ClientError as e:
        print(f"❌ AWS Client Error: {e}")
        return None

def get_or_create_security_group(ec2_client, ec2_resource):
    """Creates a security group allowing HTTP (80), Backend (8000), and SSH (22)."""
    try:
        groups = ec2_client.describe_security_groups(
            GroupNames=[SECURITY_GROUP_NAME]
        ).get("SecurityGroups", [])
        if groups:
            return groups[0]["GroupId"]
    except ClientError:
        pass

    print("🛡️  Creating dedicated security group: " + SECURITY_GROUP_NAME)
    sg = ec2_resource.create_security_group(
        GroupName=SECURITY_GROUP_NAME,
        Description="Security Group for Finlytics AI Docker & Web Stack"
    )
    # Authorize ports 80 (Frontend), 8000 (Backend API), 3000 (Alt Web), 22 (SSH)
    sg.authorize_ingress(
        IpPermissions=[
            {
                "IpProtocol": "tcp",
                "FromPort": 80,
                "ToPort": 80,
                "IpRanges": [{"CidrIp": "0.0.0.0/0", "Description": "HTTP Web Frontend"}]
            },
            {
                "IpProtocol": "tcp",
                "FromPort": 8000,
                "ToPort": 8000,
                "IpRanges": [{"CidrIp": "0.0.0.0/0", "Description": "FastAPI Backend"}]
            },
            {
                "IpProtocol": "tcp",
                "FromPort": 3000,
                "ToPort": 3000,
                "IpRanges": [{"CidrIp": "0.0.0.0/0", "Description": "Docker Compose Port"}]
            },
            {
                "IpProtocol": "tcp",
                "FromPort": 22,
                "ToPort": 22,
                "IpRanges": [{"CidrIp": "0.0.0.0/0", "Description": "SSH Access"}]
            }
        ]
    )
    return sg.id

def get_latest_ubuntu_ami(ec2_client):
    """Retrieves the latest official Ubuntu 24.04 LTS AMI ID."""
    response = ec2_client.describe_images(
        Owners=["099720109477"],  # Canonical official owner ID
        Filters=[
            {"Name": "name", "Values": ["ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*"]},
            {"Name": "state", "Values": ["available"]}
        ]
    )
    images = sorted(response["Images"], key=lambda x: x["CreationDate"], reverse=True)
    if images:
        return images[0]["ImageId"]
    return "ami-0c7217cdde317cfec"  # fallback us-east-1

def confirm_prompt(message, default_no=True):
    """Interactive confirmation prompt."""
    hint = " [y/N]: " if default_no else " [Y/n]: "
    choice = input(message + hint).strip().lower()
    if default_no:
        return choice in ["y", "yes"]
    return choice not in ["n", "no"]

def action_status(ec2_client):
    inst = find_finlytics_instance(ec2_client)
    if not inst:
        print("\n🔍 Status: No active Finlytics AI instance found on AWS.")
        return None
    
    state = inst["State"]["Name"]
    instance_id = inst["InstanceId"]
    pub_ip = inst.get("PublicIpAddress", "N/A")
    pub_dns = inst.get("PublicDnsName", "N/A")
    inst_type = inst.get("InstanceType", "t3.medium")

    print("\n" + "=" * 60)
    print("📊 CURRENT AWS INSTANCE STATUS")
    print("=" * 60)
    print(f"  Instance ID:    {instance_id}")
    print(f"  Type:           {inst_type}")
    print(f"  State:          {state.upper()}")
    print(f"  Public IP:      {pub_ip}")
    print(f"  Public DNS:     {pub_dns}")
    if state == "running":
        print(f"  🌐 Web App:     http://{pub_ip}:3000 (or http://{pub_ip})")
        print(f"  ⚡ API Docs:    http://{pub_ip}:8000/docs")
        print("  💰 Cost alert:  Instance is actively running (hourly charges apply).")
    elif state == "stopped":
        print("  💤 Cost alert:  Instance is STOPPED (zero compute charges).")
    print("=" * 60 + "\n")
    return inst

def action_start_or_launch(ec2_client, ec2_resource, region):
    inst = find_finlytics_instance(ec2_client)
    
    if inst:
        state = inst["State"]["Name"]
        inst_id = inst["InstanceId"]
        if state == "running":
            print(f"✅ Instance {inst_id} is ALREADY RUNNING at http://{inst.get('PublicIpAddress', 'N/A')}:3000")
            return
        elif state == "stopped":
            print(f"Found existing stopped instance: {inst_id}")
            if confirm_prompt(f"❓ Do you want to START (Resume) instance {inst_id} now?"):
                print(f"⏳ Starting instance {inst_id}...")
                ec2_client.start_instances(InstanceIds=[inst_id])
                waiter = ec2_client.get_waiter("instance_running")
                waiter.wait(InstanceIds=[inst_id])
                # Fetch fresh details
                refreshed = ec2_client.describe_instances(InstanceIds=[inst_id])["Reservations"][0]["Instances"][0]
                ip = refreshed.get("PublicIpAddress", "Pending")
                print(f"🎉 Instance is now RUNNING!")
                print(f"🌐 Public IP: http://{ip}:3000")
            else:
                print("Action cancelled.")
            return

    # No existing instance found -> Prompt to launch new
    instance_type = os.getenv("AWS_INSTANCE_TYPE", "t3.medium")
    print("\n🚀 No existing Finlytics instance found.")
    print(f"Configuration: Type={instance_type}, Region={region}")
    
    if not confirm_prompt(f"❓ Do you want to PROVISION and RUN a new {instance_type} EC2 instance now?"):
        print("Launch cancelled.")
        return

    sg_id = get_or_create_security_group(ec2_client, ec2_resource)
    ami_id = get_latest_ubuntu_ami(ec2_client)
    gemini_key = os.getenv("GEMINI_API_KEY", "")

    user_data_script = f"""#!/bin/bash
set -e
apt-get update -y
apt-get install -y docker.io docker-compose git curl
systemctl enable docker
systemctl start docker
usermod -aG docker ubuntu

# Clone Finlytics repository
cd /home/ubuntu
git clone https://github.com/bobbalashriya-rgb/HACKERSBYSEA.git app || true
cd app
git pull origin main || true

# Write environment file
cat <<EOF > .env
GEMINI_API_KEY={gemini_key}
PORT=8000
ENVIRONMENT=production
EOF

# Launch containers
docker-compose up -d --build
"""

    print(f"⏳ Launching EC2 instance ({instance_type}, AMI: {ami_id})...")
    run_response = ec2_client.run_instances(
        ImageId=ami_id,
        InstanceType=instance_type,
        MinCount=1,
        MaxCount=1,
        SecurityGroupIds=[sg_id],
        UserData=user_data_script,
        TagSpecifications=[
            {
                "ResourceType": "instance",
                "Tags": [
                    {"Key": "Name", "Value": "finlytics-ai-instance"},
                    {"Key": "Project", "Value": INSTANCE_TAG}
                ]
            }
        ]
    )
    new_inst_id = run_response["Instances"][0]["InstanceId"]
    print(f"Instance launched with ID: {new_inst_id}")
    print("⏳ Waiting for instance to transition to 'running' state...")
    
    waiter = ec2_client.get_waiter("instance_running")
    waiter.wait(InstanceIds=[new_inst_id])

    refreshed = ec2_client.describe_instances(InstanceIds=[new_inst_id])["Reservations"][0]["Instances"][0]
    ip = refreshed.get("PublicIpAddress", "Pending")
    
    print("\n" + "=" * 60)
    print("🎉 EC2 INSTANCE IS NOW ONLINE & BOOTSTRAPPING!")
    print("=" * 60)
    print(f"  Instance ID:    {new_inst_id}")
    print(f"  Public IP:      {ip}")
    print(f"  Web UI:         http://{ip}:3000 (ready in ~2-3 mins)")
    print(f"  API Docs:       http://{ip}:8000/docs")
    print("=" * 60)
    print("💡 Note: Docker and dependencies install automatically in the background on first boot (~2 mins).")

def action_stop(ec2_client):
    inst = find_finlytics_instance(ec2_client)
    if not inst:
        print("❌ No Finlytics AI instance found to stop.")
        return
    inst_id = inst["InstanceId"]
    state = inst["State"]["Name"]

    if state == "stopped":
        print(f"Instance {inst_id} is ALREADY STOPPED (no compute charges).")
        return

    print(f"\n⚠️  Instance ID: {inst_id} (Current state: {state})")
    print("Stopping this instance preserves your data and code while pausing all hourly compute costs.")
    if confirm_prompt(f"❓ Do you want to STOP instance {inst_id} now?"):
        print(f"⏳ Stopping instance {inst_id}...")
        ec2_client.stop_instances(InstanceIds=[inst_id])
        print("✅ Stop signal dispatched. The instance is shutting down safely.")
    else:
        print("Stop cancelled.")

def action_terminate(ec2_client):
    inst = find_finlytics_instance(ec2_client)
    if not inst:
        print("❌ No active Finlytics AI instance found to terminate.")
        return
    inst_id = inst["InstanceId"]
    state = inst["State"]["Name"]

    print("\n" + "!" * 60)
    print(f"🚨 CRITICAL WARNING: TERMINATE INSTANCE {inst_id} (State: {state})")
    print("Terminating will PERMANENTLY DELETE this virtual machine and its local disks.")
    print("All compute and EBS storage charges will STOP permanently.")
    print("!" * 60)

    if confirm_prompt(f"❓ Are you absolutely sure you want to TERMINATE {inst_id}?"):
        print(f"⏳ Terminating instance {inst_id}...")
        ec2_client.terminate_instances(InstanceIds=[inst_id])
        print(f"✅ Instance {inst_id} is terminated.")
    else:
        print("Termination cancelled.")

def interactive_menu(ec2_client, ec2_resource, region):
    while True:
        action_status(ec2_client)
        print("Choose an action:")
        print("  [1] 🚀 Run / Start Instance (Launch or Resume)")
        print("  [2] 🛑 Stop Instance (Pause compute costs)")
        print("  [3] 🚨 Terminate Instance (Delete completely to prevent any charges)")
        print("  [4] 🔄 Refresh Status")
        print("  [5] 🚪 Exit")
        
        choice = input("\nEnter choice [1-5]: ").strip()
        if choice == "1":
            action_start_or_launch(ec2_client, ec2_resource, region)
        elif choice == "2":
            action_stop(ec2_client)
        elif choice == "3":
            action_terminate(ec2_client)
        elif choice == "4":
            continue
        elif choice in ["5", "q", "exit"]:
            print("Goodbye!")
            break
        else:
            print("Invalid choice, please select 1 to 5.")
        input("\nPress Enter to return to menu...")

def main():
    parser = argparse.ArgumentParser(description="Finlytics AI AWS Instance Lifecycle Manager")
    parser.add_argument("action", nargs="?", choices=["status", "start", "run", "stop", "terminate", "launch"],
                        help="Action to perform (runs interactive menu if omitted)")
    args = parser.parse_args()

    ec2_client, ec2_resource, region = get_ec2_client()

    if args.action in ["start", "run", "launch"]:
        action_start_or_launch(ec2_client, ec2_resource, region)
    elif args.action == "stop":
        action_stop(ec2_client)
    elif args.action == "terminate":
        action_terminate(ec2_client)
    elif args.action == "status":
        action_status(ec2_client)
    else:
        interactive_menu(ec2_client, ec2_resource, region)

if __name__ == "__main__":
    main()
