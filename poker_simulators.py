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
        if straight[len(straight)-1]==14:
            print('ROYAL FLUSH!')
    elif bestMult[1] == 4:
        hand = [8] + get_tiebreak(1,[bestMult[0]],totals)
    elif bestMult[1] == 3 and secondBest[1] == 2:
        hand = [7,bestMult[0],secondBest[0]]
    elif flushBool:
        flushCards=flushCards[:5]
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



#1 = win, 0 = tie, -1 = loss
def did_i_win(my_hand,otherHands):
    result = 1
    for hand in otherHands:
        for ind in range(len(hand)):
            if hand[ind] > my_hand[ind]:
                return -1
            elif hand[ind] < my_hand[ind]:
                break
            else:
                if ind+1 == len(hand):
                    result = 0
    return result
                        
            
def get_odds(deck,flop,hand,printResults=False):
    
    my_hand = get_top_hand(flop,hand)
    
    wins = 0
    losses = 0
    ties = 0
    for card1 in deck:
        for card2 in deck:
            if card1 != card2:
                other_hand = get_top_hand(flop,[card1,card2])
                result = did_i_win(my_hand,[other_hand])
                if result == -1:
                    losses+=1
                elif result == 0:
                    ties+=1
                else:
                    wins+=1
    wins = int(wins/2)
    losses = int(losses/2)
    ties = int(ties/2)
    if printResults:
        print('My Hand = ' + str(hand))
        print('Flop = ' + str(flop))
        print('My Result: ' + str(my_hand))
        
        print('\nnum wins: ' + str(wins))
        print('num losses: ' + str(losses))
        print('num ties: ' + str(ties))
        
        print('winning percentage: ' + str(round(((wins) / (wins+losses)),2)))



def simulator_1(printResults=False):
    deck = create_deck()
    my_hand = [pick_random(deck),pick_random(deck)]
    
    flop = [pick_random(deck),pick_random(deck),pick_random(deck),pick_random(deck),pick_random(deck)]
    
    return get_odds(deck,flop,my_hand,printResults)




#simulator_1(printResults=True)


def simulator_2(num_tests=1000):
    perc = 0
    for _ in range(num_tests):
        perc += simulator_1()
    perc = perc / num_tests
    return perc



#hands is a list of (top_hand,player) tuples
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




def simulator_3(num_sims=1000, other_players=3):
    winRecords = {'me':0}
    
    deck = create_deck()
    my_hand = [pick_random(deck),pick_random(deck)]
    print('My hand: ' + str(my_hand))
    
    players = [('me',my_hand)]
    for i in range(other_players):
        name = 'player'+str(i)
        hand = [pick_random(deck),pick_random(deck)]
        players.append((name,hand))
        print('{} hand: {}'.format(name,str(hand)))
        winRecords[name] = 0
      
    printHands = 0
    for _ in range(num_sims):
        flop = [pick_random(deck),pick_random(deck),pick_random(deck),pick_random(deck),pick_random(deck)]
        
        topHands = []
        for player in players:
            p_hand = player[1]
            p_name = player[0]
            topHands.append((get_top_hand(flop,p_hand),p_name))
        
        winners = get_winner(topHands)        
        for winner in winners:
            winRecords[winner]+=1
        deck.extend(flop)                                  
                                                                               
    return winRecords



#num_sims=1000
#other_players=1
#winRecords = simulator_3(other_players=other_players, num_sims=1000)
#for player in winRecords:
#    print('{} win percentage = {}'.format(player,round(winRecords[player]*100/num_sims,2)))


#
#simulator 4 
#odds of winning with certain hand before flop
#and against certain number of opponents
#accurate within 1%
#
def simulator_4(printInfo=True, num_sims=1000, other_players=3, input_hand=None):
    wins = 0
    
    deck = create_deck()
    
    
    if input_hand:
        my_hand = input_hand
        deck.remove(my_hand[0])
        deck.remove(my_hand[1])
    else:
        my_hand = [pick_random(deck),pick_random(deck)]
    
    if printInfo:
        print('My hand: ' + str(my_hand))
        print('Number of Opponents: ' + str(other_players))
    
    
    for _ in range(num_sims):
        
        players = [('me',my_hand)]
        for i in range(other_players):
            name = 'player'+str(i)
            hand = ['07D','05D']
            #hand = [pick_random(deck),pick_random(deck)]
            players.append((name,hand))
        
        iterlen = 100 
        for _ in range(iterlen):
            flop = [pick_random(deck),pick_random(deck),pick_random(deck),pick_random(deck),pick_random(deck)]

            topHands = []
            for player in players:
                p_hand = player[1]
                p_name = player[0]
                topHands.append((get_top_hand(flop,p_hand),p_name))

            winners = get_winner(topHands)
            if 'me' in winners and len(winners)==1:
                wins+=1
                
            deck.extend(flop)    
        
        for pl in players:
            if pl[0] != 'me':
                deck.extend(pl[1])
    return round(100*wins/(num_sims*iterlen),2)



