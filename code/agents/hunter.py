from code.random_walk import RandomWalker
from code.agents.prey_predator import Prey, Predator

class Hunter(RandomWalker):
    """
    Species that walks around, lonely but FIRES.
    """

    def __init__(self, unique_id, pos, model):
        super().__init__(unique_id, pos, model)

    def step(self):
    ############################CHOIX DES MOUVEMENTS############################
    #On choisit un mouvement aléatoire
        #self.random_move() #HUNTERMODIF
    #agent of DEATH
        this_cell = self.model.grid.get_cell_list_contents([self.pos])
        victim = [obj for obj in this_cell if isinstance(obj, Prey)] #HUNTERMODIF
        #victim.extend([obj for obj in this_cell if isinstance(obj, Predator)]) #HUNTERMODIF
        if len(victim) > 0:
            #shutdown
            if self.random.random() >= 1/10:
                target = self.random.choice(victim)
                self.model.grid._remove_agent(self.pos, target)
                self.model.schedule.remove(target)
            #pentakill
            else:
                for kill in victim:
                    self.model.grid._remove_agent(self.pos, kill)
                    self.model.schedule.remove(kill)
