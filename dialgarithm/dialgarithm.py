# from .model_local import Model
from .usage_reader import *
from .dex_factory import *
from .moveset_factory import *
from .damage import *
from .metagame import *
from .evolve import *


# import random

def setup_with_user_input():
    UsageReader.select_meta()
    DexFactory().get_dex()
    UsageReader.clean_up_usage()
    MovesetFactory().get_movesets()
    Damage.start()
    # generate normies if necessary
    Metagame.generate_norms()
    prompt_core()


def setup_without_user_input():
    UsageReader.assign_meta()
    DexFactory().get_dex()
    UsageReader.clean_up_usage()
    MovesetFactory().get_movesets()
    Damage.start()
    # generate normies if necessary
    Metagame.generate_norms()
    prompt_core()


def test_speed():
    tick = time.clock()
    for _ in range(1000):
        norms = [key for key in Model.elo_dict]
        a = np.random.choice(norms)
        b = np.random.choice(norms)
        Damage.battle(a, b)
    print("1000 battles took:", time.clock() - tick)


def evolve():
    Evolve().evolve()


def output():
    # Damage.end()
    [print(team) for team in Evolve.output]
    Evolve.write_to_file()


def prompt_core():
    core_size = int(input("How big is your core? (0-5) \n"))
    if core_size < 0 or core_size > 5:
        raise ValueError("Bad core size!")
    for i in range(1, core_size + 1):
        flag = True
        while flag:
            name = input("Name of Pokemon " + str(i) + "?\n")
            potential_movesets = [mon for mon in Model.moveset_list
                                  if mon.pokemon.unique_name == name]
            if len(potential_movesets) > 0:
                if name == 'Ditto':
                    print('Ditto not supported.  Try again!')
                    flag = True
                else:
                    Model.core.append(potential_movesets)
                    flag = False
            else:
                print("No Smogon analysis for this Pokemon!\nIt probably sucks!  Try again!")
    # Model.population_size = int(input("Population size? (>3) \n"))
    # Model.time = int(input("Evolution duration?\n"))
    print("Inputs processed!")
