---
name: home-assistant-manager
description: Expert-level Home Assistant configuration management with Samba-mounted config, HA MCP server, hass-cli, SSH, REST API, Context7 docs, git workflows, automation verification, and Lovelace dashboard management.
---

# Home Assistant Manager

Expert-level Home Assistant configuration management with direct file access, multiple control interfaces, and verification protocols.

## Core Capabilities

- **Direct file editing** via Samba mount at `~/homelab/ha-config/`
- **HA MCP server** for device/entity control (turn on/off, set values, media control)
- **hass-cli** for quick state checks and service calls
- **SSH** to HAOS for `ha core check/restart/logs`
- **REST API** via curl for service calls and template rendering
- **Context7 MCP** for up-to-date HA documentation lookups
- **Git repo** at github.com/cconner8704/home-assistant-config (private)
- Automation testing and verification protocols
- Reload vs restart optimization
- Lovelace dashboard development
- Template syntax patterns and debugging

## Our Environment

```
Home Assistant:  http://homeassistant.local:8123 (HAOS, NOT behind Traefik)
Samba mount:     ~/homelab/ha-config/ (direct read/write to /config)
SSH:             ssh root@homeassistant.local (port 22)
Git repo:        ~/homelab/ha-config/.git → github.com/cconner8704/home-assistant-config
hass-cli:        installed in project .venv, uses $HASS_SERVER + $HASS_TOKEN
Env vars:        loaded from Infisical via direnv (.envrc)
Secrets:         secrets.yaml (gitignored), also in Infisical at /infrastructure
MCP servers:     Home Assistant MCP, Context7 MCP
Presence:        OwnTracks (Chris), HA Companion App (iPhone 17)
```

## Access Methods (Priority Order)

1. **HA MCP** — entity control, state queries (e.g., turn on lights, check sensors)
2. **Samba mount** — edit YAML configs directly (no scp needed!)
3. **hass-cli** — quick state checks, service calls from terminal
4. **REST API (curl)** — reload services, render templates, fire events
5. **SSH** — `ha core check/restart/logs`, config validation
6. **Context7** — look up current HA docs for integrations, automations, templates

## Remote Access Patterns

### Using curl (Direct REST API)

```bash
# List all states
curl -s -H "Authorization: Bearer $HASS_TOKEN" \
  http://homeassistant.local:8123/api/states | python3 -m json.tool | head -50

# Get specific entity state
curl -s -H "Authorization: Bearer $HASS_TOKEN" \
  http://homeassistant.local:8123/api/states/sensor.entity_name

# Call a service (e.g., reload automations)
curl -s -X POST \
  -H "Authorization: Bearer $HASS_TOKEN" \
  -H "Content-Type: application/json" \
  http://homeassistant.local:8123/api/services/automation/reload

# Trigger an automation
curl -s -X POST \
  -H "Authorization: Bearer $HASS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "automation.name"}' \
  http://homeassistant.local:8123/api/services/automation/trigger

# Fire an event
curl -s -X POST \
  -H "Authorization: Bearer $HASS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"key": "value"}' \
  http://homeassistant.local:8123/api/events/my_event

# Render a template
curl -s -X POST \
  -H "Authorization: Bearer $HASS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"template": "{{ states(\"sensor.temperature\") }}"}' \
  http://homeassistant.local:8123/api/template

# Reload specific domains (no restart needed)
# automation, script, scene, template, group
curl -s -X POST -H "Authorization: Bearer $HASS_TOKEN" \
  http://homeassistant.local:8123/api/services/automation/reload
curl -s -X POST -H "Authorization: Bearer $HASS_TOKEN" \
  http://homeassistant.local:8123/api/services/script/reload
curl -s -X POST -H "Authorization: Bearer $HASS_TOKEN" \
  http://homeassistant.local:8123/api/services/scene/reload
curl -s -X POST -H "Authorization: Bearer $HASS_TOKEN" \
  http://homeassistant.local:8123/api/services/template/reload
curl -s -X POST -H "Authorization: Bearer $HASS_TOKEN" \
  http://homeassistant.local:8123/api/services/group/reload
```

