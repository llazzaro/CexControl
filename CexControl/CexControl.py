# ------------------------------------------------------------------------------
# Name:       CexControl
# Purpose:    Automatically add mined coins on Cex.IO to GHS pool
#
# Author:     Eloque
#
# Created:    19-11-2013
# Copyright:  (c) Eloque 2013
# Licence:    Free to use, copy and distribute as long as I'm credited
#             Provided as is, use at your own risk and for your own benefit
# Donate BTC: 1Lehv8uMSMyYyY7ZFTN1NiRj8X24E56rvV
# -------------------------------------------------------------------------------

from __future__ import print_function

import re
import sys
import time
import json
import logging

import cexapi

version = "0.9.4"

log = logging.getLogger('CexControl')


class CexControl(object):

    def __init__(self):
        pass
        # Initialize class
        # Trading = "GUI"


class Coin(object):

    def __init__(self, Name, Threshold, Reserve):

        self.Name = Name
        self.Threshold = Threshold
        self.Reserve = Reserve


class Settings(object):

    def __init__(self):

        self.BTC = Coin("BTC", 0.00001, 0.00)
        self.NMC = Coin("NMC", 0.00010, 0.00)
        self.IXC = Coin("IXC", 0.10000, 0.00)
        self.LTC = Coin("LTC", 0.10000, 0.00)

        self.EfficiencyThreshold = 1.0

        self.username = ""
        self.api_key = ""
        self.api_secret = ""

        self.HoldCoins = False
        self.Trial = False

    def LoadSettings(self):

        log.info("Attempting to load Settings")

        try:

            fp = open("CexControlSettings.conf")
            LoadedFromFile = json.load(fp)

            self.username = str(LoadedFromFile['username'])
            self.api_key = str(LoadedFromFile['key'])
            self.api_secret = str(LoadedFromFile['secret'])

            try:
                self.NMC.Threshold = float(LoadedFromFile['NMCThreshold'])
            except:
                log.info("NMC Threshold Setting not present, using default")

            try:
                self.NMC.Reserve = float(LoadedFromFile['NMCReserve'])
            except:
                log.info("NMC Reserve Setting not present, using default")

            try:
                self.BTC.Threshold = float(LoadedFromFile['BTCThreshold'])
            except:
                log.info("BTC Threshold Setting not present, using default")

            try:
                self.BTC.Reserve = float(LoadedFromFile['BTCReserve'])
            except:
                log.info("BTC Reserve Setting not present, using default")

            try:
                self.EfficiencyThreshold = float(LoadedFromFile['EfficiencyThreshold'])
            except:
                log.info("Efficiency Threshold Setting not present, using default")

            try:
                self.HoldCoins = bool(LoadedFromFile['HoldCoins'])
            except:
                log.info("Hold Coins Setting not present, using default")

            try:
                self.IXC.Threshold = float(LoadedFromFile['IXCThreshold'])
            except:
                log.info("IXC Threshold Setting not present, using default")

            try:
                self.IXC.Reserve = float(LoadedFromFile['IXCReserve'])
            except:
                log.info("IXC Reserve Setting not present, using default")

            if (LoadedFromFile):
                log.info("File found, loaded")

            try:
                self.LTC.Threshold = float(LoadedFromFile['LTCThreshold'])
            except:
                log.info("LTC Threshold Setting not present, using default")

            try:
                self.LTC.Reserve = float(LoadedFromFile['LTCReserve'])
            except:
                log.info("LTC Reserve Setting not present, using default")

            if (LoadedFromFile):
                log.info("File found, loaded")

        except IOError:
            log.info("Could not open file, attempting to create new one")
            self.CreateSettings()
            self.LoadSettings()

        # Dunno, if I should...
        self.WriteSettings()

    def CreateSettings(self):

        log.info("")
        log.info("Please enter your credentials")
        log.info("")
        self.username = raw_input("Username: ")
        self.api_key = raw_input("API Key: ")
        self.api_secret = raw_input("API Secret: ")

        self.CreateTresholds()

        self.WriteSettings()

    def WriteSettings(self):

        ToFile = {"username": str(self.username),
                   "key": str(self.api_key),
                   "secret": str(self.api_secret),
                   "BTCThreshold": str(self.BTC.Threshold),
                   "BTCReserve": str(self.BTC.Reserve),
                   "NMCThreshold": str(self.NMC.Threshold),
                   "NMCReserve": str(self.NMC.Reserve),
                   "IXCThreshold": str(self.IXC.Threshold),
                   "IXCReserve": str(self.IXC.Reserve),
                   "LTCThreshold": str(self.LTC.Threshold),
                   "LTCReserve": str(self.LTC.Reserve),
                   "EfficiencyThreshold": str(self.EfficiencyThreshold),
                   "HoldCoins": bool(self.HoldCoins)}

        try:
            log.info("")
            log.info("Configuration created, attempting save")
            json.dump(ToFile, open("CexControlSettings.conf", 'w'))
            log.info("Save successfull, attempting reload")
        except:
            log.info(sys.exc_info())
            log.info("Failed to write configuration file, giving up")
            exit()

    def CreateTresholds(self):

        log.info("")
        log.info("Please enter your thresholds")
        log.info("")

        self.BTC.Threshold = raw_input("Threshold to trade BTC: ")
        self.BTC.Reserve = raw_input("Reserve for BTC: ")

        self.NMC.Threshold = raw_input("Threshold to trade NMC: ")
        self.NMC.Reserve = raw_input("Reserve for NMC: ")

        self.IXC.Threshold = raw_input("Threshold to trade IXC: ")
        self.IXC.Reserve = raw_input("Reserve for IXC: ")

        self.LTC.Threshold = raw_input("Threshold to trade LTC: ")
        self.LTC.Reserve = raw_input("Reserve for LTC: ")

        self.EfficiencyThreshold = raw_input("Efficiency at which to arbitrate: ")
        self.HoldCoins = raw_input("Hold Coins at low efficiency (Yes/No): ")

        if (self.HoldCoins == "Yes"):
            self.HoldCoins = True
        else:
            self.HoldCoins = False

        self.WriteSettings()

    # Simply return the context, based on user name, key and secret
    def GetContext(self):

        return cexapi.API(self.username, self.api_key, self.api_secret)


