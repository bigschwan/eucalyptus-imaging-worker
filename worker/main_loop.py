# Copyright 2009-2014 Eucalyptus Systems, Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.
#

# Please contact Eucalyptus Systems, Inc., 6755 Hollister Ave., Goleta
# CA 93117, USA or visit http://www.eucalyptus.com/licenses/ if you need
# additional information or have any questions.
import time
import config
import service
from service.ws import EucaISConnection

class WorkerLoop(object):
    STOPPED = "stopped"
    STOPPING = "stopping"
    RUNNING = "running"

    def __init__(self):
        # get the instance id from metadata service
        self.__instance_id = None
        self.__euca_host = config.get_clc_host()
        if self.__instance_id is None:
            self.__instance_id = config.get_service_id()

        self.__status = WorkerLoop.STOPPED
        service.log.debug('main loop running with clc_host=%s, instance_id=%s' % (self.__euca_host, self.__instance_id))

    def start(self):
        self.__status = WorkerLoop.RUNNING 
        while self.__status == WorkerLoop.RUNNING:
            service.log.info('Querying for new imaging task')
            try:
                con = EucaISConnection(host_name=service.config.get_clc_host(), aws_access_key_id=config.get_access_key_id(),
                          aws_secret_access_key=config.get_secret_access_key(), security_token=config.get_security_token())
                res = con.get_import_task()
                if res['task_id'] != None:
                    task = ImagingTask(res['task_id'], res['manifest_url'], res['volume_id'])
                    # task processing
                    service.log.info('Processing import task %s' % task.task_id)
                    if task.process_task():
                        service.log.info('Done processing task %s' % task.task_id)
                    else:
                        service.log.warn('Processing of the task %s failed' % task.task_id)
                else:
                    service.log.info('There are no task to process')
            except Exception, err:
                service.log.error('Failed to query the imaging service: %s' % err)

            start_time = time.time()
            while time.time() - start_time < config.QUERY_PERIOD_SEC and self.__status == WorkerLoop.RUNNING:
                service.log.debug('sleeping')
                time.sleep(10)

        service.log.info('Exiting')
        self.__status = WorkerLoop.STOPPED

    def stop(self):
        self.__status = WorkerLoop.STOPPING

    def status(self):
        return self.__status
