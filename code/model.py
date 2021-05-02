"""
Wolf-Sheep Predation Model
================================

Replication of the model found in NetLogo:
    Wilensky, U. (1997). NetLogo Wolf Sheep Predation model.
    http://ccl.northwestern.edu/netlogo/models/WolfSheepPredation.
    Center for Connected Learning and Computer-Based Modeling,
    Northwestern University, Evanston, IL.
"""

from mesa import Model
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector

from code.agents.prey_predator import Prey, Predator
from code.agents.plant import Plant
from code.agents.tree import Tree
from code.agents.hunter import Hunter
from code.schedule import RandomActivationByBreed


class WolfSheep(Model):
    """
    Wolf-Sheep Predation Model
    """

    height = 20
    width = 20

    initial_sheep = 100
    initial_wolves = 50

    sheep_reproduce = 0.04
    wolf_reproduce = 0.05



    wolf_gain_from_food = 20

    grass = False
    grass_regrowth_time = 30
    sheep_gain_from_food = 4

    verbose = False  # Print-monitoring

    description = (
        "A model for simulating wolf and sheep (predator-prey) ecosystem modelling."
    )

    def __init__(
        self,
        height=20,
        width=20,
        initial_sheep=100,
        initial_wolves=50,
        sheep_reproduce=0.04,
        wolf_reproduce=0.05,
        wolf_gain_from_food=20,
        grass=False,
        grass_regrowth_time=30,
        sheep_gain_from_food=4,
        trees_carrots_ratio=0.5,
        YEAR=20,
        nb_of_hunters=0,
    ):
        """
        Create a new Wolf-Sheep model with the given parameters.

        Args:
            initial_sheep: Number of sheep to start with
            initial_wolves: Number of wolves to start with
            sheep_reproduce: Probability of each sheep reproducing each step
            wolf_reproduce: Probability of each wolf reproducing each step
            wolf_gain_from_food: Energy a wolf gains from eating a sheep
            grass: Whether to have the sheep eat grass for energy
            grass_regrowth_time: How long it takes for a grass patch to regrow
                                 once it is eaten
            sheep_gain_from_food: Energy sheep gain from grass, if enabled.
        """
        super().__init__()
        # Set parameters
        self.height = height
        self.width = width
        self.initial_sheep = initial_sheep
        self.initial_wolves = initial_wolves
        self.sheep_reproduce = sheep_reproduce
        self.wolf_reproduce = wolf_reproduce
        self.wolf_gain_from_food = wolf_gain_from_food
        self.grass = grass
        self.grass_regrowth_time = grass_regrowth_time
        self.sheep_gain_from_food = sheep_gain_from_food
        self.trees_carrots_ratio = trees_carrots_ratio
        self.YEAR = YEAR
        self.nb_of_hunters = nb_of_hunters

        self.schedule = RandomActivationByBreed(self) # classe contenant un dictionnaire des types d'agents et agents existants par type, avec une ordre d'activation possible
        self.grid = MultiGrid(self.height, self.width, torus=True)
        self.datacollector = DataCollector(
            {
                "Fox": lambda m: m.schedule.get_breed_count(Predator),
                "Rabbit": lambda m: m.schedule.get_breed_count(Prey),
            }
        )

        # Create sheep:
        for i in range(self.initial_sheep):
            x = self.random.randrange(self.width)
            y = self.random.randrange(self.height)
            age = self.random.randrange(3*self.YEAR)
            energy = self.random.randrange( int(self.sheep_gain_from_food/2), 2 * self.sheep_gain_from_food)
            sheep = Prey(self.next_id(), (x, y), self, True, energy, age)
            self.grid.place_agent(sheep, (x, y))
            self.schedule.add(sheep)

        # Create wolves
        for i in range(self.initial_wolves):
            x = self.random.randrange(self.width)
            y = self.random.randrange(self.height)
            age = self.random.randrange(4*self.YEAR)
            energy = self.random.randrange(int(self.wolf_gain_from_food/2), 2 * self.wolf_gain_from_food)
            wolf = Predator(self.next_id(), (x, y), self, True, energy, age)
            self.grid.place_agent(wolf, (x, y))
            self.schedule.add(wolf)

        # Create grass patches
        if self.grass:
            for agent, x, y in self.grid.coord_iter():
                if self.trees_carrots_ratio < self.random.random(): # aléatoire du nombre d'arbres et de carottes
                    fully_grown = self.random.choice([True, False])
                    if fully_grown:                                 # carottes ou pousses de carotes
                        countdown = self.grass_regrowth_time
                    else:
                        countdown = self.random.randrange(self.grass_regrowth_time)
                    plant = Plant(self.next_id(), (x, y), self, fully_grown, countdown)
                else:
                    plant = Tree(self.next_id(), (x, y), self)
                self.grid.place_agent(plant, (x, y))
                self.schedule.add(plant)

        # create hunters
        for i in range(self.nb_of_hunters):
            x = self.random.randrange(self.width-14, self.width-6) # HUNTERMODIF
            y = self.random.randrange(self.height-14, self.height-6) # HUNTERMODIF
            hunter = Hunter(self.next_id(), (x, y), self)
            self.grid.place_agent(hunter, (x, y))
            self.schedule.add(hunter)

        self.running = True
        self.datacollector.collect(self)

    def step(self):
        self.schedule.step()
        # collect data
        self.datacollector.collect(self) # nombre de renards et lapins à l'instant
        if self.verbose:
            print(
                [
                    self.schedule.time,
                    self.schedule.get_breed_count(Predator),
                    self.schedule.get_breed_count(Prey),
                ]
            )

    def run_model(self, step_count=200):

        if self.verbose:
            print("Initial number fox: ", self.schedule.get_breed_count(Predator))
            print("Initial number rabbit: ", self.schedule.get_breed_count(Prey))

        for i in range(step_count):
            self.step()


        if self.verbose:
            print("")
            print("Final number fox: ", self.schedule.get_breed_count(Predator))
            print("Final number rabbit: ", self.schedule.get_breed_count(Prey))