# Externalised tradeloop
def TradeLoop(context, settings):
    now = time.asctime(time.localtime(time.time()))

    log.info("")
    log.info("Start cycle at %s" % now)

    CancelOrder(context)

    # balance = context.balance()
    GHSBalance = GetBalance(context, 'GHS')
    log.info("GHS balance: %s" % GHSBalance)
    log.info("")

    TargetCoin = GetTargetCoin(context)

    log.info("Target Coin set to: %s" % TargetCoin[0])
    log.info("")

    log.info("Efficiency threshold: %s" % settings.EfficiencyThreshold)
    log.info("Efficiency possible: %0.2f" % TargetCoin[1])

    if (TargetCoin[1] >= settings.EfficiencyThreshold):
        arbitrate = True
        log.info("Arbitration desired, trade coins for target coin")
    else:
        arbitrate = False
        if (settings.HoldCoins is True):
            log.info("Arbitration not desired, hold non target coins this cycle")
        else:
            log.info("Arbitration not desired, reinvest all coins this cycle")

    PrintBalance(context, "BTC")
    PrintBalance(context, "NMC")
    PrintBalance(context, "IXC")
    PrintBalance(context, "LTC")

    # Trade in IXC
    ReinvestCoinByClass(context, settings.IXC, "BTC", settings)

    # Trade in LTC
    ReinvestCoinByClass(context, settings.LTC, "BTC", settings)

    # Trade for BTC
    if (TargetCoin[0] == "BTC"):
        if (arbitrate):
            # We will assume that on arbitrate, we also respect the Reserve
            ReinvestCoinByClass(context, settings.NMC, TargetCoin[0], settings)

        else:
            if (settings.HoldCoins is False):
                ReinvestCoinByClass(context, settings.NMC, "GHS", settings)

        ReinvestCoinByClass(context, settings.BTC, "GHS", settings)

    # Trade for NMC
    if (TargetCoin[0] == "NMC"):
        if (arbitrate):
            # We will assume that on arbitrate, we also respect the Reserve
            ReinvestCoinByClass(context, settings.BTC, TargetCoin[0], settings)
        else:
            if (settings.HoldCoins is False):
                ReinvestCoinByClass(context, settings.BTC, "GHS", settings)

        ReinvestCoinByClass(context, settings.NMC, "GHS", settings)


# Convert a unicode based float to a real float for us in calculations
def ConvertUnicodeFloatToFloat(UnicodeFloat):

    # I need to use a regular expression
    # get all the character from after the dot
    position = re.search('\.', UnicodeFloat)
    if (position):
        first = position.regs
        place = first[0]
        p = place[0]
        p = p + 1

        MostSignificant = float(UnicodeFloat[:p - 1])
        LeastSignificant = float(UnicodeFloat[p:])

        Factor = len(UnicodeFloat[p:])
        Divider = 10 ** Factor

        LeastSignificant = LeastSignificant / Divider

        NewFloat = MostSignificant + LeastSignificant
    else:
        NewFloat = float(UnicodeFloat)

    return NewFloat


