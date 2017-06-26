from .team import *
from Battle import *
from Dialgarithm import *
from functools import wraps


class Metagame:
    def __init__(self):
        self.dex = Dialgarithm.gen
        self.format = Dialgarithm.format
        self.dict_of_team_elo = {}
        self.beta_offense = 0
        self.beta_defense = 0

    def generate_team(self, core=[]):
        num_teammates = 6 - len(core)
        attempt = [Team.weighted_sample() for i in range(0, num_teammates)]
        attempt += core
        new_team = Team([], attempt)
        if new_team.is_valid():
            if len(list(set([mon.pokemon.dex_name for mon in attempt]))) < 6:
                print([mon.pokemon.dex_name for mon in attempt])
                raise ValueError("Not a valid team!")
            return new_team
        else:
            return self.generate_team(core)  # this can be optimized

    def time_function(f):
        @wraps(f)
        def wrapped(inst, *args, **kwargs):
            tick = time.clock()
            result = f(inst, *args, **kwargs)
            print("PROCESS TOOK: " + str(time.clock() - tick))
            return result

        return wrapped

    @time_function
    def precomputation(self):
        """generates teams, battles them over 24 hours,
        gets regression from expectations -> Elo"""
        print("GENERATING TEAMS!")
        number_of_teams = Dialgarithm.population_size
        starting_elo = 1000
        self.dict_of_team_elo =\
            {self.generate_team(Dialgarithm.core): starting_elo for i
             in range(0, number_of_teams)}
        # teams should be 2.4 hr / (time per game)
        tick = time.clock()
        seconds_spent = Dialgarithm.time
        counter = 0

        # damage - 1800, switch - 1000

        def sample_by_elo(elo_distribution):
            r = random.uniform(0, 1000 * number_of_teams)
            runner = 0
            for key, value in elo_distribution.items():
                if runner + value >= r:
                    return key
                runner += value
            assert False, "Shouldn't get here"

        # each cycle takes roughly 15 seconds
        print("BEGINNING CYCLES")
        while time.clock() - tick < seconds_spent:
            for i in range(0, 30):
                counter += 1
                # sort by elo
                bracket = sorted(self.dict_of_team_elo,
                                 key=self.dict_of_team_elo.get)
                # pair off and battle down the line
                for i in range(0, number_of_teams // 2):
                    team1 = bracket[2 * i]
                    team2 = bracket[2 * i + 1]
                    self.run_battle(team1, team2)
            print("NEW POPULATION")
            winners = [sample_by_elo(self.dict_of_team_elo) for i
                       in range(0, number_of_teams)]
            self.dict_of_team_elo =\
                {team.reproduce(): self.dict_of_team_elo[team]
                 for team in winners}

        print("DONE BATTLING, ANALYZING")
        [t.analyze() for t in self.dict_of_team_elo.keys()]
        suggestions = sorted(self.dict_of_team_elo,
                             key=self.dict_of_team_elo.get)[0:3]
        print("SUGGESTIONS:")
        for suggestion in suggestions:
            suggestion.display()
            
    @staticmethod
    def compute_expected(elo1, elo2):
        return 1 / (1 + 10.0 ** ((elo2 - elo1) / 400.0))

    # TODO
    def run_battle(self, team1, team2):
        elo1 = self.dict_of_team_elo[team1]
        elo2 = self.dict_of_team_elo[team2]
        expected_1 = Metagame.compute_expected(elo1, elo2)
        expected_2 = Metagame.compute_expected(elo2, elo1)
        # determine winner
        winner = Battle.battle(team1, team2)
        if elo1 > 1500 or elo2 < 500:
            k = 16
        else:
            k = 32
        if winner is team1:
            s_1 = 1
            s_2 = 0
        else:
            s_1 = 0
            s_2 = 1
        self.dict_of_team_elo[team1] += k * (s_1 - expected_1)
        self.dict_of_team_elo[team2] += k * (s_2 - expected_2)