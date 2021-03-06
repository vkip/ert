#  Copyright (C) 2012  Statoil ASA, Norway. 
#   
#  The file 'enkf_fs.py' is part of ERT - Ensemble based Reservoir Tool. 
#   
#  ERT is free software: you can redistribute it and/or modify 
#  it under the terms of the GNU General Public License as published by 
#  the Free Software Foundation, either version 3 of the License, or 
#  (at your option) any later version. 
#   
#  ERT is distributed in the hope that it will be useful, but WITHOUT ANY 
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or 
#  FITNESS FOR A PARTICULAR PURPOSE.   
#   
#  See the GNU General Public License at <http://www.gnu.org/licenses/gpl.html> 
#  for more details.
from ert.cwrap import BaseCClass, CWrapper
from ert.enkf import ENKF_LIB, TimeMap
from ert.util import Buffer


class EnkfFs(BaseCClass):
    def __init__(self):
        raise NotImplementedError("Class can not be instantiated directly!")

    def has_node(self, node_key, var_type, report_step, iens, state):
        return EnkfFs.cNamespace().has_node(self, node_key, var_type, report_step, iens, state)

    def has_vector(self, node_key, var_type, iens, state):
        return EnkfFs.cNamespace().has_vector(self, node_key, var_type, iens, state)


    def fread_node(self, key, type, step, member, value):
        buffer = Buffer(100)
        EnkfFs.cNamespace().fread_node(self, buffer, key, type, step, member, value)

    def fread_vector(self, key, type, member, value):
        buffer = Buffer(100)
        EnkfFs.cNamespace().fread_vector(self, buffer, key, type, member, value)

    def get_time_map(self):
        return EnkfFs.cNamespace().get_time_map(self).setParent(self)

    def getCaseName(self):
        """ @rtype: str """
        return EnkfFs.cNamespace().get_case_name(self)

    @classmethod
    def exists(cls, path):
        return cls.cNamespace().exists(path)

    def free(self):
        EnkfFs.cNamespace().free(self)

##################################################################

cwrapper = CWrapper(ENKF_LIB)
cwrapper.registerType("enkf_fs", EnkfFs)
cwrapper.registerType("enkf_fs_obj", EnkfFs.createPythonObject)
cwrapper.registerType("enkf_fs_ref", EnkfFs.createCReference)

EnkfFs.cNamespace().close = cwrapper.prototype("void enkf_fs_close(enkf_fs)")
EnkfFs.cNamespace().has_node = cwrapper.prototype("bool enkf_fs_has_node(enkf_fs, char*, c_uint, int, int, c_uint)")
EnkfFs.cNamespace().has_vector = cwrapper.prototype("bool enkf_fs_has_vector(enkf_fs, char*, c_uint, int, c_uint)")
EnkfFs.cNamespace().fread_node = cwrapper.prototype("void enkf_fs_fread_node(enkf_fs, buffer, char*, c_uint, int, int, c_uint)")
EnkfFs.cNamespace().fread_vector = cwrapper.prototype("void enkf_fs_fread_vector(enkf_fs, buffer, char*, c_uint, int, c_uint)")
EnkfFs.cNamespace().get_time_map = cwrapper.prototype("time_map_ref enkf_fs_get_time_map(enkf_fs)")
EnkfFs.cNamespace().exists = cwrapper.prototype("bool enkf_fs_exists(char*)")
EnkfFs.cNamespace().get_case_name = cwrapper.prototype("char* enkf_fs_get_case_name(enkf_fs)")
