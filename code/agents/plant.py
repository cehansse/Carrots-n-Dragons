from mesa import Agent


class Plant(Agent):
    """
    Species that grows at a fixed rate and is eaten by prey.
    """

    def __init__(self, unique_id, pos, model, fully_grown, countdown):
        super().__init__(unique_id, model)
        # attributes
        self.fully_grown = fully_grown
        self.countdown = countdown
        self.pos = pos

    def step(self):
        if not self.fully_grown:
            if self.countdown <= 0:
                # Set as fully grown
                self.fully_grown = True
                self.countdown = self.model.grass_regrowth_time
            else:
                self.countdown -= 1
