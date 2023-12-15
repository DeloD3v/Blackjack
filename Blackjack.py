import random
import sys
from os import system

class Card:
    HEARTS   = chr(9829) # Character 9829 is '♥'.
    DIAMONDS = chr(9830) # Character 9830 is '♦'.
    SPADES   = chr(9824) # Character 9824 is '♠'.
    CLUBS    = chr(9827) # Character 9827 is '♣'.
    seme_map = {"hearts": HEARTS, "diamonods": DIAMONDS, "spades": SPADES, "clubs": CLUBS}
    value_map = {1: "A", 11: "J", 12: "Q", 13: "K"}
    
    def __init__(self, suit, value):
        self.suit = suit.lower()
        self.value = value

    def string_card(self):
        '''Return a vector of strings that if it is printed it display the card. This is necessary in order to
        concatenate two or more cards and display in a row way'''
        seme = Card.seme_map[self.suit]
        if self.value == 1 or self.value > 10: 
            value = Card.value_map[self.value]
        else:
            value = self.value
        cards = []

        # Since 10 is composed by two characters we have to adjust the dimension of the card in order to have the 
        # same dimensions among all the cards
        if value == 10:
            cards.append(" ___  ")
            cards.append("|{} | ".format(value))
            cards.append("| {} | ".format(seme))
            cards.append("|_{}| ".format(value))            
        else:
            cards.append(" ___  ")
            cards.append("|{}  | ".format(value))
            cards.append("| {} | ".format(seme))
            cards.append("|__{}| ".format(value))
        return cards
    
class Deck:
    def __init__(self):
        self.deck = []
        for seme in Card.seme_map:
            for i in range(1,14):
                card = Card(seme, i)
                self.deck.append(card)
    
    def shuffle(self):
        'Reset the deck and shuffle it'
        # Reset of the deck
        self.__init__()
        # Shuffle the deck
        random.shuffle(self.deck)
    
class TablePlayer():
    def __init__(self):
        self.hand = []
        self.handValue = self._hand_value()
        self.bust = False

    def _hand_value(self):
        value_list = []
        for card in self.hand:
            value_list.append(card.value)
        for i in range(len(value_list)):
            if value_list[i] > 10: value_list[i] = 10
            if value_list[i] == 1: value_list[i] = 11
        count = sum(value_list)
        if count > 21:
            while (count>21) and (11 in value_list):
                ace_index = value_list.index(11)
                value_list[ace_index] = 1
                count -= 10
        return count

    def displayHand(self):
        cards = ['']*4
        for card in self.hand:
            card_string = card.string_card()
            for i in range(4):
                cards[i] += card_string[i]
        for row in cards:
            print(row)

    def draw(self, deck):
        self.hand.append(deck.deck.pop())
        self.handValue = self._hand_value()
    
class Dealer(TablePlayer):
    card_string_faceDown = ['' ,'|## | ', '|###| ', '|_##| ']

    def __init__(self):
        super().__init__()

    def play(self, deck):
        self.hand = []
        self.handValue = 0
        self.bust = False
        while self.handValue<17:
            super().draw(deck)
            if self.handValue > 21:
                self.bust = True

    def displayHand(self):
        cards = self.hand[0].string_card()
        for i in range(4):
            cards[i] += Dealer.card_string_faceDown[i]
        for row in cards:
            print(row)

    # def displayHand(self):
    #     cards = self.hand[1].string_card()
    #     for card in self.hand[1:]:
    #         for i in range(4):
    #             cards[i] += Dealer.card_string_faceDown[i]
    #     for row in cards:
    #         print(row) 

    # def display2cards(self):
    #     cards = ['']*4
    #     for j in range(2):
    #         card_string = self.hand[j].string_card()
    #         for i in range(4):
    #             cards[i] += card_string[i]
    #     for row in cards:
    #         print(row)