### Using hass-cli (Local, via REST API)

All `hass-cli` commands use environment variables automatically:

```bash
# List entities
hass-cli state list

# Get specific state
hass-cli state get sensor.entity_name

# Call services
hass-cli service call automation.reload
hass-cli service call automation.trigger --arguments entity_id=automation.name
```

### Using SSH for HA CLI

```bash
# Check configuration validity
ssh root@homeassistant.local "ha core check"

# Restart Home Assistant
ssh root@homeassistant.local "ha core restart"

# View logs
ssh root@homeassistant.local "ha core logs"

# Tail logs with grep
ssh root@homeassistant.local "ha core logs | grep -i error | tail -20"
```

## Deployment Workflows

### How It Works (Samba Mount)

Our HA config is mounted via Samba at `~/homelab/ha-config/`. Edits go directly to the live HA config — **no scp needed**. Changes are immediate on disk but HA needs a reload/restart to pick them up.

### Standard Workflow

```bash
# 1. Edit files directly (they're already on HA via Samba)
#    Use Read/Write/Edit tools on ~/homelab/ha-config/*.yaml

# 2. Check validity
ssh root@homeassistant.local "ha core check"

# 3. Reload or restart
hass-cli service call automation.reload  # if reload sufficient
# OR
ssh root@homeassistant.local "ha core restart"  # if restart needed

# 4. Verify
hass-cli state get sensor.new_entity
ssh root@homeassistant.local "ha core logs | grep -i error | tail -20"

# 5. Commit when stable
cd ~/homelab/ha-config
git add file.yaml
git commit -m "Description"
git push
```

### Key Difference: No scp or git pull needed!

The Samba mount means the file you edit IS the file HA reads. The workflow is:
- **Edit** → file is already on HA
- **Reload/restart** → HA picks up changes
- **Verify** → check logs and states
- **Commit** → git tracks the change

For dashboards (.storage/ files), just edit and refresh the browser — no restart needed.

## Reload vs Restart Decision Making

**ALWAYS assess if reload is sufficient before requiring a full restart.**

### Can be reloaded (fast, preferred):
- ✅ Automations: `hass-cli service call automation.reload`
- ✅ Scripts: `hass-cli service call script.reload`
- ✅ Scenes: `hass-cli service call scene.reload`
- ✅ Template entities: `hass-cli service call template.reload`
- ✅ Groups: `hass-cli service call group.reload`
- ✅ Themes: `hass-cli service call frontend.reload_themes`

### Require full restart:
- ❌ Min/Max sensors and platform-based sensors
- ❌ New integrations in configuration.yaml
- ❌ Core configuration changes
- ❌ MQTT sensor/binary_sensor platforms

## Automation Verification Workflow

**ALWAYS verify automations after deployment:**

### Step 1: Deploy
```bash
git add automations.yaml && git commit -m "..." && git push
ssh root@homeassistant.local "cd /config && git pull"
```

### Step 2: Check Configuration
```bash
ssh root@homeassistant.local "ha core check"
```

### Step 3: Reload
```bash
hass-cli service call automation.reload
```

### Step 4: Manually Trigger
```bash
hass-cli service call automation.trigger --arguments entity_id=automation.name
```

