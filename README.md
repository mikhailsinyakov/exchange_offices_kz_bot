# Exchange offices in Kazakhstan
Telegram bot to search for exchange offices in Kazakhstan based on the details of a possible transaction. The bot uses the site https://kurs.kz/ to obtain information about exchange rates at exchange offices. Next, the bot selects exchange offices that give you the maximum amount of money in the currency of the purchase. As a result, the bot returns the amount of money you will receive, as well as a list of names of exchange offices and a link to Google Maps with office coordinates.

## Using the bot
- Go to http://t.me/exchange_offices_kz_bot and start a chat with the bot

*There are several supported commands:*
- **/find_best_offices** finds offices with best currency rates
- **/settings** shows current settings
- **/edit_city** changes your current city
- **/switch_language** switches the language to Russian or English
- **/help** gives you a help message

## Creating your own bot
- Install docker for your system: https://docs.docker.com/get-docker/
- Start docker service
- Create a new bot in BotFather using /newbot command
- Get API token
- Get geocode API key by registering at https://platform.here.com/sign-up
- Execute these commands:
```
mkdir exchange_offices
cd exchange_offices
echo TELEGRAM_API_TOKEN={YOUR_TELEGRAM_API_TOKEN} > .env
echo GEOCODE_API_KEY={YOUR_GEOCODE_API_KEY} >> .env
sudo docker run --env-file .env mikhailsinyakov/exchange_offices_kz
``` 