class Player(TablePlayer):
    valid_move = ('H', 'S', 'D')
    valid_move_wihout_double = ('H', 'S')

    def __init__(self):
        super().__init__()
        self.money = 5000
        self.bet = 0
        self.bankrupt = False
        
    def getMove(allowed_moves):
        print()
        move = input("(H)its, (S)tand, (D)ouble down ")
        move = move.upper()
        while move not in allowed_moves:
            move = input("(H)its, (S)tand, (D)ouble down ")
            move = move.upper()
        return move
    
    getMove = staticmethod(getMove)

    # I have to manage the bet here and not a Table level because otherwise I cannot stop a player to doubling
    # down when he hasn't suffiecint money to cover this move
    def getBet(self):
        while True:
            print("Money %s" %self.money)
            bet = input('How much do you bet? ')
            if not bet.isdecimal():
                continue
            bet = int(bet)
            if self.money < bet:
                print("You haven't enough money")
                continue
            else:
                self.money -= bet
                self.bet = bet
                break
        
    def play(self, deck):
        self.hand = []
        self.handValue = 0
        self.bust = False
        self.getBet()
        # Initial hand  of a player
        super().draw(deck)
        super().draw(deck)
        super().displayHand()
        move = Player.getMove(Player.valid_move)
        if move == 'D':
            if self.money >= self.bet:
                self.money -= self.bet
                self.bet += self.bet
                super().draw(deck)
                super().displayHand()
                if self.handValue > 21:
                    self.bust = True
            else:
                print("You haven't enough money to do a double down")
                print("What other move you want to do?")
                move = Player.getMove(Player.valid_move_wihout_double)
                
        if move != 'D':
            while move == 'H' and self.handValue<=21:
                super().draw(deck)
                super().displayHand()
                # If the player exceed 21 it lose and it is useless to ask its next move
                if self.handValue<=21:
                    move = Player.getMove(Player.valid_move_wihout_double)
                else:
                    self.bust = True
    
class Table:
    def __init__(self):
        self.player = Player()
        self.dealer = Dealer()
        self.deck = Deck()

    def check_winner(self):
        '''Return "player" if the player has won, "dealer" if the dealer has won and tie if if the player and
         the dealer have the same value'''
        # First check if someone has busted
        if self.player.bust:
            return "dealer"
        if self.dealer.bust:
            return "player"
        if self.player.handValue > self.dealer.handValue:
            return "player"
        if self.player.handValue < self.dealer.handValue: 
            return "dealer"
        # If here we may have a draw
        if self.player.handValue == 21 and (len(self.player.hand) == 2 or len(self.dealer.hand) == 2):
            # Someone have a blackjack
            if len(self.player.hand) == 2 and len(self.dealer.hand) == 2:
                return 'tie'
            elif len(self.player.hand) == 2:
                return 'player'
            else:
                return 'dealer'
        else:
            return 'tie'

    def check_bankrupt(self):
        'Update the value bankrupt to True if the player has no more money'
        if self.player.money <= 0:
            self.player.bankrupt = True

    def turn(self):
        self.dealer.play(self.deck)
        print("Dealer's hand")
        self.dealer.displayHand()
        print()
        self.player.play(self.deck)
        winner = self.check_winner()
        print("Dealer's hand")
        super(Dealer, self.dealer).displayHand()
        print()
        if winner == "tie":
            print("It is a draw")
        else:
            print("%s win" %winner)
        self.update(winner)
        self.check_bankrupt()
    
    def update(self, winner):
        'Given the winner, update the value of the player playing at the table'
        if winner == "player":
            self.player.money += self.player.bet*2
        elif winner == "tie":
            self.player.money += self.player.bet
        self.player.bet = 0
        return

    def play_the_game(self):
        self.deck.shuffle()
        while not self.player.bankrupt:
            self.turn()
            if len(self.deck.deck) < 15:
                print()
                print("The deck is shuffled")
                print()
                self.deck.shuffle()
            if not self.player.bankrupt:
                another = input("Press Enter if you want to play another hand ")
                if another.upper() != '':
                    sys.exit(0)
            system('cls')
        if self.player.bankrupt:
            print("You lose all your money! At least not for real")

def main():
    table = Table()
    table.play_the_game()

if __name__ == "__main__":
 main()



