# no-role-kick
A Discord bot for u/king35tana, requested at https://www.reddit.com/r/discordapp/comments/efdwtg/does_anyone_know_a_bot_that_removes_new_users/. 

Once a user joins, this bot will wait a specified amount of time. 
If the new member does not have any roles at the end of the specified period, they will be kicked. 

## Hosting
This bot is written in Go. I personally have tested Go 1.17.6 (Arch Linux x86_64).

Please see the [releases](https://github.com/qbxt/no-role-kick/releases) for the latest standalone executable.

## `nrk.env`
This file contains environment variables that are used by the bot.
It needs to be called `nrk.env` and be in the same directory as the executable.
Please see `nrk.env.template`.

## Building from source
```sh
git clone github.com/qbxt/no-role-kick
cd no-role-kick
go build
./no-role-kick
```

## License
Licensed under the "Unlicense" license.
Please see [LICENSE](LICENSE.md) file.