def CancelOrder(context):
    # BTC Order cancel
    order = context.current_orders("GHS/BTC")
    for item in order:
        try:
            context.cancel_order(item['id'])
            log.info("GHS/BTC Order %s canceled" % item['id'])
        except:
            log.info("Cancel order failed")

    # NMC Order cancel
    order = context.current_orders("GHS/NMC")
    for item in order:
        try:
            context.cancel_order(item['id'])
            log.info("GHS/NMC Order %s canceled" % item['id'])
        except:
            log.info("Cancel order failed")

    # NMC Order cancel
    order = context.current_orders("NMC/BTC")
    for item in order:
        try:
            context.cancel_order(item['id'])
            log.info("BTC/NMC Order %s canceled" % item['id'])
        except:
            log.info("Cancel order failed")

    # IXC Order cancel
    order = context.current_orders("IXC/BTC")
    for item in order:
        try:
            context.cancel_order(item['id'])
            log.info("IXC/BTC Order %s canceled" % item['id'])
        except:
            log.info("Cancel order failed")


# Get the balance of certain type of Coin
def GetBalance(Context, CoinName):

    balance = ("NULL")

    # log.info("Attempting to retreive balance for %s" % CoinName)

    try:

        balance = Context.balance()

        Coin = balance[CoinName]
        Saldo = ConvertUnicodeFloatToFloat(Coin["available"])

    except:
        # log.info (balance)
        Saldo = 0

    return Saldo


# Return the Contex for connection
def GetContext(settings):

    username = str(settings['username'])
    api_key = str(settings['key'])
    api_secret = str(settings['secret'])

    try:
        context = cexapi.API(username, api_key, api_secret)

    except:
        log.info(context)

    return context


# log.info the balance of a Coin
def PrintBalance(Context, CoinName):

    Saldo = GetBalance(Context, CoinName)

    message = "%s " % CoinName
    message = message + "Balance: %.8f" % Saldo

    log.info(message)


# Holder Class, to reinvest Coin by class
def ReinvestCoinByClass(Context, Coin, TargetCoin, settings):

    CoinName = Coin.Name
    Threshold = Coin.Threshold
    TargetCoin = TargetCoin

    Saldo = GetBalance(Context, CoinName)
    InvestableSaldo = Saldo - Coin.Reserve

    if (InvestableSaldo > Threshold):
        TradeCoin(Context, CoinName, TargetCoin, InvestableSaldo, settings)


# Reinvest a coin
def ReinvestCoin(Context, CoinName, Threshold, TargetCoin):

    log.info("Old function used, please issue a bug report, mention ReinvestCoin used")

#    Saldo = GetBalance(Context, CoinName)
#    if ( Saldo > Threshold ):
#        TradeCoin( Context, CoinName, TargetCoin )


# Trade one coin for another
def TradeCoin(Context, CoinName, TargetCoin, Amount, settings):

    # Get the Price of the TargetCoin
    Price = GetPriceByCoin(Context, CoinName, TargetCoin)

    log.info("----------------------------------------")
    log.info(CoinName + " for " + TargetCoin)

    # Get the balance of the coin
    TotalBalance = GetBalance(Context, CoinName)

    # Calculate the reserve, if any, we already have the amount
    Saldo = Amount

    # The hack we are using right now is going to be to add 2 percent to the PRICE of the
    # targetcoin,
    FeePrice = Price * 1.02

    # Caculate what to buy
    AmountToBuy = Saldo / FeePrice
    AmountToBuy = round(AmountToBuy - 0.000005, 6)

    # Calculate the total amount
    Total = AmountToBuy * FeePrice

    # Adjusted to compensate for floating math conversion
    while (Total > Saldo):
        AmountToBuy = AmountToBuy - 0.0000005
        AmountToBuy = round(AmountToBuy - 0.000005, 6)

        log.info("To buy adjusted to : %.8f" % AmountToBuy)

        # Hack to adjust for 2% fee
        Total = AmountToBuy * FeePrice

    TickerName = GetTickerName(CoinName, TargetCoin)

    # Hack, to differentiate between buy and sell
    action = ''
    Gain = 0.0
    if TargetCoin == "BTC":
        action = 'sell'
        AmountToBuy = Saldo  # sell the complete balance!
        log.info("Amount to sell %.08f" % AmountToBuy)

        # I am selling my Coin, for FeePrice BTC per Coin
        # So, I get AmounToBuy / FeePrice BTC
        Gain = AmountToBuy * FeePrice

    else:
        action = 'buy'
        log.info("Amount to buy %.08f" % AmountToBuy)

        # I am buying Coin, for FeePrice per Coin
        # So, I get AmounToBuy
        Gain = AmountToBuy
    if settings.Trial is False:
        result = Context.place_order(action, AmountToBuy, Price, TickerName)
    else:
        log.info("No real trade, trial mode")

    log.info("Placed order at %s" % TickerName)

    if TargetCoin == "BTC":
        log.info("   Sell %.8f" % AmountToBuy)
    else:
        log.info("   Buy %.8f" % AmountToBuy)

    log.info("   at %.8f" % Price)
    log.info("   Total %.8f" % Total)
    log.info("   Funds %.8f" % TotalBalance)

    string = "   Gain %.8f " % Gain
    string = string + TargetCoin
    log.info(string)

    try:
        if settings.Trial is False:
            OrderID = result['id']
            log.info("Order ID %s" % OrderID)

    except:
        log.info(result)
        log.info(AmountToBuy)
        log.info("%.7f" % Price)
        log.info(TickerName)

    log.info("----------------------------------------")


