from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid, ChartModule
from mesa.visualization.UserParam import UserSettableParameter

from code.agents.prey_predator import Prey, Predator, Hunter
from code.agents.tree import Tree
from code.agents.plant import Plant
from code.model import WolfSheep
"""
Ce code est basé sur le code "wolf_sheep" donné en exemple par la documentation de la librairie
mesa. Le code de celui-ci peut être trouvé ici :
https://github.com/projectmesa/mesa/blob/master/examples/wolf_sheep/wolf_sheep/agents.py
"""


def wolf_sheep_portrayal(agent):
    """ Fonction créant les images des agents qui seront ensuite placé sur la grille """

    if agent is None:
        return

    portrayal = {}

    if type(agent) is Hunter:
        portrayal["Shape"] = "code/resources/hunter.jpg"
        portrayal["scale"] = 0.9
        portrayal["Layer"] = 2
        portrayal["text_color"] = "White"


    elif type(agent) is Predator:
        portrayal["Shape"] = "code/resources/fox.jpg"
        # https://icons8.com/web-app/36821/German-Shepherd
        portrayal["scale"] = 0.9
        portrayal["Layer"] = 2
        portrayal["age"] = agent.age #new round(agent.energy, 1)
        portrayal["energy"] = round(agent.energy,1)
        portrayal["text_color"] = "White"

    elif type(agent) is Prey:
        portrayal["Shape"] = "code/resources/rabbit.jpg"
        # https://icons8.com/web-app/433/sheep
        portrayal["scale"] = 0.9
        portrayal["Layer"] = 2
        portrayal["age"] = agent.age
        portrayal["energy"] = round(agent.energy,1)
        portrayal["text_color"] = "White"


    elif type(agent) is Plant:
        if agent.fully_grown:
            portrayal["Shape"] = "code/resources/plant_grown.jpg"
            portrayal["Filled"] = "true"
            portrayal["Layer"] = 0
            portrayal["w"] = 1
            portrayal["h"] = 1
        else:
            portrayal["Shape"] = "code/resources/plant_sprout.jpg"
            portrayal["Filled"] = "true"
            portrayal["Layer"] = 0
            portrayal["w"] = 1
            portrayal["h"] = 1

    elif type(agent) is Tree:
        portrayal["Shape"] = "code/resources/tree.jpg"
        portrayal["Filled"] = "true"
        portrayal["Layer"] = 0
        portrayal["w"] = 1
        portrayal["h"] = 1

    return portrayal

# création de la grille grâce à des classes fournies par mesa, voir la doc
# mesa pour plus de précisions
canvas_element = CanvasGrid(wolf_sheep_portrayal, 20, 20, 500, 500)
chart_element = ChartModule(
    [{"Label": "Fox", "Color": "#AA0000"}, {"Label": "Rabbit", "Color": "#666666"}]
)

# les paramètres modifiables par l'utilisateur avant le lancement de la simulation
model_params = {
    "grass": UserSettableParameter("checkbox", "Grass Enabled", True),
    "grass_regrowth_time": UserSettableParameter(
        "slider", "Carrot Regrowth Time", 7, 1, 50
    ),
    "initial_sheep": UserSettableParameter(
        "slider", "Initial Rabbit Population", 300, 10, 500
    ),
    "sheep_reproduce": UserSettableParameter(
        "slider", "Rabbit Reproduction Rate", 0.0, 0.00, 0.1, 0.001
    ),
    "initial_wolves": UserSettableParameter(
        "slider", "Initial Fox Population", 50, 10, 300
    ),
    "wolf_reproduce": UserSettableParameter(
        "slider",
        "Fox Reproduction Rate",
        0,
        0.00,
        0.1,
        0.001,
        description="The rate at which Fox agents reproduce.",
    ),
    "wolf_gain_from_food": UserSettableParameter(
        "slider", "Fox Gain From Food Rate", 14, 1, 100
    ),
    "sheep_gain_from_food": UserSettableParameter(
        "slider", "Rabbit Gain From Food", 2, 1, 50
    ),
    "trees_carrots_ratio": UserSettableParameter(
        "slider", "trees ratio", 0.2, 0, 1, 0.01
    ),
    "YEAR": UserSettableParameter( #new
        "slider", "Steps per year", 80, 20, 1000, 10 #new
    ), #new
    "nb_of_hunters": UserSettableParameter(
        "slider", "number of hunters", 0, 0, 20
    ),
}

# création du serveur à l'aide d'une classe fournie par la librairie mesa
# voir la doc mesa pour plus de précisions
server = ModularServer(
    WolfSheep, [canvas_element, chart_element], "Fox Rabbit Predation", model_params
)
server.port = 8521
