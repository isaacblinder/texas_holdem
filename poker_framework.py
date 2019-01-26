
import random
import poker_simulators
from poker_simulators import *
import logging
import os
import configparser
import poker_bot

config = configparser.ConfigParser()
config.read('config.ini')

logLvl = config['LOGGER']['level']
logger = logging.getLogger('poker_framework')
logger.setLevel(logLvl)
numLogs = len(os.listdir('logs/'))
fs = logging.FileHandler('logs/log'+str(numLogs))
fs.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
fs.setLevel(logLvl)
logger.addHandler(fs)
initial_chips=int(config['VARS']['initial_chips'])
num_players=int(config['VARS']['num_players'])

big_blind=int(config['BLINDS']['big_blind'])
small_blind=int(config['BLINDS']['small_blind'])

#PLAYER FRAMEWORK
class Player:
    def __init__(self,initial_chips,name):
        self.chips = initial_chips
        self.name = name
        self.hand = None
        self.in_hand = True
        self.chips_in_pot = 0
        self.current_bet = 0
        self.previous_bet = 0
        self.path_to_prof=None

        #player: [(cards in hand, hand strength, action, categorization of action)]
        self.memory=[]
    

    #new round
    def reset(self):
        self.hand = None
        self.in_hand = True
        self.current_bet = 0
        self.previous_bet = None
        self.chips_in_pot = 0
         
    
    #strength = num of winning hands / hand possibilities
    def get_hand_strength(self,input_flop=[]):
        return poker_simulators.hand_strength(self.hand, input_flop)
        

    def get_num_losing_hands(self,input_flop):
        return poker_simulators.num_losing_hands(self.hand, input_flop)

    
    def get_chip_rank(self,other_players):
        rank = 1
        for player in other_players:
            if player.chips > self.chips:
                rank+=1
        return rank

    def strength_meter():
        i=3

    #def categorize_players():
        #if more than 10 hands played

    #BETTING STRATEGIES
    def value_bet():
        i=3

    def bluff():
        i=3



    #decide whether to go all in
    def all_in_decision(self,invested,hand_strength):
        if invested >= 85:
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
    

    def make_decision(self,other_players,min_bet,num_raises,input_flop=[]):
        hand_strength = self.get_hand_strength(input_flop=input_flop)
        
        if len(input_flop) == 0:
            bet =  self.pre_flop_strategy(min_bet,hand_strength)
        else:
            if len(input_flop) == 3:
                bet = self.round_1_strategy(min_bet,other_players,hand_strength,num_raises)
            elif len(input_flop) == 4:
                bet = self.round_1_strategy(min_bet,other_players,hand_strength,num_raises)
            elif len(input_flop) == 5:
                bet = self.round_1_strategy(min_bet,other_players,hand_strength,num_raises)
        
        if bet > self.chips:
            bet = self.chips
        
        logger.debug('Player = {}   Hand Strength = {}   Mininimum Bet = {}'.format(self.name,hand_strength,min_bet))  
        return bet
    
    
    
    
    #generic pre-flop strategy
    def pre_flop_strategy(self,min_bet,hand_strength):
        if hand_strength > 85:
            return min_bet*2
        elif hand_strength > 60:
            return min_bet
        else:
            return 0
        
        
    def round_1_strategy(self,min_bet,other_players,hand_strength,num_raises):
        chip_rank = self.get_chip_rank(other_players)
        dominated_players = self.get_dominated_players(other_players)
        min_bet_ratio = min_bet/self.chips
        confidence_ratio = hand_strength * (1-min_bet_ratio)
        percent_chips_invested = round(100*(1-(self.chips / (self.chips_in_pot+self.chips))))
        #logger.debug(self.name + '\'s bet strategy: chip rank={}, dominated_plyrs={}, min_bet/num_chips={}, confidence_ratio={}, perc_invested={}'.format(chip_rank,dominated_players,min_bet_ratio,confidence_ratio,percent_chips_invested))


        final_bet = 0
        #must go all in
        if min_bet >= self.chips:
            if self.all_in_decision(percent_chips_invested,hand_strength) == True:
                final_bet = min_bet
            else:
                final_bet = 0

        elif min_bet > 0:
            if confidence_ratio >= 80 or hand_strength >= 90:
                final_bet = min_bet*3
            elif confidence_ratio >= 75 or hand_strength >= 80:
                final_bet = min_bet*2
            elif 100*min_bet_ratio <= 20 and hand_strength >= 70:
                final_bet = min_bet
            elif 100*min_bet_ratio <= 10 and hand_strength >= 60:
                final_bet = min_bet
            else:
                final_bet = 0

        else:
            if hand_strength >= 90:
                final_bet = min_bet*3
            elif hand_strength >= 80:
                final_bet = min_bet*2
            elif hand_strength >= 70:
                final_bet = min_bet + int(self.chips/10)
            elif hand_strength >= 60:
                final_bet = min_bet + int(self.chips/20)
            else:
                final_bet = 0

        if num_raises >= 3:
            if final_bet > min_bet:
                logger.debug('3 raises already made')
                final_bet=min_bet
        return final_bet
            

        
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
  

    
#GAME FRAMEWORK
class Game:
    def __init__(self):
        names = ['Frank','Dee','Mac','Charlie','Dennis','Franquito','Margaret','Rickety Cricket','Artemis']
        
        self.pot = 0
        self.deck = create_deck()
        self.flop = []
        
        self.players = []#[player(initial_chips=initial_chips, name='me')]
        for _ in range(num_players-1):
            player_name = names.pop(random.randint(0,len(names)-1))
            new_player = Player(initial_chips=initial_chips, name=player_name)
            self.players.append(new_player)

        #add bot
        new_player = Player(initial_chips=initial_chips, name='megaHertz')
        new_player.path_to_prof='megaHertz_profile.json'
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
        grab = int(round(winPlayer.chips_in_pot / numWinners))
        winnings = winPlayer.chips_in_pot
        for player in self.players:
            if player != winPlayer:
                if player.chips_in_pot <= grab:
                    winnings += player.chips_in_pot
                    player.chips_in_pot = 0
                else:
                    winnings += grab
                    player.chips_in_pot -= grab

        logger.debug('{} gets {}'.format(winPlayer.name,winnings-winPlayer.chips_in_pot))
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

    def deal(self):

        for player in self.players:
            player.hand = [pick_random(self.deck),pick_random(self.deck)]
            player.in_hand = True

        self.run_hand()
        self.check_elim()
        self.rotate_players()
        self.reset()


    def run_hand(self):
        if len(self.flop)==0:
            logger.debug('DEALING')
            self.update_pot(self.players[0],big_blind)
            self.update_pot(self.players[1],small_blind)
            self.betting(min_bet=big_blind,top_bettor=[])
        else:
            logger.debug('ON TABLE: ' + str(self.flop))
            self.betting(top_bettor=[])

        players_in = self.players_in_hand()
        if len(players_in) == 1:
            self.deliver_winnings(players_in[0],1)
        else:
            if len(self.flop) == 0:
                    self.flop = [pick_random(self.deck),pick_random(self.deck),pick_random(self.deck)]
                    self.run_hand()
            elif len(self.flop) < 5:
                self.flop.append(pick_random(self.deck))
                self.run_hand()
            else:
                self.showdown()

    def get_bet_round(self):
        if not self.flop:
            return 0
        elif len(self.flop)==3:
            return 1
        elif len(self.flop)==4:
            return 2
        elif len(self.flop)==5:
            return 3
        else:
            print('ERROR: Incorrect number of cards in flop')
    
    
    #go around table
    #if everyone checks, continue on
    #if someone raises, everyone else must call / raise
    def betting(self,min_bet=0,top_bettor=[],num_raises=0):
        bet_round=self.get_bet_round()
        if bet_round <= 1:
            max_raise=10
        else:
            max_raise=20

        new_bets = False
        for player in self.players:
            if player not in top_bettor and player.in_hand:
                if player.name != 'me':
                    if player.chips > 0:
                        player_min = min_bet-player.current_bet
                        if player.path_to_prof: #bot
                            hand_str=player.get_hand_strength(self.flop)
                            decision=poker_bot.get_decision(path_to_prof=player.path_to_prof,
                                                            hand_str=hand_str,
                                                            bet_round=bet_round,
                                                            to_call=player_min,
                                                            num_opps=len(self.players_in_hand()),
                                                            chips=player.chips,
                                                            in_pot=player.chips_in_pot,
                                                            pot_size=self.pot)
                            if decision=='k':
                                decision=0
                            elif decision=='c':
                                decision=player_min
                            elif decision=='r' or decision=='b':
                                decision=player_min+max_raise
                            logger.debug(player.name + '\'s decision info: hand_str={}, to_call={}, num_opps={}, chips={}, in_pot={}'.format(hand_str,player_min,len(self.players_in_hand()),player.chips,player.chips_in_pot))


                        else:
                            decision = player.make_decision(other_players=self.players_in_hand(), min_bet=player_min, num_raises=num_raises, input_flop=self.flop)
                        

                        if decision==player_min and decision < player.chips:
                            top_bettor.append(player)
                            self.update_pot(player,decision)
                            if player_min==0:
                                logger.debug(player.name + ' checks.')
                            else:
                                logger.debug(player.name + ' calls.')
                        
                        elif decision > player_min:
                            decision=player_min+max_raise
                            self.update_pot(player,decision)
                            num_raises+=1
                            top_bettor = [player]
                            new_bets = True
                            min_bet += decision-player_min

                            if player_min==0:
                                logger.debug(player.name + ' bets.')
                            else:
                                logger.debug(player.name + ' raises.')

                        elif decision >= player.chips:
                            decision=player.chips
                            self.update_pot(player,decision)
                            logger.debug(player.name + ' is all in!')
  
                        else: 
                            #fold      
                            player.in_hand = False
                            logger.debug('{} folds.'.format(player.name))
        
        if new_bets:
            self.betting(min_bet=min_bet,top_bettor=top_bettor,num_raises=num_raises)
               
        for player in self.players:
            player.current_bet = 0


    def showdown(self):
        logger.debug('SHOWDOWN')
        topHands = []
        for player in self.players_in_hand():
            topHand=get_top_hand(self.flop,player.hand)
            topHands.append((topHand,player))
            logger.debug('Player: {}   Hand: {}, Has: {}'.format(player.name,player.hand,topHand))
        
        winners = get_winner(topHands)
        for winner in winners:
            self.deliver_winnings(winner,len(winners))
                
        

    def check_elim(self):
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

        
         

game = Game()
iters=0
while len(game.players) > 1 and iters<1000:
    iters+=1
    game.deal()
            
                