# Simply reformat a float to 8 numbers behind the comma
def FormatFloat(number):

    number = unicode("%.8f" % number)
    return number


# Get TargetCoin, reveal what coin we should use to buy GHS
def GetTargetCoin(Context):
    # Get the Price NMC/BTC

    GHS_NMCPrice = GetPrice(Context, "GHS/NMC")
    GHS_BTCPrice = GetPrice(Context, "GHS/BTC")
    NMC_BTCPrice = GetPrice(Context, "NMC/BTC")

    BTC_NMCPrice = 1 / NMC_BTCPrice

    GHS_NMCPrice = 1 / GHS_NMCPrice
    GHS_BTCPrice = 1 / GHS_BTCPrice

    log.info("1 NMC is %s GHS" % FormatFloat(GHS_NMCPrice))
    log.info("1 NMC is %s BTC" % FormatFloat(NMC_BTCPrice))
    log.info("1 BTC is %s GHS" % FormatFloat(GHS_BTCPrice))
    log.info("1 BTC is %s NMC" % FormatFloat(BTC_NMCPrice))

    NMCviaBTC = NMC_BTCPrice * GHS_BTCPrice
    BTCviaNMC = BTC_NMCPrice * GHS_NMCPrice

    BTCviaNMCPercentage = BTCviaNMC / GHS_BTCPrice * 100
    NMCviaBTCPercentage = NMCviaBTC / GHS_NMCPrice * 100

    log.info("1 BTC via NMC is %s GHS" % FormatFloat(BTCviaNMC))
    log.info("Efficiency : %2.2f" % BTCviaNMCPercentage)
    log.info("1 NMC via BTC is %s GHS" % FormatFloat(NMCviaBTC))
    log.info("Efficiency : %2.2f" % NMCviaBTCPercentage)

    if NMCviaBTCPercentage > BTCviaNMCPercentage:
        coin = "BTC"
        efficiency = NMCviaBTCPercentage - 100
    else:
        coin = "NMC"
        efficiency = BTCviaNMCPercentage - 100

    returnvalue = (coin, efficiency)

    log.info("Buy %s then use that to buy GHS" % coin)

    return returnvalue


# Get the price of a coin for a market value
def GetPriceByCoin(Context, CoinName, TargetCoin):

    Ticker = GetTickerName(CoinName, TargetCoin)

    return GetPrice(Context, Ticker)


# Fall back function to get TickerName
def GetTickerName(CoinName, TargetCoin):

    Ticker = ""

    if CoinName == "NMC":
        if TargetCoin == "GHS":
            Ticker = "GHS/NMC"
        if TargetCoin == "BTC":
            Ticker = "NMC/BTC"

    if CoinName == "BTC":
        if TargetCoin == "GHS":
            Ticker = "GHS/BTC"
        if TargetCoin == "NMC":
            Ticker = "NMC/BTC"

    if CoinName == "IXC":
        Ticker = "IXC/BTC"

    if CoinName == "LTC":
        Ticker = "LTC/BTC"

    return Ticker


# Get Price by ticker
def GetPrice(Context, Ticker):

    # Get price
    ticker = Context.ticker(Ticker)

    # Ask = ConvertUnicodeFloatToFloat(ticker["ask"])
    # Bid = ConvertUnicodeFloatToFloat(ticker["bid"])

    Ask = ticker["ask"]
    Bid = ticker["bid"]

    # Get average
    Price = (Ask + Bid) / 2

    # Change price to 7 decimals
    Price = round(Price, 7)

    return Price
