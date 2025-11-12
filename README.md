<div align="center">
  <img src="img/logo.jpg" alt="anyID logo" width="200"/>
</div>

# anyID

A unified Python library for generating a variety of unique identifiers.

`anyid` provides a simple and consistent interface for generating different kinds of IDs, from classic UUIDs to modern sortable identifiers like ULID and KSUID. It's lightweight, type-annotated, and has minimal dependencies.

## Supported Identifiers

| ID Type     | Sortable | Length (chars) | URL Safe | Notes                                                      |
| :---------- | :------- | :------------- | :------- | :--------------------------------------------------------- |
| **CUID**    | Yes      | 25             | Yes      | Collision-resistant for horizontal scaling.                |
| **CUID2**   | No       | 24 (default)   | Yes      | An improved, more secure version of CUID.                  |
| **KSUID**   | Yes      | 27             | Yes      | K-Sortable Unique Identifier.                              |
| **NanoID**  | No       | 21 (default)   | Yes      | Secure, URL-friendly, and fast.                            |
| **ShortUUID** | No       | ~22            | Yes      | A shorter, URL-safe version of a standard UUID.            |
| **Snowflake** | Yes      | 19 (integer)   | No       | Twitter's distributed, time-sortable ID generator.         |
| **ULID**    | Yes      | 26             | Yes      | Universally Unique Lexicographically Sortable Identifier.  |
| **UUID**    | No       | 36             | No       | The classic, ubiquitous UUID v4.                           |
| **XID**     | Yes      | 20             | Yes      | Globally unique ID that is sortable by time.               |

## Installation

```bash
pip install anyid
```

## Usage

The API is simple and consistent across all ID types.

```python
from anyid import cuid, ulid, uuid

# Generate a CUID
my_cuid = cuid()
print(f"CUID: {my_cuid}")

# Generate a ULID
my_ulid = ulid()
print(f"ULID: {my_ulid}")

# Generate a UUID (v4)
my_uuid = uuid()
print(f"UUID: {my_uuid}")
```

## Contributing

Contributions are welcome! This project uses `pytest` for testing and `ruff` and `black` for linting and formatting. Please feel free to open an issue or submit a pull request.

## Credits
- Logo created by Grok
- Thanks Copilot for reviewing my code
- Thanks Gemini CLI for helping me with bug fixes and tests
