class PlayerBase:
    def __init__(self, name: str, bet: int, table):
        """
        Create split player for the table
        :param name: str
        :param bet: int
        :param table: object
        """
        self.name = name
        self.bet = bet
        self.hand = []
        self.bust = False
        self.stand = False
        self.__table = table

    @property
    def total(self):
        total = 0
        values = []
        aces = values.count(11)
        for card in self.hand:
            values.append(card._value)
        for value in values:
            total += value
            while aces > 0 and total > 21:
                total -= 10
                aces -= 1

        return total

    @property
    def result(self):
        """
        Result for the player once the player is bust or stands.
        Negative implies the player loses, positive implies the player wins, and 0 implies a draw.
        The key below shows the reasons for the result:
        -2: Player busts
        -1: Player has less than the dealer
        0: Player has the same total as the dealer and both are not bust
        1: Player has 21 (aka. blackjack)
        2: Player has greater total than the dealer
        3: The dealer is bust
        None: player or dealer has not finished playing their hand yet
        """
        if (self.bust or self.stand) and (self.__table.dealer.bust or self.__table.dealer.stand):
            if self.bust:
                return -2
            elif self.total < self.__table.dealer.total and not self.__table.dealer.bust:
                return -1
            elif self.total == 21:
                return 1
            elif self.total > self.__table.dealer.total:
                return 2
            elif self.total < self.__table.dealer.total and self.__table.dealer.bust:
                return 3
            else:
                return 0
        return None

    def play_hit(self):
        """
        Deals another card to the player if the player is not busted or has played stand
        :return: Card object
        """
        if not (self.stand or self.bust):
            card = self.__table.deck.pop()
            self.hand.append(card)
            if self.total > 21:
                self.bust = True
            elif self.total == 21:
                self.stand = True
            return card

    def play_stand(self):
        """
        Stop further dealing any cards to the player before being busted.
        :return: bool
        """
        if not self.bust:
            self.stand = True
            return True
        return False


class Player(PlayerBase):
    def __init__(self, name: str, bet: int, table):
        """
        Create player for the table
        :param name: str
        :param bet: int
        :param table: object
        """
        super().__init__(name, bet, table)
        self.split = False

    def can_double_down(self):
        """
        Check if the player can play double down
        :return: bool
        """
        return True if (len(self.hand) == 2 and not self.split) else False

    def can_split(self):
        """
        Check if the player can play split
        :return: bool
        """
        if len(self.hand) == 2:
            ranks = []
            for card in self.hand:
                ranks.append(card.rank)
            if ranks[0] == ranks[1]:
                return True
        return False

    def play_double_down(self):
        """
        Double down can be played only on the first turn by doubling the bet amount and will hit only once
        :return: Card object
        """
        if self.can_double_down():
            self.bet *= 2
            card = self.play_hit()
            self.play_stand()
            return card

    def play_split(self):
        """
        Split can be played only on the first turn by splitting the hand if both the cards have the same ranks.
        The bet will remain the same on both the hands.
        If the player bets 100 initially, so after playing split the player will have placed 100 on first hand,
        and 100 more on the second hand.
        :return: Player object
        """
        if self.can_split():
            self.split = PlayerBase(self.name, self.bet, self.__table)
            self.split.hand.append(self.hand.pop())
            return self.split


class Dealer:
    def __init__(self, name, table):
        """
        Create a dealer for the table
        :param name: str
        """
        self.name = name
        self.hand = []
        self.bust = False
        self.stand = False
        self.__table = table
        self.__play_hand = False

    @property
    def total(self):
        if not self.__play_hand:
            return self.hand[0]._value
        else:
            total = 0
            values = []
            aces = values.count(11)
            for card in self.hand:
                values.append(card._value)
            for value in values:
                total += value
                while aces > 0 and total > 21:
                    total -= 10
                    aces -= 1

            return total

    def __play_hit(self):
        """
        Deals another card to the dealer if the dealer is not busted or has played stand
        :return: Card object
        """
        if not (self.stand or self.bust):
            card = self.__table.deck.pop()
            self.hand.append(card)
            if self.total > 21:
                self.bust = True
            elif self.total == 21:
                self.stand = True
            return card

    def deal_cards(self):
        """
        After initializing the table deal the cards to all the players and the dealer.
        The dealer will have 2 cards in hand but total will be returned only for the first card.
        Second card will be revealed only after the result.
        :return: True if dealt successfully, else False
        """
        if len(self.__table.players) > 0:
            self.__play_hit()

            for player in self.__table.players:
                player.play_hit()
            for player in self.__table.players:
                player.play_hit()

            self.hand.append(self.__table.deck.pop())

            return True
        else:
            return False

    def play_dealer(self):
        """
        Play the dealer once everyone has played their hands
        :return: None
        """
        self.__play_hand = True
        totals = []
        for player in self.__table.players:
            totals.append(player.total)
        highest_total = max(totals)

        while self.total < 17 and self.total < highest_total:
            self.__play_hit()
        if self.total > 21:
            self.bust = True
        else:
            self.stand = True
        return None
