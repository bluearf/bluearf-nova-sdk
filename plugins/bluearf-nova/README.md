# Bluearf Nova Codex Plugin

This plugin lets Codex use the Bluearf Nova Public API through the official
Python SDK and CLI.

## Install

Install or expose this plugin folder to Codex:

```text
plugins/bluearf-nova
```

Then set a customer API token:

```bash
export BLUEARF_NOVA_API_TOKEN="..."
```

## Check

```bash
plugins/bluearf-nova/scripts/check-bluearf-nova
```

## Example

```bash
plugins/bluearf-nova/scripts/bluearf-nova credits get
plugins/bluearf-nova/scripts/bluearf-nova vehicles list --company-id COMPANY_ID --limit 25
```

