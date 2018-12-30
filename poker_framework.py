

#HAND FRAMEWORK
import random

def create_deck():
    deck = []
    suits = ['H','S','D','C']
    for suit in suits:
        deck.extend([x+suit for x in ['14','13','12','11','10','09','08','07','06','05','04','03','02']])
    return deck

def pick_random(deck):
    size = len(deck)
    randInt = random.randint(0,size-1)
    card = deck.pop(randInt)
    return card


def get_tiebreak(num_cards,excludes,hand):
    ret = excludes
    numExc = len(excludes)
    hand.sort(key=lambda x: int(x[:2]))
    ind = len(hand)-1
    while len(ret) < num_cards+numExc and ind >= 0:
        highCard = int(hand[ind][:2])
        if highCard not in ret:
            ret.append(highCard)
        ind-=1
    return ret
        

def get_top_hand(flop,hand,printBest=False):
    
    totals = flop + hand
    
    try:
        totals.sort(key=lambda x: int(x[:2]))
    except ValueError:
        print('ERROR: Incorrect Card Format.')
        return
    
    high_card = int(totals[len(totals)-1][:2])
    second_highest = int(totals[len(totals)-2][:2])
    
    #Hand Analysis
    suits = {'H':[],'S':[],'D':[],'C':[]}
    mults = {}
    
    #add suits, mulitples
    for card in totals:
        c_number = int(card[:2])
        c_suit = card[2]
        
        suits[c_suit].append(c_number)
        mults.setdefault(c_number,0)
        mults[c_number]+=1
    
    
                

    #Check for flush
    straight = []
    flushBool = False
    topSuitCard = None
    flushCards = None

    for s_cards in suits.values():
        if len(s_cards) >= 5:
            flushBool = True
            flushCards = list(reversed(s_cards))
            #check for straight flush
            straight=[]
            straightBool=False
            if 14 in s_cards:
                s_cards.insert(0,1)
            
            for num in s_cards:
                if len(straight) == 0:
                    straight.append(num)
                elif num == straight[len(straight)-1]:
                    continue
                elif num == straight[len(straight)-1] + 1:
                    straight.append(num)
                    if len(straight) >= 5:
                        straightBool = True
                elif straightBool==False:
                    straight = [num]
            
    
    #check for straight          
    if flushBool == False:
        straightBool = False
        straight = []
        card_nums = []
        for card in totals:
            c_number = int(card[:2])
            card_nums.append(c_number)
            if c_number == 14:
                card_nums.insert(0,1)
                
        for num in card_nums:
            if len(straight) == 0:
                straight.append(num)
            elif num == straight[len(straight)-1]:
                continue
            elif num == straight[len(straight)-1] + 1:
                straight.append(num)
                if len(straight) >= 5:
                    straightBool = True
            elif straightBool==False:
                straight = [num]
    
    
    if 1 in straight and 13 in straight:
        straight.append(14)
            
      
    #(card number, how many)
    bestMult = (None,0)
    secondBest = (None,0)
    for card,num in mults.items():
        if num > bestMult[1]:
            secondBest = bestMult
            bestMult = (card,num)
        
        elif num == bestMult[1]:
            if card > bestMult[0]:
                secondBest = bestMult
                bestMult = (card,num)
        else:
            if num > secondBest[1]:
                secondBest = (card,num)
            elif num == secondBest[1] and card > secondBest[0]:
                secondBest = (card,num)
                

    #look for best hand
    hand = (None,None)
    if straightBool and flushBool:
        hand = [9,straight[len(straight)-1]]
    elif bestMult[1] == 4:
        hand = [8] + get_tiebreak(1,[bestMult[0]],totals)
    elif bestMult[1] == 3 and secondBest[1] == 2:
        hand = [7,bestMult[0],secondBest[0]]
    elif flushBool:
        hand = [6,*flushCards]
    elif straightBool:
        hand = [5,straight[len(straight)-1]]
    elif bestMult[1] == 3:
        hand = [4] + get_tiebreak(2,[bestMult[0]],totals)
    elif bestMult[1] == 2 and secondBest[1] == 2:
        hand =  [3] + get_tiebreak(1,[bestMult[0],secondBest[0]],totals)
    elif bestMult[1] == 2:
        hand = [2] + get_tiebreak(3,[bestMult[0]],totals)
    else:
        hand = [1] + get_tiebreak(5,[],totals)
    return hand



