from golem.environments.Environment import Environment
from golem.task.TaskBase import ComputeTaskDef
from golem.task.TaskState import SubtaskStatus

from GNRTask import GNRTask, GNRTaskBuilder

import random
import logging
import os

logger = logging.getLogger(__name__)

##############################################
class UpdateOtherGolemsTaskDefinition:
    def __init__(self):
        self.task_id = ""

        self.full_task_timeout    = 0
        self.subtask_timeout     = 0

        self.resource_dir        = ""
        self.src_file            = ""
        self.resources          = []
        self.total_subtasks      = 1

##############################################
class UpdateOtherGolemsTaskBuilder(GNRTaskBuilder):
    #######################
    def __init__(self, client_id, task_definition, root_path, src_dir):
        GNRTaskBuilder.__init__(self, client_id, task_definition, root_path)
        self.src_dir = src_dir

    def build(self):
        with open(self.task_definition.src_file) as f:
            src_code = f.read()
        self.task_definition.task_resources = set()
        for dir, dirs, files in os.walk(self.src_dir):
            for file_ in files:
                _, ext = os.path.splitext(file_)
                if ext in '.ini':
                    continue
                self.task_definition.task_resources.add(os.path.join(dir,file_))

        print self.task_definition.task_resources
        resource_size = 0
        for resource in self.task_definition.task_resources:
            resource_size += os.stat(resource).st_size

        return UpdateOtherGolemsTask(   src_code,
                            self.client_id,
                            self.task_definition.task_id,
                            "",
                            0,
                            "",
                            self.root_path,
                            Environment.get_id(),
                            self.task_definition.full_task_timeout,
                            self.task_definition.subtask_timeout,
                            self.task_definition.task_resources,
                            resource_size,
                            0,
                            self.task_definition.total_subtasks
                          )

##############################################
class UpdateOtherGolemsTask(GNRTask):

    def __init__(self,
                  src_code,
                  client_id,
                  task_id,
                  owner_address,
                  owner_port,
                  owner_key_id,
                  root_path,
                  environment,
                  ttl,
                  subtask_ttl,
                  resources,
                  resource_size,
                  estimated_memory,
                  total_tasks):


        GNRTask.__init__(self, src_code, client_id, task_id, owner_address, owner_port, owner_key_id, environment,
                            ttl, subtask_ttl, resource_size, estimated_memory)

        self.total_tasks = total_tasks
        self.root_path = root_path

        self.task_resources = resources
        self.active = True
        self.updated = {}


    #######################
    def abort (self):
        self.active = False

    #######################
    def query_extra_data(self, perf_index, num_cores, client_id):

        if client_id in self.updated:
            return None

        ctd = ComputeTaskDef()
        ctd.task_id = self.header.task_id
        hash = "{}".format(random.getrandbits(128))
        ctd.subtask_id = hash
        ctd.extra_data = { "start_task" : self.last_task,
                          "end_task": self.last_task + 1 }
        ctd.return_address = self.header.task_owner_address
        ctd.return_port = self.header.task_owner_port
        ctd.task_owner = self.header.task_owner
        ctd.short_description = "Golem update"
        ctd.src_code = self.src_code
        ctd.performance = perf_index
        if self.last_task + 1 <= self.total_tasks:
            self.last_task += 1
        self.updated[ client_id ] = True

        self.subtasks_given[ hash ] = ctd.extra_data
        self.subtasks_given[ hash ][ 'status' ] = SubtaskStatus.starting
        self.subtasks_given[ hash ][ 'client_id' ] = client_id

        return ctd

    #######################
    def computation_finished(self, subtask_id, task_result, dir_manager = None, result_type = 0):
        self.subtasks_given[ subtask_id ][ 'status' ] = SubtaskStatus.finished
