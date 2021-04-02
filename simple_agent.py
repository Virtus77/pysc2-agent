from pysc2.agents import base_agent
from pysc2.env import sc2_env
from pysc2.lib import actions, features, units
from absl import app
import random

class SimpleAgent(base_agent.BaseAgent):
    def unit_type_is_selected(self, obs, unit_type):
    # checks both the single and multi-selections to see if the first selected unit is the correct type
        if (len(obs.observation.single_select) > 0 and
            obs.observation.single_select[0].unit_type == unit_type):
            return True
        if (len(obs.observation.multi_select) > 0 and
            obs.observation.multi_select[0].unit_type == unit_type):
            return True
        return False
    
    def get_units_by_type(self, obs, unit_type):
        return [unit for unit in obs.observation.feature_units
                if unit.unit_type == unit_type]
                
    def can_do(self, obs, action):
        return action in obs.observation.available_actions
        
    def step(self, obs):
        super(SimpleAgent, self).step(obs)
        
        supply_depots = self.get_units_by_type(obs, units.Terran.SupplyDepot)
        if len(supply_depots) == 0:
            if self.unit_type_is_selected(obs, units.Terran.SCV):
                if self.can_do(obs, actions.FUNCTIONS.Build_SupplyDepot_screen.id):
                    x = random.randint(0, 83)
                    y = random.randint(0, 83)
                    return actions.FUNCTIONS.Build_SupplyDepot_screen("now", (x, y))
        
        barracks = self.get_units_by_type(obs, units.Terran.Barracks)
        if len(barracks) == 0 or len(barracks) < 3:
           if self.unit_type_is_selected(obs, units.Terran.SCV):
                if self.can_do(obs, actions.FUNCTIONS.Build_Barracks_screen.id):
                    x = random.randint(0, 83)
                    y = random.randint(0, 83)
                    return actions.FUNCTIONS.Build_Barracks_screen("now", (x,y))
                
        free_supply = (obs.observation.player.food_cap - obs.observation.player.food_used)
        if free_supply == 0:
            if self.unit_type_is_selected(obs, units.Terran.SCV):
                if self.can_do(obs, actions.FUNCTIONS.Build_SupplyDepot_screen.id):
                    x = random.randint(0, 83)
                    y = random.randint(0, 83)
                    return actions.FUNCTIONS.Build_SupplyDepot_screen("now", (x, y))
                    
        barracks = self.get_units_by_type(obs, units.Terran.Barracks)
        if len(barracks) > 0:
            if self.unit_type_is_selected(obs, units.Terran.Barracks):
                if self.can_do(obs, actions.FUNCTIONS.Train_Marine_quick.id):
                    return actions.FUNCTIONS.Train_Marine_quick("now")
            else:
                barrack = random.choice(barracks)
                x = max(0, barrack.x)
                y = max(0, barrack.y)
                return actions.FUNCTIONS.select_point("select_all_type", (x,y))
                        
        # get a list of all SCVs on the screen
        
        scvs = self.get_units_by_type(obs, units.Terran.SCV)
        if len(scvs) > 0:
            scv = random.choice(scvs)
            x = max(0, scv.x)
            y = max(0, scv.y)
            return actions.FUNCTIONS.select_point("select_all_type", (x, y))
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