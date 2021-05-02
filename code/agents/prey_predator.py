from code.random_walk import RandomWalker
from code.agents.plant import Plant
from code.agents.tree import Tree
from code.agents.hunter import Hunter

class Prey(RandomWalker):
    """
    Species that walks around, reproduces (asexually) and gets eaten.

    Spring effect : self.model.sheep_reproduce is increased and rabbits seek after a partner before eating. (but not before fleeing.)
    Otherwise : no effect, reproduction is the last activity the rabbits will seek to do.

    """

    def __init__(self, unique_id, pos, model, moore=True, energy=None, age=0):
        super().__init__(unique_id, pos, model)
        # attributes
        self.energy = energy
        self.age = age
        self.reproduce = False

    def step(self):
        x, y = self.pos
        spring = False

        ############################INFLUENCE SAISON############################
        #Tous les 20 steps, le primtemps durent 5 steps.
        if self.model.schedule.steps%self.model.YEAR <= self.model.YEAR/4 and self.age > self.model.YEAR/2 :
            spring = True
            reproduce_prob = self.model.sheep_reproduce + 0.3
            if reproduce_prob > 1 :
                reproduce_prob = 1
        else :
            reproduce_prob = self.model.sheep_reproduce

        ############################CHOIX DES MOUVEMENTS############################
        #On choisit un mouvement aléatoire
        if self.random.random() < 0.06:
            self.random_move()
        #Ou on effectue un mouvement optimal
        else:
            next_moves = self.model.grid.get_neighborhood(self.pos, self.moore, True)
            predator = False
            hunter = False                                                           #HUNTERMODIF
            food = False
            for next_move in next_moves:
                content_cell = self.model.grid.get_cell_list_contents(next_move)
                content = [obj for obj in content_cell if isinstance(obj, Predator)]
                if len(content) > 0:
                    # on retient le mouvement.
                    predator_move = next_move
                    predator = True
                content = [obj for obj in content_cell if isinstance(obj, Hunter)]    #HUNTERMODIF to
                if len(content) > 0:
                    # on retient le mouvement.
                    hunter_move = next_move
                    hunter = True                                                         #HUNTERMODIF
                content = [obj for obj in content_cell if isinstance(obj, Plant)]
                if len(content) > 0 and self.energy < self.model.sheep_gain_from_food*4:
                    if content[0].fully_grown:
                        # on retient le mouvement
                        food_move = next_move
                        food = True

                """
                content = [obj for obj in content_cell if isinstance(obj, Prey)] #new
                if len(content) > 1: #new
                    # on retient le mouvement #new
                    reproduce_move = next_move #new
                    reproduce = True #new
                """
            if not spring :
                self.reproduce = False


            not_moved = True
            if spring :
                #Si on est au primtemps, on cherche d'abord à se reproduire, puis à manger.
                #regarde dans un rayon de 2 cases autour de lui et avance vers une proie s'il y en a une dans ce rayon
                next_moves = self.model.grid.get_neighborhood(self.pos, self.moore, False, 2)
                cell_list_contents = [self.model.grid.get_cell_list_contents(i) for i in next_moves]
                for obj in cell_list_contents:
                    if isinstance(obj, Prey) :
                        if obj.pos[0] > x:
                            x += 1
                        elif obj.pos[0] < x:
                            x -= 1
                        if obj.pos[1] > y:
                            y += 1
                        elif obj.pos[1] < y:
                            y -= 1
                        new_pos = x,y
                        not_moved = False
                        self.model.grid.move_agent(self, new_pos)
                        break

            #Si on a pas déjà bougé (spring condition)
            if not_moved :
                #S'il y a un prédateur,
                if predator:
                    # Prendre la position opposé.
                    obj = self.model.grid.get_cell_list_contents(predator_move)[0]

                    if obj.pos[0] < x:
                        x += 1
                    elif obj.pos[0] > x:
                        x -= 1

                    if obj.pos[1] < y:
                        y += 1
                    elif obj.pos[1] > y:
                        y -= 1

                    new_pos = x, y
                    self.model.grid.move_agent(self, new_pos)
                if hunter:                                                          #HUNTERMODIF to
                    # Prendre la position opposé.
                    obj = self.model.grid.get_cell_list_contents(hunter_move)[0]
                    if obj.pos[0] < x:
                        x += 1
                    elif obj.pos[0] > x:
                        x -= 1
                    if obj.pos[1] < y:
                        y += 1
                    elif obj.pos[1] > y:
                        y -= 1
                    new_pos = x, y
                    self.model.grid.move_agent(self, new_pos)
                                                                                    #HUNTERMODIF
                #Sinon, il va sur la nourriture.
                elif food:
                    self.model.grid.move_agent(self, food_move)
                #Sinon, on explore.
                else:
                    self.random_move()
                """
                #Sinon, il se rapproche d'un partenaire.
                elif reproduce:
                    self.model.grid.move_agent(self, reproduce_move)
                """

        ############################AGE/REPRODUCTION/ENERGIE############################
        living = True
        #self.model.grass représente l'option de nourriture sur la map.
        if self.model.grass:
            # Reduce energy.
            self.energy -= 1 #On décrémente l'énergie si et seulement si il y a de la nourriture sur la map.
            self.age += 1
            if self.model.schedule.steps%self.model.YEAR == 0 : # or self.model.schedule.steps%self.model.YEAR == self.model.YEAR*(3/4):
                self.reproduce = False
            # If there is grass available, eat it
            this_cell = self.model.grid.get_cell_list_contents([self.pos])
            grass_patch = [obj for obj in this_cell if isinstance(obj, Plant)]

            if self.energy < self.model.sheep_gain_from_food*4 : # le 100 correspond à deux fois le maximum du sheep_gain_from_food.
                if grass_patch != [] :
                    #Si la liste n'est pas vide, ça veut dire qu'il y a une plante "mature" sur la case.
                    self.energy += self.model.sheep_gain_from_food
                    grass_patch[0].fully_grown = False

            # Death
            if self.energy <= 0 or self.random.random() < 1/(4*self.model.YEAR) or self.age == 4*self.model.YEAR:
                self.model.grid._remove_agent(self.pos, self)
                self.model.schedule.remove(self)
                living = False

        #Reproduction du Lapin si vivant, si possible (probs) et s'il y a un autre lapin.
        prey = [obj for obj in this_cell if isinstance(obj, Prey)]
        #if living and self.age > self.model.YEAR/2  and self.random.random() < self.model.sheep_reproduce and len(prey) > 1:
        if living and self.age > self.model.YEAR/2 and self.random.random() < reproduce_prob and len(prey) > 1 and not self.reproduce:
            # Create a new rabbit:
            prey[1].reproduce = True
            self.energy /= 2
            self.reproduce = True
            litter = self.random.randrange(4, 8, 1) #WAS 1 12 at the beginning

            for i in range(litter):
                lamb = Prey(self.model.next_id(), self.pos, self.model, self.moore, int(self.energy/litter))
                self.model.grid.place_agent(lamb, self.pos)
                self.model.schedule.add(lamb)






