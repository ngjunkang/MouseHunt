import os
import random
import re
import sched
import time
from datetime import datetime, timedelta
from bot_plus import BotPlus as Bot

MAX_DELAY = 100
TRAP_CHECK_PRIORITY = 1
HORN_PRIORITY = 2


def main():
    username = os.environ['MH_USERNAME']
    password = os.environ['MH_PASSWORD']
    trap_check = int(os.environ['MH_TRAP_CHECK'])
    keywords = os.environ.get('MH_KEYWORDS')

    captcha_host = os.environ.get('CAPTCHA_HOST', 'localhost')
    captcha_port = int(os.environ.get('CAPTCHA_PORT', '8080'))
    captcha_url = f'http://{captcha_host}:{captcha_port}'

    if keywords is None:
        bot = Bot(username, password, trap_check, captcha_url)
    else:
        pattern = r',\s*'
        keywords = [t for s in keywords.split('\n') for t in re.split(pattern, s)]
        bot = Bot(username, password, trap_check, captcha_url, keywords)

    while True:
        day = datetime.now().day
        s = sched.scheduler(time.time, time.sleep)
        s.enter(delay=0, priority=TRAP_CHECK_PRIORITY, action=trap_check_loop, argument=(bot, s, day))
        s.enter(delay=0, priority=HORN_PRIORITY, action=horn_loop, argument=(bot, s, day))
        s.run()


def horn_loop(bot: Bot, s: sched.scheduler, curr_day: int):
    bot.refresh_sess()

    secs_to_next_hunt = bot.get_user_data()['next_activeturn_seconds']
    if secs_to_next_hunt > 0:
        arbitrary_delay = 5
        total_delay = secs_to_next_hunt + arbitrary_delay
    else:
        bot.check_and_solve_captcha()
        bot.horn()
        total_delay = 15*60 + random.randint(1, MAX_DELAY)

    bot.update_journal_entries()

    if datetime.now().day != curr_day:
        return

    next_hunt_dt = datetime.now() + timedelta(seconds=total_delay)
    bot.logger.info(f'time of next hunt: {next_hunt_dt.strftime("%Y-%m-%d %T")}')

    s.enter(delay=total_delay, priority=HORN_PRIORITY, action=horn_loop, argument=(bot, s, curr_day))
    s.run()


def trap_check_loop(bot: Bot, s: sched.scheduler, curr_day: int):
    bot.refresh_sess()

    curr_min = datetime.now().minute
    if curr_min == bot.trap_check:
        bot.update_journal_entries()

    if datetime.now().day != curr_day:
        return

    if curr_min >= bot.trap_check:
        next_check_hour = datetime.now() + timedelta(hours=1)
    else:
        next_check_hour = datetime.now()

    arbitrary_buffer = 5
    next_check_dt = next_check_hour.replace(minute=bot.trap_check, second=arbitrary_buffer, microsecond=0)
    bot.logger.info(f'time of next trap check: {next_check_dt.strftime("%Y-%m-%d %T")}')

    next_day = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    secs_to_next_day = (next_day - datetime.now()).total_seconds()
    secs_to_next_check = (next_check_dt - datetime.now()).total_seconds()
    s.enter(delay=min(secs_to_next_check, secs_to_next_day), priority=TRAP_CHECK_PRIORITY, action=trap_check_loop, argument=(bot, s, curr_day))
    s.run()


if __name__ == '__main__':
    main()
