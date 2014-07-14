import sys
import time
import logging
import urllib2

from CexControl import Settings, TradeLoop, version


def init_logging():
    logger = logging.getLogger('CexControl')
    logger.setLevel(logging.INFO)
    # create file handler which logs even debug messages
    fh = logging.FileHandler('CexControl.log')
    fh.setLevel(logging.INFO)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(module)s - %(lineno)d - %(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)

init_logging()
log = logging.getLogger('CexControl')


def ParseArguments(settings):
    arguments = sys.argv

    if (len(arguments) > 1):
        log.info("CexControl started with arguments")

        # Remove the filename itself
        del arguments[0]

        for argument in arguments:

            if argument == "newconfig":
                log.info("newconfig:")
                log.info("  Delete settings and create new")
                settings.CreateSettings()

            if argument == "setthreshold":
                log.info("setthreshold:")
                log.info("  Creeate new threshold settings")
                settings.CreateTresholds()
                settings.LoadSettings()

            if argument == "version":
                log.info("Version: %s" % version)
                exit()

            if argument == "trial":
                log.info("trial:")
                log.info("  Trial mode, do not execute any real actions")
                settings.Trial = True


def main():

    log.info("======= CexControl version %s =======" % version)

    # First, try to get the configuration settings in the settings object
    settings = Settings()
    settings.LoadSettings()

    ParseArguments(settings)

    try:
        context = settings.GetContext()
        balance = context.balance()

        log.info("========================================")

        log.info("Account       : %s" % settings.username)
        log.info("GHS balance   : %s" % balance['GHS']['available'])

        log.info("========================================")

        log.info("BTC Threshold: %0.8f" % settings.BTC.Threshold)
        log.info("BTC Reserve  : %0.8f" % settings.BTC.Reserve)

        log.info("NMC Threshold: %0.8f" % settings.NMC.Threshold)
        log.info("NMC Reserve  : %0.8f" % settings.NMC.Reserve)

        log.info("IXC Threshold: %0.8f" % settings.IXC.Threshold)
        log.info("IXC Reserve  : %0.8f" % settings.IXC.Reserve)

        log.info("LTC Threshold: %0.8f" % settings.LTC.Threshold)
        log.info("LTC Reserve  : %0.8f" % settings.LTC.Reserve)

        log.info("Efficiency Threshold: %s" % settings.EfficiencyThreshold)
        log.info("Hold coins below efficiency threshold: %s" % settings.HoldCoins)

    except Exception as ex:
        log.exception(ex)

        try:
            ErrorMessage = balance['error']
        except:
            ErrorMessage = ("Unkown")

        log.info(ErrorMessage)

        log.info("")
        exit()

    while True:
        try:
            TradeLoop(context, settings)

        except urllib2.HTTPError, err:
            log.info("HTTPError :%s" % err)

        except Exception as ex:
            log.info("Unexpected error:")
            log.exception(ex)
            log.info("An error occurred, skipping cycle")

        log.info("")

        cycle = 150
        log.info("Cycle completed, idle for %s seconds" % cycle)

        while cycle > 0:
            time.sleep(10)
            cycle = cycle - 10

    pass


if __name__ == '__main__':
    main()
