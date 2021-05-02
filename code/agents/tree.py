from mesa import Agent


class Tree(Agent):
    """ 
    Agents le plus basique, on le placera sur les cases sur lesquelles il n'y a rien à faire 
    dans le futur, pourrais devenir une case présentant un moins de risques pour une proies
    d'être mangée par un prédateur (la proie se "cache" dans la forêt)
    """


    def __init__(self, unique_id, pos, model):
        super().__init__(unique_id, model)
        # attributes
        self.pos = pos

    def step(self):
        pass
