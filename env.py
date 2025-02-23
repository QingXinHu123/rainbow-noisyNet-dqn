from rl.core import Env
from pysc2.env import sc2_env
from pysc2.lib import features
from pysc2.lib import actions
import numpy as np

FUNCTIONS = actions.FUNCTIONS


# Environment Wrapper für StarCraft2 (pysc2 Bibliothek)
# Erwartet als Action das Output-Format der FullyConv Netzwerk Architektur: ein Tupel bestehend aus zwei Arrays:
# - einem linearen, welches Q-Werte für jede unterschiedliche Aktion enthält
# - einem zweidimensionalen, welches Q-Werte für jede Koordinate auf dem Screen enthält
# Die Methode action_to_sc2 wandelt dabei diesen Output in für pysc2 verwendbare Actions um.
# Außerdem wird die Art der Observation definiert; hier werden aktuell zwei Feature-Layers übergeben:
# - feature_screen.player_relative (Ganzzahlige Klassen 0-3 für (Nichts, Spieler, Gegner, Neutral))
# - feature_screen.selected (1 für selektierte Einheit, 0 für rest)
# Die Klasse implementiert das Interface Keras-rl/core/Env.
class Sc2Env2Outputs(Env):
    last_obs = None

    def __init__(self, screen=16, visualize=False, env_name="MoveToBeacon", training=False):
        print("init SC2")

        self._SCREEN = screen
        self._MINIMAP = screen
        self._VISUALIZE = visualize
        self._ENV_NAME = env_name
        self._TRAINING = training

        self.env = sc2_env.SC2Env(
            map_name=self._ENV_NAME,
            players=[sc2_env.Agent(sc2_env.Race.terran)],
            agent_interface_format=features.AgentInterfaceFormat(
                feature_dimensions=features.Dimensions(
                    screen=self._SCREEN,
                    minimap=self._MINIMAP
                ),
                use_feature_units=True
            ),
            step_mul=8,
            game_steps_per_episode=0,
            visualize=self._VISUALIZE
        )

    def action_to_sc2(self, act):

        real_action = FUNCTIONS.no_op()

        if act.action == 1:
            if 331 in self.last_obs.observation.available_actions:

                real_action = FUNCTIONS.Move_screen("now", (act.coords[1], act.coords[0]))

        elif act.action == 2:

            real_action = FUNCTIONS.select_point("toggle", (act.coords[1], act.coords[0]))

        elif act.action == 0:
            pass
        else:
            print(act.action, "wtf")
            assert False

        return real_action

    def step(self, action):
        # print(action, " ACTION")

        real_action = self.action_to_sc2(action)

        observation = self.env.step(actions=(real_action,))
        self.last_obs = observation[0]

        # small_observation = observation[0].observation.feature_screen.unit_density
        small_observation = [observation[0].observation.feature_screen.player_relative,
                             observation[0].observation.feature_screen.selected]

        return small_observation, observation[0].reward, observation[0].last(), {}

    def reset(self):
        observation = self.env.reset()

        if self._TRAINING and np.random.random_integers(0, 1) == 4:
            ys, xs = np.where(observation[0].observation.feature_screen.player_relative == 1)
            observation = self.env.step(actions=(FUNCTIONS.select_point("toggle", (xs[0], ys[0])),))

        observation = self.env.step(actions=(FUNCTIONS.select_army(0),))

        self.last_obs = observation[0]

        # small_observation = observation[0].observation.feature_screen.unit_density
        small_observation = [observation[0].observation.feature_screen.player_relative,
                             observation[0].observation.feature_screen.selected]

        return small_observation

    def render(self, mode: str = 'human', close: bool = False):
        pass

    def close(self):
        if self.env:
            self.env.close()

    def seed(self, seed=None):
        if seed:
            self.env._random_seed = seed

    def configure(self, *args, **kwargs):

        switcher = {
            '_ENV_NAME': self.set_env_name,
            '_SCREEN': self.set_screen,
            '_MINIMAP': self.set_minimap,
            '_VISUALIZE': self.set_visualize,
        }

        if kwargs is not None:
            for key, value in kwargs:
                func = switcher.get(key, lambda: print)
                func(value)

    def set_env_name(self, name: str):
        self._ENV_NAME = name

    def set_screen(self, screen: int):
        self._SCREEN = screen

    def set_visualize(self, visualize: bool):
        self._VISUALIZE = visualize

    def set_minimap(self, minimap: int):
        self._MINIMAP = minimap

    @property
    def screen(self):
        return self._SCREEN


