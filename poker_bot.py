
import pandas as pd
import os
import poker_simulators
from sklearn import svm
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler  




def get_players_in_hand(ind,p_data):
    in_hand = {}
    for name in p_data.keys():
        player = p_data[name]
        if ind in player.index:
            in_hand[name] = player.loc[ind]
    return in_hand


def betting_round(player_name, players):
    my_player_actions = {0:[],1:[],2:[],3:[]}
    #get order of players for betting rounds
    player_order=[None]*len(players.keys())
    for name in players.keys():
        ante_loc=players[name]['ante_loc']-1
        if not player_order[ante_loc]:
            player_order[ante_loc]=name
        else:
            print('ERROR')
    small_b=5
    big_b=10
    pot_size=small_b+big_b
    min_bet=10
    players_left = list(players.keys())
    curr_bets={}
    for name in players.keys():
        curr_bets[name]=0
    
    for roundNum in range(4):
        colName='r'+str(roundNum+1)
        if roundNum in [0,1]:
            limit=10
        else:
            limit=20

        more_action=True
        while more_action:
            more_action=False
            for name in player_order:
                p_row=players[name]
                round_decis=p_row[colName]
                if round_decis and round_decis != '-':
                    num_opps = len(players_left)-1
                    decis=round_decis[0]
                    p_row[colName]=round_decis[1:]
                    more_action=True

                    if decis=='B':
                        if p_row['ante_loc']==1:
                            curr_bets[name]+=small_b
                        elif p_row['ante_loc']==2:
                            curr_bets[name]+=big_b
                    else:
                        decis=decis.lower()
                        if decis=='q':
                            if name in players_left:
                                players_left.remove(name)
                            continue
                        
                        #how much for player to call
                        player_min=min_bet-curr_bets[name]

                        #record decision
                        #record_decision_made(player=name, decis=decis, bet_round=round_num, hand_str, chips_in_pot=curr_bets[name], player_min=player_min, num_opps=num_opps)
                        if name==player_name:
                            my_player_actions[roundNum].append({'player':name,'decis':decis,'to_call':player_min,'num_opps':num_opps,'chips_in_pot':curr_bets[name],'pot_size':pot_size})
                            #print('Player: {}  Round: {}  Decis={}  To Call={}  Num_Opps={} '.format(name, roundNum, decis,player_min,num_opps))

                            
                        #update pot
                        if decis=='b' or decis=='r':
                            min_bet+=limit
                            curr_bets[name]+=player_min+limit
                            pot_size+=player_min+limit
                        elif decis=='c':
                            curr_bets[name]+=player_min
                            pot_size+=player_min
                        elif decis == 'a':
                            min_bet+=p_row['chips']
                            pot_size+=p_row['chips']
                        elif decis == 'f':
                            if name in players_left:
                                players_left.remove(name)  
                        elif decis == 'k':
                            continue
                        
                        else:
                            print('weird decis: ' + decis)
    return my_player_actions


def get_player_profile(player_name, table_data, all_player_data):
    all_decisions=pd.DataFrame()
    all_player_hands = list(all_player_data[player_name].index)
    hands_played=0
    for played in all_player_hands:
        table_view=table_data.loc[played]
        players=get_players_in_hand(played,all_player_data)
        if players[player_name]['hand1'] and players[player_name]['hand2']:
            hands_played+=1
            hand=[players[player_name]['hand1'],players[player_name]['hand2']]
            flop=[]
            my_player_actions = betting_round(player_name, players)
            for roundNum in range(4):
                if roundNum==0:
                    None
                elif roundNum==1:
                    flop.extend([table_view['card1'],table_view['card2'],table_view['card3']])
                else:
                    flop.append(table_view['card'+str(roundNum+2)])
                    
                player_str=poker_simulators.hand_strength(hand,flop)
                decis_count=0
                for action in my_player_actions[roundNum]:
                    decis_count+=1
                    num_chips=players[player_name]['chips']-action['chips_in_pot']
                    ser = pd.Series([action['decis'], player_str, roundNum, action['to_call'], action['num_opps'], num_chips, action['chips_in_pot'], action['pot_size']])
                    ser.name='h'+str(hands_played)+'r'+str(roundNum)+'d'+str(decis_count)
                    all_decisions = all_decisions.append(ser)
                    
    all_decisions.columns=['decision','hand_str','bet_round','to_call','num_opps','chips','chips_in_pot','pot_size']
    return all_decisions



#table_data = pd.read_json('holdem_hand_data.json')
#all_player_data = {}
#for player in os.listdir('data'):
#    all_player_data[player] = pd.read_json('data/'+player)


#player_profile=get_player_profile('pdb.MegaHertz',table_data,all_player_data)
#player_profile.to_json('megaHertz_profile.json')

def get_decision(path_to_prof,hand_str,bet_round,to_call,num_opps,chips,in_pot,pot_size):
    player_profile=pd.read_json(path_to_prof)

    labels=player_profile['decision']
    training=player_profile.loc[:, player_profile.columns != 'decision'].as_matrix()

    scaler = StandardScaler()
    scaler.fit(training)
    training = scaler.transform(training)

    neural_net = MLPClassifier(solver='lbfgs', alpha=1e-5, hidden_layer_sizes=(5, 2), random_state=1)
    neural_net.fit(training,labels)

    variables=scaler.transform([[hand_str,bet_round,to_call,num_opps,chips,in_pot,pot_size]])
    decision = neural_net.predict(variables)[0]
    return decision


