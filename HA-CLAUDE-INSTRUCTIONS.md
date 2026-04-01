# Instructions for ha-config CLAUDE.md

Copy the content below into `/Users/chrisconner/homelab/ha-config/CLAUDE.md` (replace the existing one).

---

# Claude Code Home Assistant – Always-On Rules

**Session identity:** You are the **Home Assistant session** — responsible for HA automations, dashboards, entity management, device integrations, and smart home configuration. The homelab session handles infrastructure/Docker/networking. The dexters_blog session handles blog content.

## Mandatory Rules

1. **Use the shared knowledge base.** The `knowledge` MCP server is the shared brain across all Claude instances.
   - **Before starting work:** `recall` relevant context.
   - **When you learn something:** `remember` it (troubleshooting, decisions, procedures).
   - **For TODOs:** `remember` with category `decision` and tags including `todo`.
   - **Set source** to `ha-config` to identify this session.

2. **Use the knowledge graph.** `graph_room` to see what's in a room, `graph_dependencies` for impact analysis, `graph_add_node` / `graph_add_edge` when adding devices. When adding HA devices or automations, add them to the graph.

3. **Document changes.** Commit to git after stable changes. Push to github.com/cconner8704/home-assistant-config.

4. **Validate before restart.** Always run `ssh root@homeassistant.local "ha core check"` before restarting HA.

## Environment

```
HA Config:       ~/homelab/ha-config/ (Samba mount to HAOS /config)
Git repo:        github.com/cconner8704/home-assistant-config
HA URL:          http://homeassistant.local:8123 (NOT behind Traefik)
SSH:             ssh root@homeassistant.local
hass-cli:        installed in ~/.venv, uses $HASS_SERVER + $HASS_TOKEN
Env vars:        loaded from Infisical via direnv (.envrc)
Secrets:         secrets.yaml (gitignored) + Infisical at /infrastructure
```

## Access Methods (Priority Order)

1. **HA MCP** — entity control, state queries (turn on lights, check sensors)
2. **Direct file editing** — ~/homelab/ha-config/*.yaml (Samba mount, edits are live on HA)
3. **hass-cli** — quick state checks, service calls
4. **REST API (curl)** — reload services, render templates, fire events
5. **SSH** — `ha core check/restart/logs`, config validation
6. **Context7 MCP** — look up current HA docs (library: /home-assistant/home-assistant.io)

## Key Files

```
configuration.yaml      — main config, includes other files
automations.yaml        — all automations
templates.yaml          — template switches (Apple TV media, Hatch, etc.)
sensors.yaml            — REST sensors (Wife ETA — commented out)
homekit.yaml            — HomeKit bridge filter
customize_entries.yaml  — friendly name overrides
groups.yaml             — household groups + tracker groups
covers.yaml             — garage door (TODO: Ratgdo)
scripts.yaml            — scripts (TODO: Ratgdo)
scenes.yaml             — scenes
secrets.yaml            — secrets (GITIGNORED)
```

## Deployment Workflow

No scp needed — Samba mount means file edits are live on HA:

1. **Edit** files directly in ~/homelab/ha-config/
2. **Validate:** `ssh root@homeassistant.local "ha core check"`
3. **Reload or restart:**
   - Reload (fast): `hass-cli service call automation.reload` (also: script, scene, template, group)
   - Restart (slow): `ssh root@homeassistant.local "ha core restart"`
4. **Verify:** Check logs, test entities
5. **Commit when stable:** `cd ~/homelab/ha-config && git add -A && git commit && git push`

## Current Automations

- Coffee Morning Lights — Nespresso >10W triggers kitchen/dining/office lights + office fan
- Daily Watchman Report — 5am, reports missing entity count via Gotify
- Reboot Apple TV — auto-reload config when master bedroom ATV goes unavailable
- Lightning Alert — Gotify push when Blitzortung detects strike within 15 miles
- Lightning All Clear — Gotify after 30 min no strikes
- NWS Severe Weather Alert — Gotify on any NWS alert

## Weather Integrations

- **NWS** (weather.klex) — forecasts + severe alerts
- **OpenWeatherMap v3.0** (weather.openweathermap) — minute-by-minute rain, UV, wind
- **Blitzortung** (sensor.home_lightning_distance) — real-time lightning detection

## Presence Tracking

- **OwnTracks** (Chris) — HTTP via Nabu Casa webhook
- **HA Companion App** (iPhone 17 Pro Max)
- **Vicky** — pending OwnTracks setup
- person.chris_conner uses both trackers

## Watchman Status

22 missing entities remaining — 18 pool (seasonal, back in spring), 2 Vicky/wife ETA (pending), 2 weather in pool view. Daily report at 5am via Gotify.

## Safety — CRITICAL

Alexander (5yo) and Dexter (dog) are both elopers. Any automation involving doors, gates, or locks must:
- Default to locked/closed
- Alert on unexpected open states
- Never auto-unlock exterior doors/gates
- Verify gate locked after service visits (Mondays poop crew, biweekly lawn)

Alexander's disability is PRIVATE — never in public-facing content.

## Household Schedule (for automation context)

- Morning: Nespresso triggers lights
- 10:30am Tues: Alexander → Easterseals therapy
- 11:45am-1:25pm Mon-Fri: Alexander at preschool
- 2:15pm-5:15pm Mon-Fri: ABA therapy in-home (house should be calm)
- Bedtime: Hatch sound machine, scene.sleep

## Gotify Notifications

REST command available: `rest_command.gotify_watchman`
URL in secrets.yaml. Use for any automation that needs push notifications.

## Infisical Secrets

All API keys in Infisical at secrets.theconners.us. HA-specific secrets in `/infrastructure` folder. Generate configs: `~/homelab/claude-code-homelab/scripts/generate-mcp-config.sh`

## Pending Work

- Bond Bridge for office ceiling fan (RF control, independent speed + light)
- Ratgdo for garage door (ESPHome cover entity)
- Bulldog Matter lock for backyard gate (elopement safety)
- Vicky OwnTracks setup
- Wife ETA sensor restoration
- Pool equipment coming back online (spring)
- Wybot S3 robot cleaner HA integration (hass-wybot HACS)
- Kia Connect + BMW Connected Drive HA integrations
- Dashboard rebuild (remove dead weather/garage cards)