# Selbes wie Sc2Env2Outputs, allerdings mit anderem Output:
# Gibt ALLE Screen-Feature-Layers zurück (war als Experiment nützlich, wird aber aktuell nicht verwendet).
class Sc2Env2OutputsFull(Env):
    last_obs = None

    def __init__(self, screen=16, visualize=False, env_name="MoveToBeacon", training=False):
        print("init SC2")

        self._SCREEN = screen
        self._MINIMAP = screen
        self._VISUALIZE = visualize
        self._ENV_NAME = env_name
        self._TRAINING = training

        self.env = sc2_env.SC2Env(
            map_name=self._ENV_NAME,
            players=[sc2_env.Agent(sc2_env.Race.terran)],
            agent_interface_format=features.AgentInterfaceFormat(
                feature_dimensions=features.Dimensions(
                    screen=self._SCREEN,
                    minimap=self._MINIMAP
                ),
                use_feature_units=True
            ),
            step_mul=8,
            game_steps_per_episode=0,
            visualize=self._VISUALIZE
        )

    def action_to_sc2(self, act):

        real_action = FUNCTIONS.no_op()

        if act.action == 1:
            if 331 in self.last_obs.observation.available_actions:

                real_action = FUNCTIONS.Move_screen("now", (act.coords[1], act.coords[0]))

        elif act.action == 2:

            real_action = FUNCTIONS.select_point("toggle", (act.coords[1], act.coords[0]))

        elif act.action == 0:
            pass
        else:
            print(act.action, "wtf")
            assert False

        return real_action

    def step(self, action):

        real_action = self.action_to_sc2(action)

        observation = self.env.step(actions=(real_action,))
        self.last_obs = observation[0]

        small_observation = observation[0].observation.feature_screen
        # small_observation = [observation[0].observation.feature_screen.player_relative,
        #                      observation[0].observation.feature_screen.selected]

        return small_observation, observation[0].reward, observation[0].last(), {}

    def reset(self):
        self.env.reset()

        # if self._TRAINING and np.random.random_integers(0, 1) == 4:
        #     ys, xs = np.where(observation[0].observation.feature_screen.player_relative == 1)
        #     observation = self.env.step(actions=(FUNCTIONS.select_point("toggle", (xs[0], ys[0])),))

        observation = self.env.step(actions=(FUNCTIONS.select_army(0),))

        self.last_obs = observation[0]

        small_observation = observation[0].observation.feature_screen

        # small_observation = [observation[0].observation.feature_screen.player_relative,
        #                      observation[0].observation.feature_screen.selected]

        return small_observation

    def render(self, mode: str = 'human', close: bool = False):
        pass

    def close(self):
        if self.env:
            self.env.close()

    def seed(self, seed=None):
        if seed:
            self.env._random_seed = seed

    def configure(self, *args, **kwargs):

        switcher = {
            '_ENV_NAME': self.set_env_name,
            '_SCREEN': self.set_screen,
            '_MINIMAP': self.set_minimap,
            '_VISUALIZE': self.set_visualize,
        }

        if kwargs is not None:
            for key, value in kwargs:
                func = switcher.get(key, lambda: print)
                func(value)

    def set_env_name(self, name: str):
        self._ENV_NAME = name

    def set_screen(self, screen: int):
        self._SCREEN = screen

    def set_visualize(self, visualize: bool):
        self._VISUALIZE = visualize

    def set_minimap(self, minimap: int):
        self._MINIMAP = minimap

    @property
    def screen(self):
        return self._SCREEN


