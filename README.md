# 🏅 Quotes Discord Bot
[![forthebadge](https://forthebadge.com/images/badges/made-with-python.svg)](https://forthebadge.com)
[![forthebadge](https://forthebadge.com/images/badges/built-with-love.svg)](https://forthebadge.com)
[![forthebadge](https://forthebadge.com/images/badges/makes-people-smile.svg)](https://forthebadge.com)


Quote and pin **the most memorable short messages** forever in a **unique and original quote design** by **reacting with a specific emoji** under someone's message!

❯ **[Invite the bot to your server](https://discord.com/oauth2/authorize?client_id=831875019071291433&permissions=388160&scope=bot)**

# 🖼️ Demo

<img src="https://raw.githubusercontent.com/vdElyn/quotes/%F0%9F%93%96-Adding-README.md/demo.png" alt="demo">

# Configuration

After the bot arrives, you have to **configure the emoji with which you want to quote messages** as well as **the channel in which the quoted images will be posted.**

### 🕹️ Here are the configuration commands, make sure you are in a channel to which the bot has access.

|  Command  | Description | Default
| ------------- | ------------- | --- |
| `.help` | Prints helps message | `.help` |
| `.set_prefix <prefix>` | Set another **prefix** for the bot | `.` |
| `.set_quote_reaction <emoji>`  | Set a new reaction **emoji** to Quote a message | 🏅 |
| `.set_quote_channel <#text_channel>`  | Set the **channel** where the Quotes are posted  | Current channel |

# ⚡ Limitations

You can choose to **limit the number of quotes generated per person per hour** on your server if you feel the need to limit spam.
For example, you can limit each member to **quoting one post every 12 hours.**

***

# 🔴 ToDo

- [x] Add an reaction emoji by default
- [ ] Add custom_quote help entry
- [ ] Ask user confirmation before sending on the server. (should be configurable)
- [ ] Redo quote reaction if requested, and sets a limit.
- [ ] Fix empty message content when a channel is mentionned
- [ ] Fix GMT timedate to localtime
- [ ] Investigate about random bot crashes. Might be webdriver timeouts or other.
- [ ] Investigate on random custom_quote delays