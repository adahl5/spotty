import os
from typing import List
import chevron
import pystache
import re
from spotty.commands.writers.abstract_output_writrer import AbstractOutputWriter
from spotty.deployment.abstract_instance_volume import AbstractInstanceVolume
from spotty.deployment.container_deployment import ContainerDeployment
from spotty.providers.gcp.config.instance_config import InstanceConfig
from spotty.providers.gcp.helpers.sync import BUCKET_SYNC_DIR


def prepare_instance_template(instance_config: InstanceConfig, container: ContainerDeployment, sync_filters: list,
                              volumes: List[AbstractInstanceVolume], machine_name: str, bucket_name: str,
                              output: AbstractOutputWriter):
    """Prepares deployment template to run an instance."""

    # read and update the template
    with open(os.path.join(os.path.dirname(__file__), 'instance', 'template.yaml')) as f:
        template = f.read()

    # get mount directories for the volumes
    mount_dirs = []  # TODO: [volume.mount_dir for volume in volumes]

    # get Docker runtime parameters
    runtime_parameters = container.get_runtime_parameters(bool(instance_config.gpu))

    # render startup script
    startup_script = open(os.path.join(os.path.dirname(__file__), 'instance', 'cloud_init.yaml'), 'r').read()
    startup_script = pystache.render(startup_script, {
        'MACHINE_NAME': machine_name,
        'ZONE': instance_config.zone,
        'VOLUME_MOUNT_DIRS': ('"%s"' % '" "'.join(mount_dirs)) if mount_dirs else '',
        'PROJECT_GS_BUCKET': bucket_name,
        'BUCKET_SYNC_DIR': BUCKET_SYNC_DIR,
        'HOST_PROJECT_DIR': container.host_project_dir,
        'DOCKER_DATA_ROOT_DIR': instance_config.docker_data_root,
        'DOCKER_IMAGE': container.config.image,
        'DOCKERFILE_PATH': container.dockerfile_path,
        'DOCKER_BUILD_CONTEXT_PATH': container.docker_context_path,
        'DOCKER_RUNTIME_PARAMS': runtime_parameters,
        'DOCKER_WORKING_DIR': container.config.working_dir,
    })

    indent_size = len(re.search('( *){{{STARTUP_SCRIPT}}}', template).group(1))
    startup_script = startup_script.replace('\n', '\n' + ' ' * indent_size)  # fix indent for the YAML file

    # render the template
    parameters = {
        'SERVICE_ACCOUNT_EMAIL': 'spotty@spotty-221422.iam.gserviceaccount.com',
        'GCP_PROJECT_ID': instance_config.project_id,
        'ZONE': instance_config.zone,
        'MACHINE_TYPE': instance_config.machine_type,
        'SOURCE_IMAGE': instance_config.image_name,
        'STARTUP_SCRIPT': startup_script,
        'MACHINE_NAME': machine_name,
        'PREEMPTIBLE': 'false' if instance_config.on_demand else 'true',
        'GPU_TYPE': instance_config.gpu['type'] if instance_config.gpu else '',
        'GPU_COUNT': instance_config.gpu['count'] if instance_config.gpu else 0,
    }
    template = chevron.render(template, parameters)

    return template