# Environment Wrapper für StarCraft2 (pysc2 Bibliothek)
# Diese Version erwartet als Action einen einzelnen Vektor mit Q-Values für entsprechende Aktionen.
# Durch die FullyConv Architektur, welche 2 Outputs verschiedener Dimension bereitstellt ist dies nicht mehr verwendbar.
# Aus historischen Gründen noch nicht gelöscht.
class Sc2Env1Output(Env):
    last_obs = None

    def __init__(self, screen=16, visualize=False, env_name="MoveToBeacon", training=False):
        print("init SC2")

        self._SCREEN = screen
        self._MINIMAP = screen
        self._VISUALIZE = visualize
        self._ENV_NAME = env_name
        self._TRAINING = training

        self.env = sc2_env.SC2Env(
            map_name=self._ENV_NAME,
            players=[sc2_env.Agent(sc2_env.Race.terran)],
            agent_interface_format=features.AgentInterfaceFormat(
                feature_dimensions=features.Dimensions(
                    screen=self._SCREEN,
                    minimap=self._MINIMAP
                ),
                use_feature_units=True
            ),
            step_mul=8,
            game_steps_per_episode=0,
            visualize=self._VISUALIZE
        )

    def action_to_sc2(self, act):
        real_action = FUNCTIONS.no_op()

        # hacked to only move_screen
        if 0 < act <= self._SCREEN * self._SCREEN:
            if 331 in self.last_obs.observation.available_actions:
                arg = act - 1
                x = int(arg / self._SCREEN)
                y = arg % self._SCREEN
                real_action = FUNCTIONS.Move_screen("now", (y, x))

        elif self._SCREEN * self._SCREEN < act < self._SCREEN * self._SCREEN * 2:
            # if FUNCTIONS.select_point.id in self.last_obs.observation.available_actions:
            arg = act - 1 - self._SCREEN * self._SCREEN
            x = int(arg / self._SCREEN)
            y = arg % self._SCREEN
            real_action = FUNCTIONS.select_point("toggle", (y, x))

        return real_action

    def step(self, action):
        # print(action, " ACTION")

        real_action = self.action_to_sc2(action)

        observation = self.env.step(actions=(real_action,))
        self.last_obs = observation[0]
        small_observation = [observation[0].observation.feature_screen.player_relative, observation[0].observation.feature_screen.selected]

        return small_observation, observation[0].reward, observation[0].last(), {}

    def reset(self):
        observation = self.env.reset()

        if self._TRAINING and np.random.random_integers(1, 1) == 1:
            ys, xs = np.where(observation[0].observation.feature_screen.player_relative == 1)
            observation = self.env.step(actions=(FUNCTIONS.select_point("toggle", (xs[0], ys[0])),))

        # observation = self.env.step(actions=(FUNCTIONS.select_army()))

        self.last_obs = observation[0]
        small_observation = np.array([observation[0].observation.feature_screen.player_relative, observation[0].observation.feature_screen.selected])

        return small_observation

    def render(self, mode: str = 'human', close: bool = False):
        pass

    def close(self):
        if self.env:
            self.env.close()

    def seed(self, seed=None):
        if seed:
            self.env._random_seed = seed

    def configure(self, *args, **kwargs):

        switcher = {
            '_ENV_NAME': self.set_env_name,
            '_SCREEN': self.set_screen,
            '_MINIMAP': self.set_minimap,
            '_VISUALIZE': self.set_visualize,
        }

        if kwargs is not None:
            for key, value in kwargs:
                func = switcher.get(key, lambda: print)
                func(value)

    def set_env_name(self, name: str):
        self._ENV_NAME = name

    def set_screen(self, screen: int):
        self._SCREEN = screen

    def set_visualize(self, visualize: bool):
        self._VISUALIZE = visualize

    def set_minimap(self, minimap: int):
        self._MINIMAP = minimap

