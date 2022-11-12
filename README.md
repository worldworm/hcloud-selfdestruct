<h1 align="center">💣 hcloud-selfdestruct</h1>
<p align="center">
  <i>A cli tool to self destruct a hetzner cloud server</i>
</p>


## Why

Are you using a hetzner cloud server for heavy and long-running computing power? But you don't want to have additional costs when the calculation is done?

With hcloud-selfdestruct, the server instance now self-destructs after the computation and generates no further costs.

> **Warning**
> This tool is in early development and may not work as expected.


## Installation
```bash
pip install hcloud-selfdestruct
```
## Usage
```
longrunningcommand && hcloud-selfdestruct --api-token abcdefg &
#-- or --
sleep 1h && hcloud-selfdestruct --api-token abcdefg --server-id 12345678 --apprise-id gotify://example.com/token &
```

## Help
```
> hcloud-selfdestruct --help
usage: hcloud-selfdestruct [-h] --api-token API_TOKEN [--server-id SERVER_ID] [--apprise-id APPRISE_ID] [--shutdown]

cli tool to self destruct a hetzner cloud server

options:
  -h, --help            show this help message and exit
  --api-token API_TOKEN, --api API_TOKEN, --token API_TOKEN
                        hetzner cloud api token

  --server-id SERVER_ID, --server SERVER_ID, --id SERVER_ID
                        server id

  --apprise-id APPRISE_ID, --apprise APPRISE_ID, --notify APPRISE_ID
                        apprise notification string

  --shutdown            just shutdown the server and not destroy it
```

Find the apprise syntax here: [apprise wiki](https://github.com/caronc/apprise/wiki#notification-services)

Find the server id here (enter without "#")
![How to find the server id](./media/howToFindServerId.png "How to find the server id")

## Not yet tested
- server instances with mounted volume
- additional addons that could prevent deletion
- complete self detection
---
<p align="center">
  <i>© <a href="https://github.com/worldworm">worldworm</a> 2022</i><br>
  <i>Licensed under <a href="https://github.com/worldworm/hcloud-selfdestruct/blob/main/LICENSE">MIT</a></i><br>
</p>
