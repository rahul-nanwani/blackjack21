# MIT License
#
# Copyright (c) 2022 Rahul Nanwani
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

class PlayerBase:
    # noinspection PyUnresolvedReferences
    def __init__(self, name: str, bet: int, table: 'Table'):
        """
        Create split player for the table
        :param name: str
        :param bet: int
        :param table: object instance
        """
        self.name = name
        self.bet = bet
        self.hand = []
        self.bust = False
        self.stand = False
        self._table = table

    @property
    def total(self) -> int:
        total = 0
        values = []
        for card in self.hand:
            # noinspection PyProtectedMember
            values.append(card._value)
        aces = values.count(11)
        for value in values:
            total += value
            while aces > 0 and total > 21:
                total -= 10
                aces -= 1

        return total

    @property
    def result(self) -> int:
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
        if (self.bust or self.stand) and (self._table.dealer.bust or self._table.dealer.stand):
            if self.bust:
                return -2
            elif self.total < self._table.dealer.total and not self._table.dealer.bust:
                return -1
            elif self.total == 21:
                return 1
            elif self.total > self._table.dealer.total:
                return 2
            elif self.total < self._table.dealer.total and self._table.dealer.bust:
                return 3
            else:
                return 0

    # noinspection PyUnresolvedReferences
    def play_hit(self) -> 'Card':
        """
        Deals another card to the player if the player is not busted or has played stand
        :return: Card object
        """
        if not (self.stand or self.bust):
            card = self._table.deck.pop()
            self.hand.append(card)
            if self.total > 21:
                self.bust = True
            elif self.total == 21:
                self.stand = True
            return card

    def play_stand(self) -> bool:
        """
        Stop further dealing any cards to the player before being busted.
        :return: bool
        """
        if not self.bust:
            self.stand = True
            return True
        return False


class Player(PlayerBase):
    # noinspection PyUnresolvedReferences
    def __init__(self, name: str, bet: int, table: 'Table'):
        """
        Create player for the table
        :param name: str
        :param bet: int
        :param table: object
        """
        super().__init__(name, bet, table)
        self.split = False

    @property
    def can_double_down(self) -> bool:
        return True if (len(self.hand) == 2 and not self.split) else False

    @property
    def can_split(self) -> bool:
        if len(self.hand) == 2:
            ranks = []
            for card in self.hand:
                ranks.append(card.rank)
            if ranks[0] == ranks[1]:
                return True
        return False

    # noinspection PyUnresolvedReferences
    def play_double_down(self) -> 'Card':
        """
        Double down can be played only on the first turn by doubling the bet amount and will hit only once
        :return: Card object
        """
        if self.can_double_down:
            self.bet *= 2
            card = self.play_hit()
            self.play_stand()
            return card

    def play_split(self) -> 'PlayerBase':
        """
        Split can be played only on the first turn by splitting the hand if both the cards have the same ranks.
        The bet will remain the same on both the hands.
        If the player bets 100 initially, so after playing split the player will have placed 100 on first hand,
        and 100 more on the second hand.
        :return: Player object
        """
        if self.can_split:
            self.split = PlayerBase(self.name, self.bet, self._table)
            self.split.hand.append(self.hand.pop())
            return self.split


class Dealer:
    # noinspection PyUnresolvedReferences
    def __init__(self, name: str, table: 'Table'):
        """
        Create a dealer for the table
        :param name: str
        """
        self.name = name
        self.hand = []
        self.bust = False
        self.stand = False
        self._table = table

    @property
    def __hands_played(self) -> bool:
        for player in self._table.players:
            if not (player.bust or player.stand):
                return False
            if player.split:
                if not (player.split.bust or player.split.stand):
                    return False
        return True

    @property
    def total(self) -> int:
        if self.__hands_played:
            total = 0
            values = []
            for card in self.hand:
                # noinspection PyProtectedMember
                values.append(card._value)
            aces = values.count(11)
            for value in values:
                total += value
                while aces > 0 and total > 21:
                    total -= 10
                    aces -= 1

            return total
        # noinspection PyProtectedMember
        return self.hand[0]._value

    # noinspection PyUnresolvedReferences
    def __play_hit(self) -> 'Card':
        """
        Deals another card to the dealer if the dealer is not busted or has played stand
        :return: Card object
        """
        if not (self.stand or self.bust):
            card = self._table.deck.pop()
            self.hand.append(card)
            if self.total > 21:
                self.bust = True
            elif self.total == 21:
                self.stand = True
            return card

    def _deal_cards(self) -> bool:
        """
        After initializing the table deal the cards to all the players and the dealer.
        The dealer will have 2 cards in hand but total will be returned only for the first card.
        Second card will be revealed only after the result.
        :return: True if dealt successfully, else False
        """
        if len(self._table.players) > 0:
            self.__play_hit()

            for player in self._table.players:
                player.play_hit()
            for player in self._table.players:
                player.play_hit()

            self.__play_hit()

            return True
        return False

    def play_dealer(self) -> bool:
        """
        Play the dealer once everyone has played their hands
        :return: True if hand is successfully played, else False
        """
        if self.__hands_played:
            totals = []
            for player in self._table.players:
                totals.append(player.total)
            highest_total = max(totals)

            while self.total < 17 and self.total < highest_total:
                self.__play_hit()
            if self.total > 21:
                self.bust = True
            else:
                self.stand = True
            return True
        return False
