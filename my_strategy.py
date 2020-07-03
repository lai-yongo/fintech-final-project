# Class name must be Strategy
class Strategy():
    # option setting needed
    def __setitem__(self, key, value):
        self.options[key] = value

    # option setting needed
    def __getitem__(self, key):
        return self.options.get(key, '')

    def __init__(self):
        # strategy property needed
        self.subscribedBooks = {
            'Binance': {
                'pairs': ['BTC-USDT'],
            },
        }
        #period: 10 minutes
        self.period = 10 * 60
        self.options = {}

        # user defined class attribute
        self.last_type = 'sell'
        
        self.close_price_trace = np.array([])
        self.old_close_price_trace = np.array([])
        self.number_of_period = 10
        self.UP = 1
        self.DOWN = 2
        self.EQUAL =3
        self.close_price_upward = False
        
       

    
    def get_ma_trend(self):
        ma = talib.SMA(self.close_price_trace, self.number_of_period)[-1]
        if np.size(self.old_close_price_trace) is  0:
            return None
        old_ma = talib.SMA(self.old_close_price_trace, self.number_of_period)[-1]
        # if number of period =5,  first return [nan] , then [nan, nan]...until element has 5 item, like [ nan , nan , nan , nan 9687.678]
        # talib.SMA(self.close_price_trace, 5)[-1]  ==  9687.678 == (9710.52 + 9676.67 + 9672.88 + 9693.29 + 9685.03)/5
        #Log( ' SMA: ' + str(s_ma) )
        if np.isnan(ma) or np.isnan(old_ma):
            return None
        if ma > old_ma:
            return self.UP
        if ma < old_ma:
            return self.DOWN
        if ma == old_ma:
            return self.EQUAL
        else:
            return None
    
    
    def  if_cross_happend(self):

        close_price = self.close_price_trace[-1]
        if np.size(self.old_close_price_trace) is  0:
            return False
        old_close_price = self.old_close_price_trace[-1]
        ma = talib.SMA(self.close_price_trace, self.number_of_period)[-1]
        if np.isnan(ma):
            return False
        if  close_price  > ma and ma > old_close_price:
            return True
        if old_close_price > ma and ma > close_price:
            return True
        else:
            return False
    
    # called every self.period
    def trade(self, information):
        # for single pair strategy, user can choose which exchange/pair to use when launch, get current exchange/pair from information
        #information = {'asset':  {'Binance': {'BTC': 0.0, 'USDT': 100000.0}}, 'candles': {'Binance': {'BTC-USDT': [{'open': ..., 'high': ..., 'low': ..., 'close': ..., 'volume': ..., 'time...}]}}...}
        
        #exchange = 'Binance'
        exchange = list(information['candles'])[0]
        #pair = 'BTC-USDT'
        pair = list(information['candles'][exchange])[0]

        open_price = information['candles'][exchange][pair][0]['open']
        high_price = information['candles'][exchange][pair][0]['high']
        low_price = information['candles'][exchange][pair][0]['low']
        close_price = information['candles'][exchange][pair][0]['close']
        volume = information['candles'][exchange][pair][0]['volume']

       
        #info key {'asset', 'candles','orders','orderBooks'}
        '''
        for key in information:
            Log(str(key))
        '''
        '''
        Log(str(information['assset']))
        Log(str(information['candles']))
        Log(str(information['orders']))
        Log(str(information['orderBooks']))
        '''

        # add latest price into trace
        self.close_price_trace = np.append(self.close_price_trace, [float(close_price)])
        self.old_close_price_trace = self.close_price_trace[-(self.number_of_period+1):-1]
        self.close_price_trace = self.close_price_trace[-self.number_of_period:]
        # e.g. if number of period =5, self.close_price_trace == [9710.52 9676.67 9672.88 9693.29 9685.03]
        #Log('old_close_price_trace' + str(self.old_close_price_trace))
        #Log('close_price_trace' + str(self.close_price_trace))

        close_price = self.close_price_trace[-1]
        ma = talib.SMA(self.close_price_trace, self.number_of_period)[-1]
        if np.size(self.old_close_price_trace) is not 0:
            old_close_price = self.old_close_price_trace[-1]
        #Log('close_price'+str(close_price))
        #Log('ma'+str(ma))
        #if np.size(self.old_close_price_trace) is not 0:
        #    Log('old_close_price'+str(old_close_price))
        
        if np.isnan(ma):
            self.close_price_upward =False
        elif close_price > ma:
            self.close_price_upward = True
        else:
            self.close_price_upward =False
        
        #if self.close_price_upward is True:
        #    Log('close_price_upward')

        ma_trend = self.get_ma_trend()
        
        
        cross = self.if_cross_happend()
        #if cross is True:
        #    Log('cross happened')


        if ma_trend is None:
            return[]
        #if ma_trend is not None:
            #Log(str(ma_trend))
        if ma_trend == self.UP  and cross is True and  self.close_price_upward is True :
            
            self.last_type = 'buy'
            return [
                {
                    'exchange': exchange,
                    'amount': 1,
                    'price': -1,
                    'type': 'MARKET',
                    'pair': pair,
                },
            ]
        elif  ma_trend == self.DOWN  and cross is True and  self.close_price_upward is False :
            
            self.last_type = 'sell'
            return [
                {
                    'exchange': exchange,
                    'amount': -1,
                    'price': -1,
                    'type': 'MARKET',
                    'pair': pair,
                },
            ]
        
        return []
