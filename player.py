import constants


class Player:
    def __init__(self):
        self.score = 0
        self.favourite_singers = []

    def initialize_favourite_singers(self):
        print(f"Please insert your {constants.AMOUNT_OF_SINGERS_INPUT} favourite bands / singers:")
        for i in range(constants.AMOUNT_OF_SINGERS_INPUT):
            singer_name = input()
            self.favourite_singers.append(singer_name)