#hands is a list of (get_top_hand,player_name) tuples
def get_winner(hands):
    winHand = None
    winPlayers = []

    for hand,player in hands:
        if winHand == None:
            winHand = hand
            winPlayers.append(player)
        else:
            if winHand == hand:
                winPlayers.append(player)
            else:
                for ind in range(len(winHand)):
                    if hand[ind] > winHand[ind]:
                        winHand = hand
                        winPlayers = [player]
                        break
                    elif hand[ind] < winHand[ind]:
                        break
    return winPlayers





#GAME FRAMEWORK
class player:
    def __init__(self,initial_chips,name):
        self.chips = initial_chips
        self.name = name
        self.hand = None
        self.in_hand = True
        self.chips_in_pot = 0
        self.current_bet = 0
        self.previous_bet = 0
        
    
    def reset(self):
        self.hand = None
        self.in_hand = True
        self.current_bet = 0
        self.previous_bet = None
        self.chips_in_pot = 0
         
    
    #returns the strength of input_hand
    #strength = num of winning hands / hand possibilities
    def get_hand_strength(self,input_flop=[]):
        deck = create_deck()
        my_hand = (get_top_hand(input_flop, self.hand),'me')
        deck.remove(self.hand[0])
        deck.remove(self.hand[1])

        for card in input_flop:
            deck.remove(card)

        visited_hands = []
        losses = 0
        for card1 in deck:
            for card2 in deck:
                if card1 != card2 and [card1,card2] not in visited_hands:
                    visited_hands.append([card1,card2])
                    visited_hands.append([card2,card1])
                    other_hand = (get_top_hand([card1,card2],input_flop),'other')
                    winners = get_winner([my_hand,other_hand])
                    if 'me' not in winners:
                        losses+=1
        total_hands = len(deck)*len(deck)/2                
        return round(100*(total_hands-losses) / total_hands,2)
    

    def get_num_losing_hands(self,input_flop):
        deck = create_deck()
        my_hand = (get_top_hand(input_flop, self.hand),'me')
        deck.remove(self.hand[0])
        deck.remove(self.hand[1])

        for card in input_flop:
            deck.remove(card)

        visited_hands = []
        losses = 0
        for card1 in deck:
            for card2 in deck:
                if card1 != card2 and [card1,card2] not in visited_hands:
                    visited_hands.append([card1,card2])
                    visited_hands.append([card2,card1])
                    other_hand = (get_top_hand([card1,card2],input_flop),'other')
                    winners = get_winner([my_hand,other_hand])
                    if 'me' not in winners:
                        losses+=1
        return losses
    
    #what rank are you in chips compared to your opponents
    def get_chip_rank(self,other_players):
        rank = 1
        for player in other_players:
            if player.chips > self.chips:
                rank+=1
        return rank
    
    def all_in_decision(self,invested,hand_strength):
        if invested >= 90:
            return True
        elif invested >= 50 and hand_strength >= 75:
            return True
        elif hand_strength >= 90:
            return True
        else:
            return False
    
    #player is comsidered dominated if you have more chips than him * ratio
    #returns the number of chips needed to put the most powerful dominated player all-in
    #if no player is dominated returns None
    def get_dominated_players(self,other_players):
        num_dominated_chips = None
        ratio = 10
        for player in other_players:
            if player.chips * ratio < self.chips:
                if num_dominated_chips:
                    if player.chips > num_dominated_chips:
                        num_dominated_chips = player.chips
                else:
                    num_dominated_chips = player.chips
        return num_dominated_chips
    
    def make_decision(self,other_players,min_bet,input_flop=[],printInfo=False):
        hand_strength = self.get_hand_strength(input_flop=input_flop)
        
        if len(input_flop) == 0:
            bet =  self.pre_flop_strategy(min_bet,hand_strength)
        else:
            if len(input_flop) == 3:
                bet = self.round_1_strategy(min_bet,other_players,hand_strength)
            elif len(input_flop) == 4:
                bet = self.round_1_strategy(min_bet,other_players,hand_strength)
            elif len(input_flop) == 5:
                bet = self.round_1_strategy(min_bet,other_players,hand_strength)
        
        if bet > self.chips:
            bet = self.chips
        if printInfo:
            print('Player = {}   Hand Strength = {}    Bet = {}'.format(self.name,hand_strength,bet))  
        return bet
    
    
    
    
    #generic pre-flop strategy
    def pre_flop_strategy(self,min_bet,hand_strength):
        if hand_strength > 85:
            return min_bet*2
        elif hand_strength > 60:
            return min_bet
        else:
            return 0
        
        
    def round_1_strategy(self,min_bet,other_players,hand_strength):
        chip_rank = self.get_chip_rank(other_players)
        dominated_players = self.get_dominated_players(other_players)
        min_bet_ratio = min_bet/self.chips
        confidence_ratio = hand_strength * (1-min_bet_ratio)
        percent_chips_invested = 100*self.chips / (self.chips_in_pot+self.chips)
        
        #must go all in
        if min_bet >= self.chips:
            if self.all_in_decision(percent_chips_invested,hand_strength) == True:
                return min_bet
            else:
                return 0
        if min_bet > 0:
            if confidence_ratio >= 80 or hand_strength >= 90:
                return min_bet*3
            elif confidence_ratio >= 75 or hand_strength >= 80:
                return min_bet*2
            elif 100*min_bet_ratio <= 20 and hand_strength >= 70:
                return min_bet
            elif 100*min_bet_ratio <= 10 and hand_strength >= 60:
                return min_bet
            else:
                return 0
        else:
            if hand_strength >= 90:
                return min_bet*3
            elif hand_strength >= 80:
                return min_bet*2
            elif hand_strength >= 70:
                return min_bet + int(self.chips/10)
            elif hand_strength >= 60:
                return min_bet + int(self.chips/20)
            else:
                return 0
            

        
    #def round_2_strategy(self,min_bet,other_players,hand_strength):
        
    #def river_strategy(self,min_bet,other_players,hand_strength):
        
    
    def make_bet(func):
        def wrapper(func):
            self.previous_bet = func()
        return wrapper

    #@make_bet
    #def value_bet(self,min_bet,other_players):
    
    #@make_bet
    #def bluff(self,min_bet,other_players):
    
    #@make_bet
    #def continuation_bet(self,previous_bet):
    
    

