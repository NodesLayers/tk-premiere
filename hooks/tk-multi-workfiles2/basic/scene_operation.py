# Copyright (c) 2019 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.
import os
import sgtk


HookClass = sgtk.get_hook_baseclass()


class SceneOperation(HookClass):
    """
    Hook called to perform an operation with the current scene.
    """

    def get_default_premiere_project(self):
        """
        Can be overriden in derived hooks to provide a default Premiere project.

        :returns: A string, full path to a Premiere project.
        """
        return os.path.join(
            self.parent.engine.disk_location,
            "resources",
            "Untitled.prproj"
        )

    def execute(self, operation, file_path, context, parent_action, file_version, read_only, **kwargs):
        """
        Main hook entry point

        :param operation:       String
                                Scene operation to perform

        :param file_path:       String
                                File path to use if the operation
                                requires it (e.g. open)

        :param context:         Context
                                The context the file operation is being
                                performed in.

        :param parent_action:   This is the action that this scene operation is
                                being executed for.  This can be one of:
                                - open_file
                                - new_file
                                - save_file_as
                                - version_up

        :param file_version:    The version/revision of the file to be opened.  If this is 'None'
                                then the latest version should be opened.

        :param read_only:       Specifies if the file should be opened read-only or not

        :returns:               Depends on operation:
                                'current_path' - Return the current scene
                                                 file path as a String
                                'reset'        - True if scene was reset to an empty
                                                 state, otherwise False
                                all others     - None
        """
        engine = self.parent.engine
        adobe = engine.adobe
        logger = engine.logger
        logger.info("Executing operation %s" % operation)

        if operation == "current_path":
            return adobe.app.project.path

        elif operation == "open":
            adobe.app.openDocument(file_path)

        elif operation == "save":
            adobe.app.project.save()

        elif operation == "save_as":
            adobe.app.project.saveAs(file_path)

        elif operation == "reset":
            adobe.app.project.closeDocument(0, 0)
            return True

        elif operation == "prepare_new":
            # Premiere seems to have no NewDocument(), so close/open is used instead.
            project_path = self.get_default_premiere_project()
            logger.debug("Opening default project %s" % project_path)
            adobe.app.openDocument(project_path)
