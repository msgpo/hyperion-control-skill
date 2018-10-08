#!/usr/bin/env python
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Mycroft Core.  If not, see <http://www.gnu.org/licenses/>.

from os.path import dirname, join
from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger
from mycroft.util import play_mp3
from colour import Color
import math
import re
from pexpect import pxssh
from mycroft.util.log import LOG

import asyncio
import websockets

__author__ = 'PCWii'

# Logger: used for debug lines, like "LOGGER.debug(xyz)". These
# statements will show up in the command line when running Mycroft.
LOGGER = getLogger(__name__)

# List each of the bulbs here
seq_delay = 0.5
effect_delay = 3000

Valid_Color = ['red', 'read', 'orange', 'yellow', 'green', 'blue', 'indigo', 'violet', 'purple', 'white']


async def send_to_hyperion(ambilight_command):
    async with websockets.connect('ws://192.168.0.32:19444') as websocket:
        name = ambilight_command
        await websocket.send(name)
        LOG.info(f"> {name}")
        greeting = await websocket.recv()
        LOG.info(f"< {greeting}")
        return greeting


class HyperionLightSkill(MycroftSkill):
    def ssh_cmd(self, str_cmd):
        try:
            s = pxssh.pxssh()
            hostname = '192.168.0.32'  # raw_input('hostname: 192.168.0.32')
            username = 'osmc'  # raw_input('username: osmc')
            password = 'osmc'  # getpass.getpass('password: osmc')
            s.login(hostname, username, password)
            s.sendline(str_cmd)
            s.logout()
            return None
        except pxssh.ExceptionPxssh as e:
            return e

    # The constructor of the skill, which calls MycroftSkill's constructor
    def __init__(self):
        super(HyperionLightSkill, self).__init__(name="HyperionLightSkill")

    # This method loads the files needed for the skill's functioning, and
    # creates and registers each intent that the skill uses
    def initialize(self):
        self.load_data_files(dirname(__file__))

        hyperion_light_on_intent = IntentBuilder("HyperionLightOnIntent").\
            require("DeviceKeyword").require("OnKeyword").\
            optionally("LightKeyword").build()
        self.register_intent(hyperion_light_on_intent, self.handle_hyperion_light_on_intent)

        hyperion_light_off_intent = IntentBuilder("HyperionLightOffIntent").\
            require("DeviceKeyword").require("OffKeyword").\
            optionally("LightKeyword").build()
        self.register_intent(hyperion_light_off_intent, self.handle_hyperion_light_off_intent)

        hyperion_light_dim_intent = IntentBuilder("HyperionLightDimIntent").\
            require("DimKeyword").require("DeviceKeyword").\
            optionally("LightKeyword").build()
        self.register_intent(hyperion_light_dim_intent, self.handle_hyperion_light_dim_intent)

        hyperion_light_set_intent = IntentBuilder("HyperionLightSetIntent").\
            require("SetKeyword").require("DeviceKeyword").\
            optionally("LightKeyword").build()
        self.register_intent(hyperion_light_set_intent, self.handle_hyperion_light_set_intent)

        hyperion_goal_intent = IntentBuilder("HyperionGoalIntent"). \
            require("GoalKeyword").build()
        self.register_intent(hyperion_goal_intent, self.handle_hyperion_goal_intent)

    def handle_hyperion_light_on_intent(self, message):
        mycmd = '{"color":[255,255,255],"command":"color","priority":100}'
        result = asyncio.get_event_loop().run_until_complete(send_to_hyperion(mycmd))
        if 'success' in str(result):
            self.speak_dialog("light.on")

    def handle_hyperion_light_off_intent(self, message):
        mycmd = '{"command":"clear","priority":100}'
        result = asyncio.get_event_loop().run_until_complete(send_to_hyperion(mycmd))
        if 'success' in str(result):
            self.speak_dialog("light.off")

    def handle_hyperion_light_dim_intent(self, message):
        mycmd = '{"command":"effect","duration":3000,"effect":{"name":"Knight rider"},"priority":100}'
        result = asyncio.get_event_loop().run_until_complete(send_to_hyperion(mycmd))
        if 'success' in str(result):
            self.speak_dialog("light.dim")

    def handle_hyperion_light_set_intent(self, message):
        str_remainder = str(message.utterance_remainder())
        for findcolor in Valid_Color:
            mypos = str_remainder.find(findcolor)
            if mypos > 0:
                if findcolor == 'read':
                    findcolor = 'red'
                my_red = math.trunc(Color(findcolor).get_red() * 255)
                my_green = math.trunc(Color(findcolor).get_green() * 255)
                my_blue = math.trunc(Color(findcolor).get_blue() * 255)
                myHex = Color(findcolor).hex_l
                mycmd = '{"color":[' + str(my_red) + ',' + str(my_blue) + ',' + str(my_green) + '],' \
                        '"command":"color","priority":100}'
                result = asyncio.get_event_loop().run_until_complete(send_to_hyperion(mycmd))
                if 'success' in str(result):
                    self.speak_dialog("light.set", data ={"result": findcolor})
                    break
        dim_level = re.findall('\d+', str_remainder)
        if dim_level:
            new_brightness = int(dim_level[0]) * 0.01
            mycmd = '{"command": "transform", "transform": {"luminanceGain": ' + str(new_brightness) + '}}'
            result = asyncio.get_event_loop().run_until_complete(send_to_hyperion(mycmd))
            if 'success' in str(result):
                self.speak_dialog("light.set", data={"result": str(dim_level[0])+ ", percent"})

    def handle_hyperion_goal_intent(self, message):
        mycmd = '{"command":"effect","duration":3000,"effect":{"name":"Knight rider"},"priority":100}'
        result = asyncio.get_event_loop().run_until_complete(send_to_hyperion(mycmd))
        if 'success' in str(result):
            self.process = play_mp3(join(dirname(__file__), "mp3", "Bruins-GH.mp3"))

    def stop(self):
        pass


def create_skill():
    return HyperionLightSkill()
