# wattweight

A Python project for energy management.

`wattweight` is a command-line tool to track and manage energy data from various devices. It allows you to register devices, record measurements, and manage the underlying database.

## Installation

You can install `wattweight` using pip. It is recommended to install it in a virtual environment.

```bash
pip install .
```

This will install the `wattweight` command-line tool.

## Usage

The `wattweight` tool has several commands to manage devices, measurements, and the database.

### Device Management

You can add, list, modify, and remove devices.

**Add a new device:**

```bash
wattweight device add <identifier> <name> [options]
```

Example:
```bash
wattweight device add "tplink-plug-1" "Living Room TV" --idle-power 5.0
```

**List devices:**

```bash
wattweight device list
```

**Modify a device:**

```bash
wattweight device modify <identifier> [options]
```

Example:
```bash
wattweight device modify "tplink-plug-1" --name "LR TV"
```

**Remove a device:**

```bash
wattweight device remove <identifier>
```

### Measurement Management

You can add and list measurements for each device.

**Add a new measurement:**

```bash
wattweight measurement add <device_identifier> <value>
```

Example:
```bash
wattweight measurement add "tplink-plug-1" 120.5
```

**List measurements for a device:**

```bash
wattweight measurement list <device_identifier>
```

### Database Migrations

The tool uses Alembic for database migrations.

**Upgrade the database:**

To apply the latest database migrations, run:

```bash
wattweight db upgrade
```

**Create a new migration:**

When you change the data models in `src/wattweight/model`, you need to create a new migration.

```bash
wattweight db migrate "Your migration message"
```

## Development

To set up a development environment, clone the repository and install the project with the `dev` dependencies.

```bash
git clone https://github.com/krmarien/wattweight.git
cd wattweight
pip install -e .[dev]
```

This will install the project in editable mode and include development tools like `pytest`, `black`, `flake8`, and `mypy`.

### Running tests

To run the test suite, use `pytest`:

```bash
pytest
```
