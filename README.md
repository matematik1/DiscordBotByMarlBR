\# 🛡️ MarlBR Bot — LEGALIZE Community \& Dota 2 Clan Assistant



<p align="center">

&#x20; <img src="img/CONNECTED\_PANEL\_IMG\_EU.png" alt="MarlBR Banner" width="650"/>

</p>



<p align="center">

&#x20; <img src="https://img.shields.io/badge/Python-3.11%2B-blue?style=for-the-badge\&logo=python" alt="Python Version"/>

&#x20; <img src="https://img.shields.io/badge/Disnake-2.9%2B-blueviolet?style=for-the-badge\&logo=discord" alt="Disnake Version"/>

&#x20; <img src="https://img.shields.io/badge/Dota%202-API%20Integration-red?style=for-the-badge\&logo=steam" alt="Dota 2"/>

&#x20; <img src="https://img.shields.io/badge/Status-Active%20Development-success?style=for-the-badge" alt="Status"/>

</p>



\---



\## 📌 Overview



\*\*MarlBR Bot\*\* is an interactive Discord bot tailored for the \*\*LEGALIZE\*\* Discord community and the \*\*MarlBR\*\* competitive Dota 2 clan. It automates server management, handles clan membership synchronization, verifies Steam accounts via in-game profile inspection, and dynamically assigns rank roles corresponding to active Dota 2 medals.



\---



\## ✨ Key Features



\### 🎮 Dota 2 Clan \& Profile Integration

\- \*\*Steam Account Verification:\*\* Secure linking flow using verification codes placed inside Steam's `Real Name` field.

\- \*\*Rank Tier Synchronization:\*\* Automatic fetching of rank tiers via OpenDota/Steam APIs with dynamic Discord role assignment (`Recruit` to `Immortal`).

\- \*\*Profile Quick Links:\*\* Fast access buttons to third-party tracker statistics including Dotabuff, OpenDota, and Stratz.

\- \*\*Item \& Hero Visualizers:\*\* Dynamic Pillow-powered inventory assembly and custom hero asset previews.



\### 🌐 Interactive Webhook \& Connection Panel

\- \*\*Persistent Connection Views:\*\* Interactive buttons that never expire across bot restarts (`timeout=None`).

\- \*\*Modal Input:\*\* Clean modal windows for members to submit their Steam ID or Friend ID without cluttering public channels.

\- \*\*Bilingual Interface:\*\* Support for English and Russian localized UI cards and guidance messages.



\### ⚙️ Guild Economy \& Automated Scheduling

\- \*\*Automated Salary Loop:\*\* Timed payouts tied to server roles with cross-guild deduplication and troll-role protection.

\- \*\*Admin Control Suite:\*\* Remote process control with persistent voice state cleanup and restart handlers.



\---



\## 🏗️ Project Architecture


├── img/                               # Visual assets \& banner graphics

├── utils/

│   ├── commands/

│   │   ├── adm/                       # Administrative command submodules

│   │   └── dota/                      # Dota 2 verification views \& profile tools

│   │       ├── subcom/connect\_cmd.py  # Verification logic \& code generation

│   │       └── helpers.py             # Steam API callers \& role mappers

│   ├── slash\_commands/

│   │   └── adm/                       # Application command handlers (close, restart)

│   ├── webhook/                       # Webhook \& UI panel system

│   │   ├── helpers.py                 # Embed templates \& localized text

│   │   ├── views.py                   # ConnectModal \& ConnectProfileView

│   │   ├── webhook\_cog.py             # Main slash command group \& Cog registration

│   │   └── subcom/

│   │       └── connect\_panel.py       # Channel panel dispatch handler

│   ├── config.py                      # Bot tokens, API keys, role configurations

│   └── storage.py                     # Account linking database handlers

├── main.py                            # Entry point, event loop \& Cog loader

└── README.md

---


\## 🚀 Getting Started



\### Prerequisites



\- Python 3.10+ (Python 3.11+ recommended)

\- Steam Web API Key (https://steamcommunity.com/dev/apikey)

\- Discord Bot Token with Message Content and Server Members Gateway Intents enabled.



\### Installation



1\. Clone the repository:

&#x20;  git clone https://github.com/matematik1/DiscordBotByMarlBR.git

&#x20;  cd DiscordBotByMarlBR



2\. Set up a virtual environment:

&#x20;  python -m venv venv

&#x20;  source venv/bin/activate  # On Windows: venv\\Scripts\\activate



3\. Install dependencies:

&#x20;  pip install -r requirements.txt



4\. Configuration:

&#x20;  Configure your environment variables or update utils/config.py:

&#x20;  BOT\_TOKEN = "YOUR\_DISCORD\_BOT\_TOKEN"

&#x20;  STEAM\_API\_KEY = "YOUR\_STEAM\_API\_KEY"

&#x20;  DOTA\_RANK\_ID = {

&#x20;      1: 123456789012345678,  # Recruit

&#x20;      8: 123456789012345678   # Immortal

&#x20;  }



5\. Run the bot:

&#x20;  python main.py



\---



\## 📋 Slash Commands Overview



| Command | Scope | Description |

| :--- | :--- | :--- |

| `/webhook panel` | Admins | Dispatches the interactive profile link card to the designated channel. |

| `/adm restart` | Admins | Gracefully disconnects voice sessions and reboots the bot instance. |

| `/adm close` | Admins | Terminates Gateway connection and safely halts execution. |

| `!dota connect <id>` | Members | Prefix-based direct Steam ownership verification flow. |



\---



\## 🛡️ License



Distributed under the MIT License. See `LICENSE` for further details. Built specifically for \*\*LEGALIZE\*\* and Clan \*\*MarlBR\*\*.

