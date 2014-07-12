import sys
import time
import urllib2

from CexControl import Settings, TradeLoop, version
from CexControl.Log import Logger
log = Logger()


def ParseArguments(settings):
    arguments = sys.argv

    if (len(arguments) > 1):
        log.Output("CexControl started with arguments")
        log.Output("")

        # Remove the filename itself
        del arguments[0]

        for argument in arguments:

            if argument == "newconfig":
                log.Output("newconfig:")
                log.Output("  Delete settings and create new")
                settings.CreateSettings()

            if argument == "setthreshold":
                log.Output("setthreshold:")
                log.Output("  Creeate new threshold settings")
                settings.CreateTresholds()
                settings.LoadSettings()

            if argument == "version":
                log.Output("Version: %s" % version)
                exit()

            if argument == "trial":
                log.Output("trial:")
                log.Output("  Trial mode, do not execute any real actions")
                settings.Trial = True


def main():

    log.Output("======= CexControl version %s =======" % version)

    # First, try to get the configuration settings in the settings object
    global settings
    settings = Settings()
    settings.LoadSettings()

    ParseArguments(settings)

    try:
        context = settings.GetContext()
        balance = context.balance()

        log.Output("========================================")

        log.Output("Account       : %s" % settings.username)
        log.Output("GHS balance   : %s" % balance['GHS']['available'])

        log.Output("========================================")

        log.Output("BTC Threshold: %0.8f" % settings.BTC.Threshold)
        log.Output("BTC Reserve  : %0.8f" % settings.BTC.Reserve)

        log.Output("NMC Threshold: %0.8f" % settings.NMC.Threshold)
        log.Output("NMC Reserve  : %0.8f" % settings.NMC.Reserve)

        log.Output("IXC Threshold: %0.8f" % settings.IXC.Threshold)
        log.Output("IXC Reserve  : %0.8f" % settings.IXC.Reserve)

        log.Output("LTC Threshold: %0.8f" % settings.LTC.Threshold)
        log.Output("LTC Reserve  : %0.8f" % settings.LTC.Reserve)

        log.Output("Efficiency Threshold: %s" % settings.EfficiencyThreshold)
        log.Output("Hold coins below efficiency threshold: %s" % settings.HoldCoins)

    except:
        log.Output("== !! ============================ !! ==")
        log.Output("Error:")

        try:
            ErrorMessage = balance['error']
        except:
            ErrorMessage = ("Unkown")

        log.Output(ErrorMessage)

        log.Output("")

        log.Output("Could not connect Cex.IO, exiting")
        log.Output("== !! ============================ !! ==")
        exit()

    while True:
        try:
            TradeLoop(context, settings)

        except urllib2.HTTPError, err:
            log.Output("HTTPError :%s" % err)

        except:
            log.Output("Unexpected error:")
            log.Output(sys.exc_info()[0])
            log.Output("An error occurred, skipping cycle")

        log.Output("")

        cycle = 150
        log.Output("Cycle completed, idle for %s seconds" % cycle)

        while cycle > 0:
            time.sleep(10)
            cycle = cycle - 10

    pass


if __name__ == '__main__':
    main()