class Predator(RandomWalker):
    """
    Species that walks around, reproduces (asexually) and eats prey.

    Problem when 2 predators meet at the beginning of spring and they stick with each other and do not eat anymore.
    N'y aurait t'il pas trop de contrainte sur les lapins pour que les loups s'épanouissent ? (Manque d'énergie limité chez les lapins quand +4 par carotte.)
    """
    def __init__(self, unique_id, pos, model, moore=True, energy=None, age=0):
        super().__init__(unique_id, pos, model)
        #attributes
        self.energy = energy
        self.age = age
        self.reproduce = False
        #self.speed = speed #new (Pour le nombre de mouvements qu'on peut faire à un tour, à implémenter

    def step(self):
        x, y = self.pos
        spring = False

        ############################INFLUENCE SAISON############################
        if self.model.schedule.steps%self.model.YEAR <= self.model.YEAR/4 and self.age > self.model.YEAR+4/2  :
            spring = True
            reproduce_prob = self.model.wolf_reproduce + 0.5
            if reproduce_prob > 1 :
                reproduce_prob = 1
        else :
            reproduce_prob = self.model.wolf_reproduce

        not_moved = True
        ############################CHOIX DES MOUVEMENTS############################
        if self.random.random() < 0.06:
            steps = 2
            if spring and not self.reproduce:
                steps = 4
            #mouvement aléatoire
            for i in range(steps):
              self.random_move()
              self.energy -= 1
            not_moved = False

        elif spring :
            for i in range(3):
                #regarde dans un rayon de 6 cases pour trouver un partenaire pour la BAISE
                next_moves = self.model.grid.get_neighborhood(self.pos, self.moore, False, 6)
                cell_list_contents = [self.model.grid.get_cell_list_contents(i) for i in next_moves]
                for obj in cell_list_contents:
                    if isinstance(obj, Predator):
                        if obj.pos[0] > x:
                            x += 1
                        elif obj.pos[0] < x:
                            x -= 1
                        if obj.pos[1] > y:
                            y += 1
                        elif obj.pos[1] < y:
                            y -= 1
                        new_pos = x,y
                        not_moved = False
                        self.model.grid.move_agent(self, new_pos)
                        self.energy -= 1
                        break



        if not_moved and self.energy < self.model.wolf_gain_from_food*4: ################################################################################################################################################
            for i in range(2):
                next_moves = self.model.grid.get_neighborhood(self.pos, self.moore, True)                                                    #HUNTERMODIF to
                for next_move in next_moves:
                    content_cell = self.model.grid.get_cell_list_contents(next_move)
                    content = [obj for obj in content_cell if isinstance(obj, Hunter)]
                    if len(content) > 0:
                        # on retient le mouvement.
                        hunter_move = next_move
                        # Prendre la position opposé.
                        obj = self.model.grid.get_cell_list_contents(hunter_move)[0]
                        if obj.pos[0] < x:
                            x += 1
                        elif obj.pos[0] > x:
                            x -= 1
                        if obj.pos[1] < y:
                            y += 1
                        elif obj.pos[1] > y:
                            y -= 1
                        new_pos = x, y
                        not_moved = False
                        self.model.grid.move_agent(self, new_pos)
                        break
                                                                                        #HUNTERMODIF
            if not_moved:
                for i in range(2):
                    #regarde dans un rayon de 3 cases autour de lui et avance vers une proie s'il y en a une dans ce rayon
                    next_moves = self.model.grid.get_neighborhood(self.pos, self.moore, False, 3)
                    cell_list_contents = [self.model.grid.get_cell_list_contents(i) for i in next_moves]
                    for obj in cell_list_contents:
                        if isinstance(obj, Prey):
                            if obj.pos[0] > x:
                                x += 1
                            elif obj.pos[0] < x:
                                x -= 1
                            if obj.pos[1] > y:
                                y += 1
                            elif obj.pos[1] < y:
                                y -= 1
                            new_pos = x,y
                            not_moved = False
                            self.model.grid.move_agent(self, new_pos)
                            self.energy -= 1
                            break

                #s'il n'y a pas de proies autour de lui, le prédateur fait un mouvement aléatoire
            if not_moved:
                self.energy -= 1
                self.random_move()
        if not spring :
            self.reproduce = False
        ############################AGE/REPRODUCTION/ENERGIE############################

        self.age += 1 #new
        if self.model.schedule.steps%self.model.YEAR == 0:
            self.reproduce = False
        # If there is a prey present, eat one
        this_cell = self.model.grid.get_cell_list_contents([self.pos])
        prey = [obj for obj in this_cell if isinstance(obj, Prey)]
        if self.energy < self.model.wolf_gain_from_food*2:
            #if len(prey) > 0 and self.random.random() < 2/3:
            if len(prey) > 0:
                prey_to_eat = self.random.choice(prey)
                self.energy += self.model.wolf_gain_from_food
                # Kill the prey
                self.model.grid._remove_agent(self.pos, prey_to_eat)
                self.model.schedule.remove(prey_to_eat)

        if self.random.random() < 1/(5*self.model.YEAR) or self.energy <= 0 or self.age == 5*self.model.YEAR:
        #if self.energy <= 0 or self.age == 5*self.model.YEAR:
            #print(str(self.age/(6*self.model.YEAR)) + " proba de mort")
            self.model.grid._remove_agent(self.pos, self)
            self.model.schedule.remove(self)
        else:
            predator = [obj for obj in this_cell if isinstance(obj, Predator)]
            #S'il y a un autre prédateur et que le reproduce_prob est supérieur au random, alors on peut se reproduire.
            #if self.age > self.model.YEAR+4/2 and self.random.random() < reproduce_prob and len(predator) > 1 :
            if self.age > self.model.YEAR/2 and self.random.random() < reproduce_prob and len(predator) > 1 and not self.reproduce:
                #print(self.pos, self.model.schedule.steps)
                # Create a new fox cub
                self.energy /= 2
                self.reproduce = True
                predator[1].reproduce = True
                litter = self.random.randrange(2,5,1)
                #if int(self.energy/litter) > 4 :
                for i in range(litter):
                    cub = Predator(self.model.next_id(), self.pos, self.model, self.moore, int(self.energy/litter))
                    self.model.grid.place_agent(cub, cub.pos)
                    self.model.schedule.add(cub)
