# Setting up Heroku

This is the instructions to run auto bot on Heroku.

## Prerequisite

* You should know how to use Git CLI.
* You should know how to use shell application (Terminal, Command Prompt etc).

## General Steps

1. Create an account on Heroku (one account for AutoBot and another for Captcha API).
2. Go to Dashboard - New - Create new app.
3. On the new app page, go to Deploy and follow the instructions to install the Heroku CLI onto your computer and then login via CLI.
4. Clone the repository (`git clone https://github.com/ngjunkang/MouseHunt.git`) or download the code directly.
5. Navigate to the main directory of the code using CLI and add another remote repository using `heroku git:remote -a <app-name>`, e.g. if your app name is mhbot, then the command is `heroku git:remote -a mhbot`.

## Setting up Captcha API (only if you do not have access to one)

1. As of 18 May 2022, new apps come with heroku-20 stack, but the current code base of the Captcha API only works with heroku-18 stack. To change to heroku-18, use `heroku stack:set heroku-18` in your shell application.

2. Go to Settings of app, under Config Vars, add two environment variable as follows,
    1. `TESSDATA_PREFIX` = `./.apt/usr/share/tesseract-ocr/4.00/tessdata`
    2. `TESS_PATH` = `./.apt/usr/bin/tesseract`

3. Then, on the same page, add this Buildpack under Buildpacks, `https://github.com/heroku/heroku-buildpack-apt`. Also, ensure that you have the `heroku/python` buildpack, else add the official python buildpack.

4. Using shell application, push the code to Heroku using the following command (heroku-captcha is one of the branches in this repository, and we are pushing to master branch of the Heroku repository),

```
git checkout heroku-captcha
git push heroku heroku-captcha:master
```

The API will then be accessible @ `https://<app_name>.herokuapp.com`, if your app name is mhbot, then the URL is `https://mhbot.herokuapp.com`.

## Setting up AutoBot

Note: The free version of Heroku provides 550 hours of running time per month, which allows us to run around 75% of the time, assuming 720 hours per 30-day month. Unlike Captcha API (sleeps and wait for requests), AutoBot will be running 24/7, hence AutoBot will have a downtime of 25% every month (acceptable to me). However, you can enter your credit card details at zero cost for an additional 450 hours every month.


1. Go to Settings of app, under Config Vars, add two environment variable as follows,
    1. `MH_USERNAME` = your username
    2. `MH_PASSWORD` = your password
    3. `MH_TRAP_CHECK` = your trap check timing (0, 15, 30, 45)
    4. `CAPTCHA_URL` = your Captcha API URL or someone's URL

2. On the same page, under Buildpacks, ensure that you have the `heroku/python` buildpack, else add the official python buildpack.

3. Using shell application, push the code to Heroku using the following command (heroku-bot is one of the branches in this repository, and we are pushing to master branch of the Heroku repository),

```
git checkout heroku-bot
git push heroku heroku-bot:master
```

4. Using shell application, activate a worker,
```
heroku ps:scale worker=1
```

