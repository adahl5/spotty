from spotty.providers.gcp.helpers.ce_client import CEClient


class Image(object):

    def __init__(self, data: dict):
        """
        Args:
            data (dict): Example:
                {'archiveSizeBytes': '3652446976',
                 'creationTimestamp': '2018-11-03T19:00:48.577-07:00',
                 'description': '',
                 'diskSizeGb': '10',
                 'guestOsFeatures': [{'type': 'VIRTIO_SCSI_MULTIQUEUE'}],
                 'id': '7541350343606791231',
                 'kind': 'compute#image',
                 'labelFingerprint': '42WmSpB8rSM=',
                 'licenseCodes': ['1000201'],
                 'licenses': ['https://www.googleapis.com/compute/v1/projects/ubuntu-os-cloud/global/licenses/ubuntu-1604-xenial'],
                 'name': 'spotty-ami',
                 'selfLink': 'https://www.googleapis.com/compute/v1/projects/spotty-221422/global/images/spotty-ami',
                 'sourceDisk': 'https://www.googleapis.com/compute/v1/projects/spotty-221422/zones/us-central1-a/disks/spotty-ami',
                 'sourceDiskId': '3401548142858207031',
                 'sourceType': 'RAW',
                 'status': 'READY'}
        """
        self._data = data

    @staticmethod
    def get_by_name(compute: CEClient, image_name: str):
        """Returns an image by its name."""
        res = compute.list_images(image_name)
        if not res:
            return None

        return Image(res[0])

    @property
    def image_id(self) -> str:
        return self._data['id']

    @property
    def name(self) -> str:
        return self._data['name']

    @property
    def size(self) -> int:
        return self._data['diskSizeGb']

    @property
    def self_link(self):
        return self._data['selfLink']

    @property
    def source_disk(self):
        return self._data['sourceDisk']
