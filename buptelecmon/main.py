# -*- coding:utf-8 -*-
import sys
import buptelecmon.logger
import buptelecmon.configurationmanager
import buptelecmon.electricitymonitor
import buptelecmon.animateprogress

# Initialize animate process bar
ap = buptelecmon.animateprogress.AnimateProgress()

# Remaining available time formater
def convert_rat(remaining_hrs):
    return '%dday(s) %.2d:%.2d:%.2d' % (
        remaining_hrs // 24, remaining_hrs % 24,
        remaining_hrs * 60 % 60, remaining_hrs * 3600 % 60
    )

# Output formater
def output(dormitory, data, params=None):
    print('%s %s - Remaining: %.2f kWh (Free: %.2f kWh).' % 
        (
            dormitory, 
            data['time'], 
            float(data['surplus'])+float(data['freeEnd']), float(data['freeEnd'])
        )
    )
    print('\t- Voltage/Current/Power/Power Factory: %.1f V, %.3f A, %.1f W, %.2f.' % 
        (
            float(data['vTotal']), 
            float(data['iTotal']), 
            1000*float(data['pTotal']), 
            float(data['cosTotal'])
        )
    )
    print('\t- Available time: %s.' % 
        (convert_rat((float(data['surplus'])+float(data['freeEnd']) / float(data['pTotal'])))
            if float(data['pTotal']) != 0 else 'Infinite')
    )

# Run once mode
def once_mode(username, password, dormitories):
    ap.start_rotated_progress('Collecting data...')
    em = buptelecmon.electricitymonitor.ElectricityMonitor()
    em.login(username, password)
    results = em.query(dormitories)
    ap.stop_progress()
    for dormitory in results:
        output(dormitory, results[dormitory])

# Run loop mode
def loop_mode(username, password, dormitories):
    print("Electricity Monitor will collect data every 60 seconds.")
    em = buptelecmon.electricitymonitor.ElectricityMonitor()
    em.login(username, password)
    em.loop(dormitories, output)

# Main function
def main(argv):
    # Create logger
    log = buptelecmon.logger.register(__name__)
    # Create config man
    cman = buptelecmon.configurationmanager.ConfigMan('elecmon', 'elecmon.json')
    try:
        # Set initial parameters
        param = {
            'username': '',
            'password': '',
            'dormitories': []
        }
        # Parse arguments
        if len(argv) > 0 and argv[0] == '--set-auth': # Set authorization
            param['username'] = input('Student ID: ')
            param['password'] = input('Password: ')
            cman.write_back(param)
        else:
            # Load configurations
            param = cman.read()
            # Run
            if len(argv) > 0 and argv[0] == '--loop': # Loop mode
                if len(argv) > 1:
                    param['dormitories'] = argv[1:]
                    cman.write_back(param)
                loop_mode(param['username'], param['password'], param['dormitories'])
            else: # Once mode
                if len(argv) > 0:
                    param['dormitories'] = argv[0:]
                    cman.write_back(param)
                once_mode(param['username'], param['password'], param['dormitories'])
    except KeyboardInterrupt:
        log.info('Aborted by user.')
    except Exception as e:
        log.error(str(e))
        log.debug('', exc_info=True)
        log.error("Please check the log for more information.")

# Run by command line
def loader():
    main(sys.argv[1:])

# Run by file name
def init(name):
    if name == '__main__':
        loader()

init(__name__)