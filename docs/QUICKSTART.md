# Quickstart — local cockpit, no cloud deployment

**Outcome:** start the CAPT-Bot UI bridge, see the local operator page, and identify whether it can query a compatible CAPT Core. This is **not** a Bot-autonomy or R5 acceptance test.

## Before starting

You need a checkout of **this** repository and an existing healthy [CAPT Core](https://github.com/knowurknottty/CAPT_core) RuntimeService on the **same machine**, with a readable authorized Unix socket and token file. There is no standalone Core installer in this repository; see [Installation](INSTALLATION.md).

## Steps

1. In the CAPT-Bot checkout, use the Python environment already configured for CAPT Core. Start:

   ```zsh
   python3 -m capt_bot.ui_server \
     --core-root /absolute/path/to/CAPT_core \
     --sock "$HOME/.capt/runtime.sock" \
     --token-file "$HOME/.capt/runtime.token" \
     --host 127.0.0.1 --port 8765
   ```

2. Look for `CAPT_BOT_UI_READY http://127.0.0.1:8765`. If the process exits, resolve the Core/socket/token failure; see [Troubleshooting](TROUBLESHOOTING.md).
3. On the same machine, open [http://127.0.0.1:8765](http://127.0.0.1:8765). For an optional **bridge-only** probe:

   ```zsh
   curl --fail --silent http://127.0.0.1:8765/api/health
   ```

   An `{"ok":true}` response proves only that this HTTP bridge answered.
4. Inspect the cockpit runtime state and available Bots. If the resident Core lacks the `bots` query or `register_bot` command, stop rather than writing directly into Core's storage.
5. Follow [Human operator guide → Create a Bot identity](PUBLIC_USER_GUIDE.md#create-a-bot-identity) **only if** you are ready to create durable identity state and are an authorized human operator.

## Stop conditions

Do **not** expose the UI beyond loopback; put an authentication proxy in front and call it secure; or treat a visible button as Core admission. Do not issue model runs, spend credits, or approve consequential actions merely to complete the quickstart.

**Next:** [User guide](PUBLIC_USER_GUIDE.md) · [Cheatsheet](CHEATSHEET.md) · [Status and limits](COMPATIBILITY.md).