**Why trigger manually?**
- Instant feedback (don't wait for scheduled triggers)
- Verify logic before production
- Catch errors immediately

### Step 5: Check Logs
```bash
sleep 3
ssh root@homeassistant.local "ha core logs | grep -i 'automation_name' | tail -20"
```

**Success indicators:**
- `Initialized trigger AutomationName`
- `Running automation actions`
- `Executing step ...`
- No ERROR or WARNING messages

**Error indicators:**
- `Error executing script`
- `Invalid data for call_service`
- `TypeError`, `Template variable warning`

### Step 6: Verify Outcome

**For notifications:**
- Ask user if they received it
- Check logs for mobile_app messages

**For device control:**
```bash
hass-cli state get switch.device_name
```

**For sensors:**
```bash
hass-cli state get sensor.new_sensor
```

### Step 7: Fix and Re-test if Needed
If errors found:
1. Identify root cause from error messages
2. Fix the issue
3. Re-deploy (steps 1-2)
4. Re-verify (steps 3-6)

## Dashboard Management

### Dashboard Fundamentals

**What are Lovelace Dashboards?**
- JSON files in `.storage/` directory (e.g., `.storage/lovelace.control_center`)
- UI configuration for Home Assistant frontend
- Optimizable for different devices (mobile, tablet, wall panels)

**Critical Understanding:**
- Creating dashboard file is NOT enough - must register in `.storage/lovelace_dashboards`
- Dashboard changes don't require HA restart (just browser refresh)
- Use panel view for full-screen content (maps, cameras)
- Use sections view for organized multi-card layouts

### Dashboard Development Workflow

**Direct editing via Samba mount:**

```bash
# 1. Edit dashboard file directly (it's already on HA)
#    ~/homelab/ha-config/.storage/lovelace.control_center

# 2. Refresh browser (Ctrl+F5 or Cmd+Shift+R)
#    No HA restart needed!

# 3. Iterate until perfect

# 4. Commit when stable (dashboards are gitignored by default)
```

**Why this is fast:**
- File edits are instant on HA via Samba
- No scp, no git pull, no deploy step
- Just edit → refresh browser

### Creating New Dashboard

**Complete workflow:**

```bash
# Step 1: Create dashboard file (via Samba mount)
cp ~/homelab/ha-config/.storage/lovelace.my_home ~/homelab/ha-config/.storage/lovelace.new_dashboard

# Step 2: Register in lovelace_dashboards
# Edit ~/homelab/ha-config/.storage/lovelace_dashboards to add:
{
  "id": "new_dashboard",
  "show_in_sidebar": true,
  "icon": "mdi:tablet-dashboard",
  "title": "New Dashboard",
  "require_admin": false,
  "mode": "storage",
  "url_path": "new-dashboard"
}

# Step 3: Files are already on HA (Samba mount) — no deploy step!

# Step 4: Restart HA (required for registry changes)
ssh root@homeassistant.local "ha core restart"
sleep 30

# Step 5: Verify appears in sidebar
```

**Update .gitignore to track:**
```gitignore
# Exclude .storage/ by default
.storage/

# Include dashboard files
!.storage/lovelace.new_dashboard
!.storage/lovelace_dashboards
```

### View Types Decision Matrix

**Use Panel View when:**
- Displaying full-screen map (vacuum, cameras)
- Single large card needs full width
- Want zero margins/padding
- Minimize scrolling

**Use Sections View when:**
- Organizing multiple cards
- Need responsive grid layout
- Building multi-section dashboards

**Layout Example:**
```json
// Panel view - full width, no margins
{
  "type": "panel",
  "title": "Vacuum Map",
  "path": "map",
  "cards": [
    {
      "type": "custom:xiaomi-vacuum-map-card",
      "entity": "vacuum.dusty"
    }
  ]
}

// Sections view - organized, has ~10% margins
{
  "type": "sections",
  "title": "Home",
  "sections": [
    {
      "type": "grid",
      "cards": [...]
    }
  ]
}
```

### Card Types Quick Reference

**Mushroom Cards (Modern, Touch-Optimized):**
```json
{
  "type": "custom:mushroom-light-card",
  "entity": "light.living_room",
  "use_light_color": true,
  "show_brightness_control": true,
  "collapsible_controls": true,
  "fill_container": true
}
```
- Best for tablets and touch screens
- Animated, colorful icons
- Built-in slider controls

**Mushroom Template Card (Dynamic Content):**
```json
{
  "type": "custom:mushroom-template-card",
  "primary": "All Doors",
  "secondary": "{% set sensors = ['binary_sensor.front_door'] %}\n{% set open = sensors | select('is_state', 'on') | list | length %}\n{{ open }} / {{ sensors | length }} open",
  "icon": "mdi:door",
  "icon_color": "{% if open > 0 %}red{% else %}green{% endif %}"
}
```
- Use Jinja2 templates for dynamic content
- Color-code status with icon_color
- Multi-line templates use `\n` in JSON

**Tile Card (Built-in, Modern):**
```json
{
  "type": "tile",
  "entity": "climate.thermostat",
  "features": [
    {"type": "climate-hvac-modes", "hvac_modes": ["heat", "cool", "fan_only", "off"]},
    {"type": "target-temperature"}
  ]
}
```
- No custom cards required
- Built-in features for controls

### Common Template Patterns

**Counting Open Doors:**
```jinja2
{% set door_sensors = [
  'binary_sensor.front_door',
  'binary_sensor.back_door'
] %}
{% set open = door_sensors | select('is_state', 'on') | list | length %}
{{ open }} / {{ door_sensors | length }} open
```

**Color-Coded Days Until:**
```jinja2
{% set days = state_attr('sensor.bin_collection', 'daysTo') | int %}
{% if days <= 1 %}red
{% elif days <= 3 %}amber
{% elif days <= 7 %}yellow
{% else %}grey
{% endif %}
```

**Conditional Display:**
```jinja2
{% set bins = [] %}
{% if days and days | int <= 7 %}
  {% set bins = bins + ['Recycling'] %}
{% endif %}
{% if bins %}This week: {{ bins | join(', ') }}{% else %}None this week{% endif %}
```

**IMPORTANT:** Always use `| int` or `| float` to avoid type errors when comparing

### Tablet Optimization

**Screen-specific layouts:**
- 11-inch tablets: 3-4 columns
- Touch targets: minimum 44x44px
- Minimize scrolling: Use panel view for full-screen
- Visual feedback: Color-coded status (red/green/amber)

**Grid Layout for Tablets:**
```json
{
  "type": "grid",
  "columns": 3,
  "square": false,
  "cards": [
    {"type": "custom:mushroom-light-card", "entity": "light.living_room"},
    {"type": "custom:mushroom-light-card", "entity": "light.bedroom"}
  ]
}
```

### Common Dashboard Pitfalls

**Problem 1: Dashboard Not in Sidebar**
- **Cause:** File created but not registered
- **Fix:** Add to `.storage/lovelace_dashboards` and restart HA

**Problem 2: "Configuration Error" in Card**
- **Cause:** Custom card not installed, wrong syntax, template error
- **Fix:**
  - Check HACS for card installation
  - Check browser console (F12) for details
  - Test templates in Developer Tools → Template

**Problem 3: Auto-Entities Fails**
- **Cause:** `card_param` not supported by card type
- **Fix:** Use cards that accept `entities` parameter:
  - ✅ Works: `entities`, `vertical-stack`, `horizontal-stack`
  - ❌ Doesn't work: `grid`, `glance` (without specific syntax)

**Problem 4: Vacuum Map Has Margins/Scrolling**
- **Cause:** Using sections view (has margins)
- **Fix:** Use panel view for full-width, no scrolling

**Problem 5: Template Type Errors**
- **Error:** `TypeError: '<' not supported between instances of 'str' and 'int'`
- **Fix:** Use type filters: `states('sensor.days') | int < 7`

### Dashboard Debugging

**1. Browser Console (F12):**
- Check for red errors when loading dashboard
- Common: "Custom element doesn't exist" → Card not installed

**2. Validate JSON Syntax:**
```bash
python3 -m json.tool .storage/lovelace.control_center > /dev/null
```

**3. Test Templates:**
```
Home Assistant → Developer Tools → Template
Paste template to test before adding to dashboard
```

**4. Verify Entities:**
```bash
hass-cli state get binary_sensor.front_door
```

**5. Clear Browser Cache:**
- Hard refresh: Ctrl+F5 or Cmd+Shift+R
- Try incognito window

## Real-World Examples

### Quick Controls Dashboard Section
```json
{
  "type": "grid",
  "title": "Quick Controls",
  "cards": [
    {
      "type": "custom:mushroom-template-card",
      "primary": "All Doors",
      "secondary": "{% set doors = ['binary_sensor.front_door', 'binary_sensor.back_door'] %}\n{% set open = doors | select('is_state', 'on') | list | length %}\n{{ open }} / {{ doors | length }} open",
      "icon": "mdi:door",
      "icon_color": "{% if open > 0 %}red{% else %}green{% endif %}"
    },
    {
      "type": "tile",
      "entity": "climate.thermostat",
      "features": [
        {"type": "climate-hvac-modes", "hvac_modes": ["heat", "cool", "fan_only", "off"]},
        {"type": "target-temperature"}
      ]
    }
  ]
}
```

### Individual Light Cards (Touch-Friendly)
```json
{
  "type": "grid",
  "title": "Lights",
  "columns": 3,
  "cards": [
    {
      "type": "custom:mushroom-light-card",
      "entity": "light.office_studio",
      "name": "Office",
      "use_light_color": true,
      "show_brightness_control": true,
      "collapsible_controls": true
    }
  ]
}
```

### Full-Screen Vacuum Map
```json
{
  "type": "panel",
  "title": "Vacuum",
  "path": "vacuum-map",
  "cards": [
    {
      "type": "custom:xiaomi-vacuum-map-card",
      "vacuum_platform": "Tasshack/dreame-vacuum",
      "entity": "vacuum.dusty"
    }
  ]
}
```

## Common Commands Quick Reference

```bash
# Configuration
ssh root@homeassistant.local "ha core check"
ssh root@homeassistant.local "ha core restart"

# Logs
ssh root@homeassistant.local "ha core logs | tail -50"
ssh root@homeassistant.local "ha core logs | grep -i error | tail -20"

# State/Services (hass-cli)
hass-cli state list
hass-cli state get entity.name
hass-cli service call automation.reload
hass-cli service call automation.trigger --arguments entity_id=automation.name

# State/Services (HA MCP — preferred for entity control)
# Use mcp__Home_Assistant__HassTurnOn, HassTurnOff, HassLightSet, etc.

# Edit config (Samba mount — no scp needed)
# Files at ~/homelab/ha-config/ are live on HA

# Commit when stable
cd ~/homelab/ha-config && git add . && git commit -m "..." && git push

# Dashboard (edit directly, refresh browser)
# ~/homelab/ha-config/.storage/lovelace.* files
python3 -m json.tool ~/homelab/ha-config/.storage/lovelace.my_dashboard > /dev/null  # Validate JSON

# Quick test cycle
# 1. Edit ~/homelab/ha-config/automations.yaml
# 2. Reload
hass-cli service call automation.reload
# 3. Test
hass-cli service call automation.trigger --arguments entity_id=automation.name
# 4. Check logs
ssh root@homeassistant.local "ha core logs | grep -i 'automation' | tail -10"
```

## Best Practices Summary

1. **Always check configuration** before restart: `ha core check`
2. **Prefer reload over restart** when possible
3. **Test automations manually** after deployment
4. **Check logs** for errors after every change
5. **Edit via Samba mount** — files are live on HA, no deploy step
6. **Verify outcomes** — don't assume it worked
7. **Use Context7 MCP** for current HA documentation
8. **Use HA MCP** for entity control (not curl for on/off)
9. **Test templates in Dev Tools** before adding to dashboards
10. **Validate JSON syntax** before deploying dashboards
11. **Commit only stable versions** — test first, git after
12. **Secrets in secrets.yaml** (gitignored) + Infisical

## Workflow Decision Tree

```
Configuration Change Needed
├─ Edit file via Samba mount (~/homelab/ha-config/)
├─ Check configuration valid: ha core check
├─ Needs restart?
│  ├─ YES → ha core restart
│  └─ NO → Use appropriate reload (automation, script, scene, etc.)
├─ Verify in logs
├─ Test outcome (hass-cli or HA MCP)
└─ Commit to git when stable

Dashboard Change Needed
├─ Edit .storage/ file directly
├─ Refresh browser (Ctrl+F5)
├─ Test on target device
├─ Iterate until perfect
└─ Commit to git when stable (if tracked)
```

---

This skill is customized for our environment: Samba-mounted config, HA MCP server, Infisical secrets, Context7 docs, OwnTracks presence, and direct file access. No scp needed.
