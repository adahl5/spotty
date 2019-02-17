import subprocess
from spotty.helpers.ssh import get_ssh_command
from spotty.providers.aws.helpers.aws_cli import AwsCli


def get_project_s3_path(bucket_name: str):
    return 's3://%s/project' % bucket_name


def get_instance_sync_arguments(sync_filters: list):
    return AwsCli.get_s3_sync_arguments(sync_filters, exact_timestamp=True)


def sync_project_with_s3(project_dir, bucket_name, region, sync_filters, dry_run=False):
    # sync the project with S3, deleted files will be deleted from S3
    AwsCli(region=region).s3_sync(project_dir, get_project_s3_path(bucket_name), filters=sync_filters, delete=True,
                                  capture_output=False, dry_run=dry_run)


def sync_instance_with_s3(sync_filters: list, host: str, user: str, key_path: str, local_ssh_port: int = None):
    # command to sync S3 with the instance
    remote_cmd = subprocess.list2cmdline(['sudo', '/tmp/spotty/instance/scripts/sync_project.sh',
                                          *get_instance_sync_arguments(sync_filters), '>', '/dev/null'])

    # connect to the instance and run remote command
    ssh_command = get_ssh_command(host, user, key_path, remote_cmd, local_ssh_port, quiet=True)
    subprocess.call(ssh_command)
