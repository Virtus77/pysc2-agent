from pysc2.agents import base_agent
from pysc2.env import sc2_env
from pysc2.lib import actions, features, units
from absl import app
import random

class SimpleAgent(base_agent.BaseAgent):
    def step(self, obs):
        super(SimpleAgent, self).step(obs)
        # get a list of all SCVs on the screen
        scvs = [unit for unit in obs.observation.feature_units
                if unit.unit_type == units.Terran.SCV]
        if len(scvs) > 0:
            scv = random.choice(scvs)
            return actions.FUNCTIONS.select_point("select_all_type", (scv.x, scv.y))
        return actions.FUNCTIONS.no_op()
        
def main(unused_argv):
    agent = SimpleAgent()
    try:
        while True:
            with sc2_env.SC2Env(
                    map_name="AbyssalReef",
                    # first player is my terran agent, second player is a random bot
                    players=[sc2_env.Agent(sc2_env.Race.terran),
                             sc2_env.Bot(sc2_env.Race.random, 
                                        sc2_env.Difficulty.very_easy)],
                    # specify the screen and minimap resolutions
                    agent_interface_format = features.AgentInterfaceFormat(
                        feature_dimensions = features.Dimensions(screen=84, minimap=84),
                        use_feature_units=True),
                    # how many "game steps" pass before the bot will choose an action to take
                    # default is set to 8, approximately 300 APM on "Normal" game speed
                    # set it to 160 to reduce the APM to 150
                    step_mul = 16,
                    # length of each game, default is 30 mins at normal speed
                    # set this value to 0 allows the game to run as long as necessary
                    game_steps_per_episode = 0,
                    # visualize all of the observation layers
                    visualize=True) as env:
                    
                agent.setup(env.observation_spec(), env.action_spec())
                timesteps = env.reset()
                agent.reset()
                
                while True:
                    step_actions = [agent.step(timesteps[0])]
                    if timesteps[0].last():
                        break
                    timesteps = env.step(step_actions)
    except KeyboardInterrupt:
        pass
                
if __name__ == "__main__":
    app.run(main)