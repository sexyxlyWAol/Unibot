# Feature List

> This document will guide you in using UniBot.

- UniBot is a functional Discord bot that mainly provides query services related to "Project SEKAI Colorful Stage" Japanese server, international server, Traditional Chinese server and Korean Server.
- By using this bot, you agree to the [Terms of Use](/en/licence/) and [Privacy Policy](/en/privacy/).

::: warning Note
The bot mainly serves users who use Simplified Chinese. Although most commands support English, the bot's response is in Chinese, and it is difficult to match the alias database in English
:::

::: danger Note
Due to modifications in the pjsk Japanese server API, only the top 100 rankings can be retrieved. The affected functions in the Japanese server are:
sk, pjsk progress, pjsk b30, rk, and difficulty rankings.
:::


## Query Project Sekai Song Information
> Popularity and difficulty deviation statistics are sourced from [profile.pjsekai.moe](https://profile.pjsekai.moe/) (some data may be outdated due to API changes).

### pjskinfo
- `pjskinfo+song name` to view detailed information about the current song.
- `pjskbpm+song name` to view the BPM.
- `findbpm+number` to query all songs with the corresponding BPM.

### Chart Preview
- `pjskchart [song title] [difficulty]` to preview the chart of the corresponding song and difficulty (Source: [ぷろせかもえ！](https://pjsekai.moe/) (~~under development~~ unlikely to continue due to API changes)).
  - Supported difficulty inputs: `easy`, `normal`, `hard`, `expert`, `master`, `ez`, `nm`, `hd`, `ex`, `ma`
  - If querying for `master`, the difficulty can be omitted.
- `pjskchart2 [song title] [difficulty]` to preview the chart of the corresponding song and difficulty (Source: [プロセカ譜面保管所](https://sdvx.in/prsk.html)).

### Various Rankings
- `levelrank [playlevel] [diffculty (master, expert, etc)]` to view the rankings of songs based on deviation for the current difficulty (e.g., `levelrank 26 expert`, difficulty can be omitted, default is master, lowercase is required).
- `fclevelrank [playlevel] [diffculty]` to view the rankings of songs based on FC deviation for the current difficulty (e.g., `fclevelrank 26 expert`, difficulty can be omitted, default is master, lowercase is required).
- `aplevelrank [playlevel] [diffculty]` to view the rankings of songs based on AP deviation for the current difficulty (e.g., `aplevelrank 26 expert`, difficulty can be omitted, default is master, lowercase is required).

### alias Settings

- `pjskset[alias]to[musictitle]`
- `pjskdel[alias]` to delete the corresponding alias.
- `charaset[alias]to[character name](existing alias can be used)` to set a common alias for the character across all groups, e.g., `charasetkndto宵崎奏`
- `charadel[alias]` to delete the common alias for the character across all groups.
- `grcharaset[new alias]to[exist alias]` to set a alias for the character that is only usable in the current group.
- `grcharadel[exist alias]` to delete the alias for the character that is only usable in the current group.
- `charainfo[alias]` to view the alias for the character in the group and across all groups.

::: warning Note
If you use the `pjskdel` command, please only delete inappropriate aliass. Deleting shortcut aliass used for guessing songs will cause inconvenience.

All song alias settings and character alias settings will be publicly displayed daily on the [Real-time Log](/dailylog/) page.
:::


## Query Player Information

> Add `en` before the command to query international server information, e.g., `enbind`, `ensk`, `enpjskcheck`, `enpjskprogress`, `enpjskprofile`.

> Add `tw` before the command to query Traditional Chinese server information, e.g., `twbind`, `twsk`, `twpjskcheck`, `twpjskprogress`, `twpjskprofile`.

> Add `kr` before the command to query Korean server information, e.g., `krbind`, `krsk`, `krpjskcheck`, `krpjskprogress`, `krpjskprofile`.

::: danger Note
Due to modifications in the pjsk Japanese server API, only the top 100 rankings can be retrieved. The affected functions in the Japanese server are:
sk, pjsk progress, pjsk b30, rk, and difficulty rankings.
:::

- `bind+id` to bind an ID.
### Event Query
- > Due to conflicts with other bot commands, the functionalities of `sk`, `pjskcheck`, `pjskpeek`, `stoptime` can be enabled or disabled by group administrators using the commands `关闭sk` and `开启sk`.
- `sk+id` to query rankings (this command does not bind an ID).
- `sk+rank` to query the score corresponding to the ranking.
- `pjskpredict` to view the prediction line, prediction information is sourced from [3-3.dev](https://3-3.dev/) (Japanese server only).
- `pjskspeed` to query the real-time speed line of the last hour (Japanese server only).
- `pjsk5v5` to view the real-time number of players in 5v5 mode.
- `pjskpeek+id` or `pjskpeek+rank` to query the weekly play count, speed, average points, etc. for the top 200 players (Japanese server, Taiwanese server).
- `stoptime+id` or `stoptime+rank` to query the parking situation for the top 200 players (Japanese server, Taiwanese server).
- `scoreline+id` or `scoreline+rank` to plot the score trend for the top 200 players over time (Japanese server, Taiwanese server).

### User Query
- `pjskcheck+id` to view the FC and AP count, as well as ranking information for the EX and Master difficulties of the corresponding ID.
- `pjskcheck` to view the FC and AP count, as well as ranking information for the EX and Master difficulties of the bound ID.
- `pjskprogress` to generate a progress image of master songs for the bound ID (FC/AP/Clear/All).
- `pjskprofile` to generate a profile image for the bound ID
- `pjsk b30` to generate a best 30 image for the bound ID.
### Privacy-related
- `pjskprivate` Your ID will not be displayed when checking scores or arresting yourself.
- `pjskpublic` to allow others to see.

### Card and Event Information Query
> The `findcard/event` functionalities were written by [Yozora](https://github.com/cYanosora). Many thanks.
- `findcard [character alias]`: Get all cards of the current character.
- `cardinfo [card ID]`: Get detailed information about the card with the specified ID.
- `event [event ID]`: View information about the specified event (can use `event` to view current event information directly).
- `findevent [keywords]`: Filter events by keywords and return a summary image. If no keywords are provided, a prompt image will be returned.
  - Single keyword method:
    - `findevent 5v5`: Return events with the 5v5 type.
    - `findevent mysterious`: Return events with the Purple Moon attribute.
    - `findevent knd`: Return events that include knd cards (including rewards).
    - `findevent miku`: Return events with any combination of Miku cards.
    - `findevent 25miku`: Return events with White Leek cards.
    - `findevent 25h`: Return events with any 25 members (excluding vs), not limited to the 25-box event.
  - Multiple keyword method:
    - `findevent pure 5v5`: Return events with the 5v5 type and Green Grass attribute.
    - `findevent knd cool`: Return events with the Blue Star attribute and knd cards.
    - `findevent marathon mysterious knd`: Return Marathon-type events with the Purple Moon attribute and knd cards (even if knd cards have different attributes, they will be displayed).
  - Examples:
    - `findevent 25h`: Only return events related to the 25-box event.
    - `findevent 25h 25miku`: Return events related to the 25-box event with White Leek cards.
    - `findevent knd ick`: Return events with mixed knd and ick cards.
- `findevent all`: Return a summary of all current events. This functionality cannot be used in channel bots due to large image size.

## Project Sekai Guessing
::: warning About Channel Version Guessing
Please answer within the specified time. The bot will not automatically end the guessing. If the answer exceeds the time limit, it will automatically end and prompt a timeout.
:::

- Guessing with cropped colored song illustrations: `pjskguess`
- Guessing with cropped black and white song illustrations: `pjskguess2`
- Guessing with very small cut (30*30): `pjsk非人类猜曲`
- Guessing the song with chart: `chartguess`
- Guessing the card's character with cropped card's image: `charaguess`


## Project Sekai Card Drawing (Gacha) Simulation
> Ten consecutive card draws will generate an image.
- `pjskgacha`: Simulate ten consecutive draws.
- `sekaiXXpull`: Simulate `XX` draws (only display rarity-4 cards). `XX` accepts values from `1` to `200` (from `1` to `400` in channels).
- `pjskgacha2`: Reverse the probability of two-star and rarity-4 cards.
- `pjskgacha+[card pool id]`: Simulate ten consecutive draws in the corresponding card pool.
- `sekai100pull+[card pool id]`: Simulate 100 draws (only display rarity-4 cards) in the corresponding card pool.
- `sekai200pull+[card pool id]`: Simulate 200 draws (only display rarity-4 cards) in the corresponding card pool.
- `pjskgacha2+[card pool id]`: Reverse the probability of rarity-2 and rarity-4 cards in the corresponding card pool.

::: tip About Card Pool ID
The card pool ID can be found by visiting <https://sekai.best/gacha> and checking the number at the end of the URL. For example, if the URL is <https://sekai.best/gacha/159>, the card pool ID is `159`.
:::


## About
- Developer: [綿菓子ウニ](https://space.bilibili.com/622551112)
### Framework Used
- Framework: [Mrs4s/go-cqhttp](https://github.com/Mrs4s/go-cqhttp)
- SDK: [nonebot/aiocqhttp](https://github.com/nonebot/aiocqhttp)
### Data Sources
- Prediction line: [33Kit](https://3-3.dev/)
- Song achievement rate, difficulty deviation, popularity, and other information: [Project Sekai Profile](https://profile.pjsekai.moe/) (limited due to API changes)
- Chart preview: [ぷろせかもえ！](https://pjsekai.moe/) (~~under development~~ unlikely to continue due to API changes), [プロセカ譜面保管所](https://sdvx.in/prsk.html)
- honor images for Traditional Chinese and EN servers: [Sekai Viewer](https://sekai.best/)