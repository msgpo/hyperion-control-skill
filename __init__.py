#!/usr/bin/env python
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Mycroft Core.  If not, see <http://www.gnu.org/licenses/>.

from os.path import dirname
from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger
from mycroft.util import play_mp3
from colour import Color
import math
import re
from pexpect import pxssh

__author__ = 'PCWii'

# Logger: used for debug lines, like "LOGGER.debug(xyz)". These
# statements will show up in the command line when running Mycroft.
LOGGER = getLogger(__name__)

# List each of the bulbs here
seq_delay = 0.5
effect_delay = 3000

Valid_Color = ['red', 'read', 'orange', 'yellow', 'green', 'blue', 'indigo', 'violet', 'purple', 'white']

# The logic of each skill is contained within its own class, which inherits
# base methods from the MycroftSkill class with the syntax you can see below:
# "class ____Skill(MycroftSkill)"
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


    # The "handle_xxxx_intent" functions define Mycroft's behavior when
    # each of the skill's intents is triggered: in this case, he simply
    # speaks a response. Note that the "speak_dialog" method doesn't
    # actually speak the text it's passed--instead, that text is the filename
    # of a file in the dialog folder, and Mycroft speaks its contents when
    # the method is called.
    def handle_hyperion_light_on_intent(self, message):
        mycmd = 'hyperion-remote -c white'
        result = self.ssh_cmd(self, mycmd)
        if not result:
            self.speak_dialog("light.on")

    def handle_hyperion_light_off_intent(self, message):
        mycmd = "hyperion-remote -x"
        result = self.ssh_cmd(self, mycmd)
        if not result:
            self.speak_dialog("light.off")

    def handle_hyperion_light_dim_intent(self, message):
        mycmd = "hyperion-remote --effect 'Knight rider' --duration 3000"
        result = self.ssh_cmd(self, mycmd)
        if not result:
            self.speak_dialog("light.dim")

    def handle_hyperion_light_set_intent(self, message):
        str_remainder = str(message.utterance_remainder())
        for findcolor in Valid_Color:
            mypos = str_remainder.find(findcolor)
            if mypos > 0:
                if findcolor == 'read':
                    findcolor = 'red'
                myRed = math.trunc(Color(findcolor).get_red() * 255)
                myGreen = math.trunc(Color(findcolor).get_green() * 255)
                myBlue = math.trunc(Color(findcolor).get_blue() * 255)
                myHex = Color(findcolor).hex_l
                mycmd = "hyperion-remote --color " + myHex[1:]
                result = self.ssh_cmd(self, mycmd)
                if not result:
                    self.speak_dialog("light.set", data ={"result": findcolor})
                    break
        dim_level = re.findall('\d+', str_remainder)
        if dim_level:
            new_brightness = int(dim_level[0]) * 0.1
            mycmd = "hyperion-remote -m" + new_brightness
            result = self.ssh_cmd(self, mycmd)
            if not result:
                self.speak_dialog("light.set", data={"result": str(dim_level[0])+ ", percent"})

    def handle_hyperion_goal_intent(self, message):
        mycmd = "hyperion-remote --effect 'Knight rider' --duration 40000"
        result = self.ssh_cmd(self, mycmd)
        if not result:
            self.process = play_mp3(join(dirname(__file__), "mp3", "Bruins-GH.mp3"))
            # self.speak_dialog("light.dim")

    # The "stop" method defines what Mycroft does when told to stop during
    # the skill's execution. In this case, since the skill's functionality
    # is extremely simple, the method just contains the keyword "pass", which
    # does nothing.
    def stop(self):
        pass

# The "create_skill()" method is used to create an instance of the skill.
# Note that it's outside the class itself.
def create_skill():
    return HyperionLightSkill()
