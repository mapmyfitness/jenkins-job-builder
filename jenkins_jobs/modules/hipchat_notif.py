# Copyright 2012 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""
Enable HipChat notifications of build execution.

:Parameters:
  * **enabled** *(bool)*: general cut off switch. If not explicitly set to
    ``true``, no hipchat parameters are written to XML. For Jenkins HipChat
    plugin of version prior to 0.1.5, also enables all build results to be
    reported in HipChat room. For later plugin versions, explicit notify-*
    setting is required (see below).
  * **room** *(str)*: name of HipChat room to post messages to
    (default = "")
  * **notify-start** *(bool)*: post messages about build start event
    (default = False)
  * **notify-success** *(bool)*: post messages about successful build event
    (Jenkins HipChat plugin >= 0.1.5) (default = False)
  * **notify-aborted** *(bool)*: post messages about aborted build event
    (Jenkins HipChat plugin >= 0.1.5) (default = False)
  * **notify-not-built** *(bool)*: post messages about build set to NOT_BUILT
    status (Jenkins HipChat plugin >= 0.1.5). This status code is used in a
    multi-stage build (like maven2) where a problem in earlier stage prevented
    later stages from building. (default = False)
  * **notify-unstable** *(bool)*: post messages about unstable build event
    (Jenkins HipChat plugin >= 0.1.5) (default = False)
  * **notify-failure** *(bool)*:  post messages about build failure event
    (Jenkins HipChat plugin >= 0.1.5) (default = False)
  * **notify-back-to-normal** *(bool)*: post messages about build being back to
    normal after being unstable or failed (Jenkins HipChat plugin >= 0.1.5)
    (default = False)

Example:

.. literalinclude:: /../../tests/hipchat/fixtures/hipchat001.yaml
   :language: yaml

"""

# Enabling hipchat notifications on a job requires specifying the hipchat
# config in job properties, and adding the hipchat notifier to the job's
# publishers list.
# The publisher configuration contains extra details not specified per job:
#   - the hipchat authorisation token.
#   - the jenkins server url.
#   - a default room name/id.
# This complicates matters somewhat since the sensible place to store these
# details is in the global config file.
# The global config object is therefore passed down to the registry object,
# and this object is passed to the HipChat() class initialiser.

import xml.etree.ElementTree as XML
import jenkins_jobs.modules.base
import jenkins_jobs.errors
import logging
from six.moves import configparser
import sys

logger = logging.getLogger(__name__)


class HipChat(jenkins_jobs.modules.base.Base):
    sequence = 80

    def __init__(self, registry):
        self.registry = registry

    def gen_xml(self, parser, xml_parent, data):
        logger = logging.getLogger("%s:HipChat" % __name__)
        hipchat = data.get('hipchat')
        if not hipchat or not hipchat.get('enabled', True):
            return
        properties = xml_parent.find('properties')
        if properties is None:
            properties = XML.SubElement(xml_parent, 'properties')
        pdefhip = XML.SubElement(properties,
                                 'jenkins.plugins.hipchat.'
                                 'HipChatNotifier_-HipChatJobProperty')
        XML.SubElement(pdefhip, 'room').text = hipchat.get('room', '')
        # Handle backwards compatibility 'start-notify' but all add an element
        # of standardization with notify-*
        if hipchat.get('start-notify'):
            logger.warn('start-notify is deprecated please use notify-start')
        if hipchat.get('start-notify') is not None or \
           hipchat.get('notify-start') is not None:
            value = str(hipchat.get('notify-start', '')) or \
                str(hipchat.get('start-notify', ''))
            value = value.lower()
            if value == '':
                value = 'false'
            XML.SubElement(pdefhip, 'startNotification').text = value
        if hipchat.get('notify-success') is not None:
            XML.SubElement(pdefhip, 'notifySuccess').text = str(
                hipchat.get('notify-success')).lower()
        if hipchat.get('notify-aborted') is not None:
            XML.SubElement(pdefhip, 'notifyAborted').text = str(
                hipchat.get('notify-aborted')).lower()
        if hipchat.get('notify-not-built') is not None:
            XML.SubElement(pdefhip, 'notifyNotBuilt').text = str(
                hipchat.get('notify-not-built')).lower()
        if hipchat.get('notify-unstable') is not None:
            XML.SubElement(pdefhip, 'notifyUnstable').text = str(
                hipchat.get('notify-unstable')).lower()
        if hipchat.get('notify-failure') is not None:
            XML.SubElement(pdefhip, 'notifyFailure').text = str(
                hipchat.get('notify-failure')).lower()
        if hipchat.get('notify-back-to-normal') is not None:
            XML.SubElement(pdefhip, 'notifyBackToNormal').text = str(
                hipchat.get('notify-back-to-normal')).lower()

        publishers = xml_parent.find('publishers')
        if publishers is None:
            publishers = XML.SubElement(xml_parent, 'publishers')
        hippub = XML.SubElement(publishers,
                                'jenkins.plugins.hipchat.HipChatNotifier')
        
        # If we don't specify anything for these they will be picked up from the jenkins master config
        # XML.SubElement(hippub, 'jenkinsUrl').text = self.jenkinsUrl
        # XML.SubElement(hippub, 'authToken').text = self.authToken
        # The room specified here is the default room.  The default is
        # redundant in this case since a room must be specified.  Leave empty.
        XML.SubElement(hippub, 'room').text = ''