class poker_game:
    def __init__(self,num_players,initial_chips,printInfo=False):
        names = ['Frank','Dee','Mac','Charlie','Dennis','Franquito','Margaret','Rickety Cricket','Artemis']
        
        self.pot = 0
        self.deck = create_deck()
        self.flop = []
        self.printInfo = printInfo
        
        self.players = []#[player(initial_chips=initial_chips, name='me')]
        for _ in range(num_players):
            player_name = names.pop(random.randint(0,len(names)-1))
            new_player = player(initial_chips=initial_chips, name=player_name)
            self.players.append(new_player)
    
    
    #getters
    def get_players(self):
        for player in self.players:
            print(player.name)
    
    def get_chip_counts(self):
        for player in self.players:
            print('Player: {}  Chip Count: {}'.format(player.name,player.chips))
    
    
    def reset(self):
        self.pot = 0
        self.deck = create_deck()
        self.flop = []
        for player in self.players:
            player.reset()
        
    def rotate_players(self):
        self.players = self.players[-1:] + self.players[:-1]
    
    def update_pot(self,player,bet):
        self.pot += bet
        player.chips -= bet
        player.current_bet += bet
        player.chips_in_pot += bet
    
    def players_in_hand(self):
        players_in = []
        for player in self.players:
            if player.in_hand == True:
                players_in.append(player)
        return players_in
    
    def deliver_winnings(self,winPlayer,numWinners):
        grab = winPlayer.chips_in_pot / numWinners
        winnings = winPlayer.chips_in_pot
        for player in self.players:
            if player != winPlayer:
                if player.chips_in_pot <= grab:
                    winnings += player.chips_in_pot
                    player.chips_in_pot = 0
                else:
                    winnings += grab
                    player.chips_in_pot -= grab

        if self.printInfo:
            print('{} gets {}'.format(winPlayer.name,winnings-winPlayer.chips_in_pot))
        winPlayer.chips += winnings
        winPlayer.chips_in_pot = 0
        
        unresolved = []
        for player in self.players:
            if player.chips_in_pot > 0 and player.in_hand:
                unresolved.append((get_top_hand(self.flop,player.hand),player))
        
        if unresolved:
            next_winners = get_winner(unresolved)
            num_winners_left = len(next_winners)
            for next_winner in next_winners:
                self.deliver_winnings(next_winner, num_winners_left)
        else:
            for player in self.players:
                player.chips += player.chips_in_pot
                player.chips_in_pot = 0
                    

    
    
    #go around table
    #if everyone checks, continue on
    #if someone raises, everyone else must call / raise
    def betting(self,min_bet=0,top_bettor=None):         
        new_bets = False
        for player in self.players:
            if player != top_bettor and player.in_hand:
                if player.name != 'me':
                    if player.chips == 0:
                        continue
                    else:
                        player_min = min_bet-player.current_bet
                        decision = player.make_decision(other_players=self.players_in_hand(), min_bet=player_min, input_flop=self.flop, printInfo=self.printInfo)
                        if decision == player.chips:
                            self.update_pot(player,decision)
                            if self.printInfo:
                                print(player.name + ' is all in!')
                        elif decision >= player_min:
                            self.update_pot(player,decision)
                            #raise
                            if decision > player_min:
                                top_bettor = player
                                new_bets = True
                                min_bet += decision-player_min  
                        else:                      
                            player.in_hand = False
                            if self.printInfo:
                                print('{} folds.'.format(player.name))
        
        if new_bets:
            self.betting(min_bet=min_bet,top_bettor=top_bettor)
               
        for player in self.players:
            player.current_bet = 0
        
            
    
    def deal(self):
        if self.printInfo:
            print('Dealing round')
        big = 10
        small = 5
        add_bet = 0

        for player in self.players:
            player.hand = [pick_random(self.deck),pick_random(self.deck)]
            player.in_hand = True
            
        self.update_pot(self.players[0],big)
        self.update_pot(self.players[1],small)
        
        self.betting(min_bet=10,top_bettor=self.players[0])
                
        players_in = self.players_in_hand()
        if len(players_in) == 1:
            winPlayer = players_in[0]
            self.deliver_winnings(winPlayer,1)
        else:
            self.deal_flop()
        
        elimBool = False
        for player in self.players:
            if player.chips == 0:
                print('{} has been eliminated.'.format(player.name))
                elimBool = True
                self.players.remove(player)
        if elimBool:
            print('Chip Counts:')
            self.get_chip_counts()
            print('\n')
                              
        if len(self.players)==1:
            print('Game Over! {} Wins!'.format(self.players[0].name))
            return 

        self.rotate_players()
        self.reset()
        
    

    def deal_flop(self):
        if self.printInfo:
            print('\nFirst Flop')
        self.flop = [pick_random(self.deck),pick_random(self.deck),pick_random(self.deck)]
        self.betting()

        players_in = self.players_in_hand()
        if len(players_in) == 1:
            winPlayer = players_in[0]
            self.deliver_winnings(winPlayer,1)
        else:
            self.flop_two()
        
        
    def flop_two(self):
        if self.printInfo:
            print('\nSecond Flop')
        self.flop.append(pick_random(self.deck))
        self.betting()
            
        players_in = self.players_in_hand()
        if len(players_in) == 1:
            winPlayer = players_in[0]
            self.deliver_winnings(winPlayer,1)
        else:
            self.river()
    
    
    def river(self):
        if self.printInfo:
            print('\nRiver Card')
        self.flop.append(pick_random(self.deck))
        self.betting()
            
        players_in = self.players_in_hand()
        if len(players_in) == 1:
            winPlayer = players_in[0]
            self.deliver_winnings(winPlayer,1)
        else:
            self.showdown()
    
    
    def showdown(self):
        topHands = []
        in_hand = self.players_in_hand()
        for player in in_hand:
            topHands.append((get_top_hand(self.flop,player.hand),player))

        winners = get_winner(topHands)
        
        if self.printInfo:
            print('Flop:  ' + str(self.flop))
        if self.printInfo:
            for player in in_hand:
                print('Player: {}   Hand: {}'.format(player.name,player.hand))
        
        for winner in winners:
            self.deliver_winnings(winner,len(winners))
        if self.printInfo:
            print('')
        
game = poker_game(num_players=4,initial_chips=100)
while len(game.players) > 1:
    game.deal()
            
                
                
                
        
        
                

        





