# Copyright (C) Collabora Limited 2019
# Author: Guillaume Tucker <guillaume.tucker@collabora.com>
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this library; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

"""The model that represents a test regression document in the database."""

import bson
import copy
import datetime
import types

import models
import models.base as modb
import utils

REGRESSION_KEYS = [
    models.TEST_CASE_ID_KEY,
    models.CREATED_KEY,
    models.STATUS_KEY,
    models.KERNEL_KEY,
    models.GIT_COMMIT_KEY,
    models.LAB_NAME_KEY,
    models.BUILD_ID_KEY,
    models.PLAN_VARIANT_KEY,
]


class TestRegressionDocument(modb.BaseDocument):
    """Model for a test regression document.

    Each document is a single test case regression.
    """

    def __init__(self, job, kernel, git_branch, git_url, defconfig_full,
                 build_environment, device_type, lab_name, arch, mach,
                 hierarchy, plan, test_case_path):
        """A new TestRegressionDocument.

        :param job: The job value.
        :type job: string
        :param kernel: The kernel value.
        :type kernel: string
        :param git_branch: The git branch mame.
        :type git_branch: string
        :param git_url: The git repository URL.
        :type git_branch: string
        :param defconfig_full: The full defconfig name with fragments.
        :type defconfig_full: string
        :param build_environment: The description of the build environment.
        :type build_environment: string
        :param device_type: The name of the device type.
        :type device_type: string
        :param lab_name: The name of the test lab.
        :type lab_name: string
        :param arch: The name of the CPU architecture.
        :type arch: string
        :param hierarchy: The test group hierarchy containing the test case.
        :type hierarchy: list of strings
        :param test_case_path: The path representation of the test case.
        :type test_case_path: string
        """
        self._created_on = datetime.datetime.now(tz=bson.tz_util.utc)
        self._id = None
        self._version = None

        self.job = job
        self.kernel = kernel
        self.git_branch = git_branch
        self.git_url = git_url
        self.defconfig_full = defconfig_full
        self.build_environment = build_environment
        self.device_type = device_type
        self.lab_name = lab_name
        self.arch = arch
        self.mach = mach
        self.hierarchy = hierarchy
        self.plan = plan
        self.test_case_path = test_case_path
        self.regressions = []
        self.compiler = None
        self.compiler_version = None

    @property
    def collection(self):
        return models.TEST_REGRESSION_COLLECTION

    @property
    def id(self):
        """The ID of this object as returned by mongodb."""
        return self._id

    @id.setter
    def id(self, value):
        """Set the ID of this object with the ObjectID from mongodb."""
        if self._id:
            raise AttributeError("ID already set")
        self._id = value

    @property
    def created_on(self):
        """When this regression object was created."""
        return self._created_on

    @property
    def version(self):
        """The version of this document schema."""
        return self._version

    @version.setter
    def version(self, value):
        """Set the schema version of this test group."""
        if self._version:
            raise AttributeError("Schema version already set")
        self._version = value

    def add_regression(self, regr_dict):
        """Add information about test regression.

        :param regr_dict: The test regression data.
        :type regr_dict: dictionary

        The test regression data contains one instance of the test case that
        either passed or failed for a given kernel revision.  It must contain
        the following keys:
            * models.TEST_CASE_ID_KEY
            * models.CREATED_KEY
            * models.STATUS_KEY
            * models.KERNEL_KEY
            * models.GIT_COMMIT_KEY

        It is then added to the self.regressions list.
        """
        if not all(k in regr_dict for k in REGRESSION_KEYS):
            raise ValueError("Invalid regression data: {}".format(regr_dict))
        self.regressions.append(regr_dict)

    def to_dict(self):
        regr_dict = {
            models.ARCHITECTURE_KEY: self.arch,
            models.CREATED_KEY: self.created_on,
            models.DEFCONFIG_FULL_KEY: self.defconfig_full,
            models.BUILD_ENVIRONMENT_KEY: self.build_environment,
            models.DEVICE_TYPE_KEY: self.device_type,
            models.LAB_NAME_KEY: self.lab_name,
            models.GIT_BRANCH_KEY: self.git_branch,
            models.GIT_URL_KEY: self.git_url,
            models.HIERARCHY_KEY: self.hierarchy,
            models.MACH_KEY: self.mach,
            models.PLAN_KEY: self.plan,
            models.TEST_CASE_PATH_KEY: self.test_case_path,
            models.JOB_KEY: self.job,
            models.KERNEL_KEY: self.kernel,
            models.REGRESSIONS_KEY: self.regressions,
            models.VERSION_KEY: self.version,
            models.COMPILER_KEY: self.compiler,
            models.COMPILER_VERSION_KEY: self.compiler_version,
        }

        if self._id:
            regr_dict[models.ID_KEY] = self._id

        return regr_dict

    @staticmethod
    def from_json(json_obj):
        if not isinstance(json_obj, types.DictionaryType):
            return None

        regr_doc = None
        obj = copy.deepcopy(json_obj)
        regr_id = obj.pop(models.ID_KEY, None)
        regressions = obj.get(models.REGRESSIONS_KEY, [])
        try:
            job = obj.pop(models.JOB_KEY)
            kernel = obj.pop(models.KERNEL_KEY)
            git_branch = obj.pop(models.GIT_BRANCH_KEY)
            git_url = obj.pop(models.GIT_URL_KEY)
            defconfig_full = obj.pop(models.DEFCONFIG_FULL_KEY)
            build_environment = obj.pop(models.BUILD_ENVIRONMENT_KEY)
            device_type = obj.pop(models.DEVICE_TYPE_KEY)
            lab_name = obj.pop(models.LAB_NAME_KEY)
            arch = obj.pop(models.ARCHITECTURE_KEY)
            mach = obj.pop(models.MACH_KEY)
            hierarchy = obj.pop(models.HIERARCHY_KEY)
            plan = obj.pop(models.PLAN_KEY)
            test_case_path = obj.pop(models.TEST_CASE_PATH_KEY)

            regr_doc = TestRegressionDocument(
                job, kernel, git_branch, git_url, defconfig_full,
                build_environment, device_type, lab_name, arch, mach,
                hierarchy, plan, test_case_path)

            regr_doc.id = regr_id

            for r in regressions:
                regr_doc.add_regression(r)

            for k, v in obj.iteritems():
                setattr(regr_doc, k, v)
        except KeyError as e:
            regr_doc = None

        return regr_doc