#my_win_pct = simulator_4(other_players=1)
#print('Win Percentage: ' + str(my_win_pct))


#
#simulator 5
#odds of winning at certain point of the hand
#and against certain number of opponents
#
#
def simulator_5(input_hand, input_flop=[], printInfo=True, num_sims=1000, other_players=3):
    wins = 0 
    deck = create_deck()
    my_hand = input_hand
    deck.remove(my_hand[0])
    deck.remove(my_hand[1])
        
    for card in input_flop:
        if card in input_hand:
            print('ERROR: flop contains card in hand')
            return        
    
    if input_flop:
        for card in input_flop:
            deck.remove(card)
    
    if printInfo:
        print('My hand: ' + str(my_hand))
        print('Number of Opponents: ' + str(other_players))
        if input_flop:
            print('Flop:  ' + str(input_flop))
        else:
            print('Flop:  Before flop')
            
            
    for _ in range(num_sims): 
        players = [('me',my_hand)]
        for i in range(other_players):
            name = 'player'+str(i)
            hand = [pick_random(deck),pick_random(deck)]
            players.append((name,hand))
        
        iterlen = 100
        for _ in range(iterlen):
            flop = input_flop.copy()
            newCards = []
            while len(flop) + len(newCards) < 5:
                newCards.append(pick_random(deck))
            flop.extend(newCards)

            topHands = []
            for player in players:
                topHands.append((get_top_hand(flop,player[1]),player[0]))

            winners = get_winner(topHands)
            if 'me' in winners:
                wins+=1/len(winners)
            
            deck.extend(newCards)

        for pl in players:
            if pl[0] != 'me':
                deck.extend(pl[1])
           
    return round(100*wins/(num_sims*iterlen),2)




#my_win_pct = simulator_5(input_hand=['07D','05D'],input_flop=['11C','04S','02C'], other_players=1)
#print('Win Percentage: ' + str(my_win_pct))


def simulator_6(input_hands = [], input_flop=[], printInfo=True, num_sims=1000):
    wins = 0 
    deck = create_deck()
    players = []
    wins = {}
    for i,hand in enumerate(input_hands):
        playerName =hand[0] + ' ' + hand[1]
        deck.remove(hand[0])
        deck.remove(hand[1]) 
        players.append((playerName,hand))
        wins[playerName] = 0
    
    if input_flop:
        for card in input_flop:
            deck.remove(card)            
            
    for _ in range(num_sims): 
        flop = input_flop.copy()
        newCards = []
        while len(flop) + len(newCards) < 5:
            newCards.append(pick_random(deck))
        flop.extend(newCards)

        topHands = []
        for player in players:
            topHands.append((get_top_hand(flop,player[1]),player[0]))

        winners = get_winner(topHands)
        
        #odds of winning out, no ties
        if len(winners) == 1:
            wins[winners[0]] +=1
            
        #for winner in winners:
        #    wins[winner] =wins[winner] + 1

        deck.extend(newCards)
    for name in wins.keys():
        wins[name] = round(100*wins[name] / num_sims, 2)
        
    return wins


#simulator_6(input_hands=[['14C','06C'],['14D','04D'],['09H','09C'],['14S','03S']], input_flop=['03H','02D','13S'], printInfo=True, num_sims=10000)


#returns the strength of input_hand
#strength = num of winning hands / hand possibilities
def hand_strength(input_hand,input_flop):
    deck = create_deck()
    my_hand = (get_top_hand(input_flop, input_hand),'me')
    deck.remove(input_hand[0])
    deck.remove(input_hand[1])
    
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



def num_losing_hands(input_hand,input_flop):
    deck = create_deck()
    my_hand = (get_top_hand(input_flop, input_hand),'me')
    deck.remove(input_hand[0])
    deck.remove(input_hand[1])
    
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
    

#get_hand_strength(input_hand=['06H','06D'],input_flop=['13C','13S','14S','05D','11S'])
#num_losing_hands(input_hand=['02H','03D'],input_flop=['02S','03S','11D'])
