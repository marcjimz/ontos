# Authentication for Databricks Apps

## How It Works

The `setup_ontos_demo.py` script supports two authentication modes:

### Local Development (No Authentication)
```bash
python demo/setup_ontos_demo.py --base-url http://localhost:8000
```

When running against a local backend, no authentication is required. The backend uses mock user credentials for local development.

### Databricks Apps (Identity Token)
```bash
python demo/setup_ontos_demo.py \
  --base-url https://app-name.aws.databricksapps.com \
  --databricks-profile e2-demo-field-eng
```

When running against a deployed Databricks App, the script uses `databricks auth token` to get an identity token:

1. **Get identity token**: Runs `databricks auth token --profile <profile>`
2. **Parse JSON response**: Extracts `access_token` from the JSON output
3. **Add to requests**: Includes `Authorization: Bearer <token>` header in all API requests

## Setting Up Databricks CLI

### One-time Setup

Configure your Databricks CLI profile:

```bash
# Install Databricks CLI
pip install databricks-cli

# Login with OAuth (opens browser)
databricks auth login --profile e2-demo-field-eng
```

Follow the browser prompts to authenticate. This creates a profile in `~/.databrickscfg` and stores OAuth tokens in `~/.databricks/token-cache.json`.

### Verifying Configuration

Test that authentication works:

```bash
# Get an identity token
databricks auth token --profile e2-demo-field-eng

# Should output JSON like:
# {
#   "access_token": "eyJ...",
#   "token_type": "Bearer",
#   "expiry": "2026-01-06T15:40:47...",
#   "expires_in": 3600
# }
```

Test API access with curl:

```bash
# Get token and test endpoint
TOKEN=$(databricks auth token --profile e2-demo-field-eng | jq -r .access_token)
curl -H "Authorization: Bearer $TOKEN" https://your-app.aws.databricksapps.com/api/version

# Should return JSON like:
# {"version":"0.1.0","startTime":1767733427,"timestamp":1767737813}
```

## How the Script Uses the Token

When you run:

```bash
python demo/setup_ontos_demo.py \
  --base-url https://app-name.aws.databricksapps.com \
  --databricks-profile e2-demo-field-eng
```

The script:

1. **Executes**: `databricks auth token --profile e2-demo-field-eng`
2. **Captures**: The stdout JSON response
3. **Parses**: `json.loads(output)` to get the token data
4. **Extracts**: `token_data['access_token']` field
5. **Stores**: The access token for use in requests
6. **Adds header**: `Authorization: Bearer <access_token>` to all HTTP requests

## Token Lifecycle

- **Expiry**: Tokens typically expire after 1 hour (3600 seconds)
- **Refresh**: The `databricks auth token` command automatically refreshes expired tokens
- **Caching**: Tokens are cached in `~/.databricks/token-cache.json`
- **Renewal**: Each script run gets a fresh token (or refreshed if expired)

## Troubleshooting

### Error: "databricks CLI not found"

Install the Databricks CLI:
```bash
pip install databricks-cli
```

### Error: "Failed to get identity token"

Configure your profile:
```bash
databricks auth login --profile e2-demo-field-eng
```

### Error: "Invalid header" or "Authentication failed"

1. Check that the profile is configured:
   ```bash
   databricks auth token --profile e2-demo-field-eng
   ```

2. Verify the app URL is correct (should end in `.databricksapps.com`)

3. Check that you have access to the Databricks App in the browser

### Token Shows as JSON in Error

This is expected! The script parses the JSON to extract just the `access_token` field. If you see this error, it means the parsing failed. Check that you're using `databricks-cli` version 0.17+ which outputs JSON format.

## Comparison with Direct OAuth

You might wonder why we use `databricks auth token` instead of reading from the token cache directly. Here's why:

| Approach | How It Works | Issues |
|----------|--------------|---------|
| **Token cache** | Read `~/.databricks/token-cache.json` | Tokens from cache don't work with Databricks Apps - they're workspace tokens, not app tokens |
| **databricks auth token** | CLI generates proper identity token | ✅ Works correctly - generates app-compatible tokens |

The `databricks auth token` command generates a proper identity token that works with Databricks Apps, while tokens in the cache are workspace API tokens that don't work for app authentication.

## Code Reference

See `demo/setup_ontos_demo.py` lines 36-64 for the token acquisition logic:

```python
# Get identity token if using Databricks profile
if databricks_profile:
    print(f"  Getting identity token for profile: {databricks_profile}")
    result = subprocess.run(
        ['databricks', 'auth', 'token', '--profile', databricks_profile],
        capture_output=True,
        text=True,
        check=True
    )
    # Parse JSON output to get access_token
    token_data = json.loads(result.stdout)
    self.identity_token = token_data['access_token']
```

And lines 68-78 for how it's used:

```python
def _make_request(self, method: str, path: str, **kwargs):
    url = f"{self.base_url}{path}"

    # Add identity token if using Databricks profile
    if self.identity_token:
        if 'headers' not in kwargs:
            kwargs['headers'] = {}
        kwargs['headers']['Authorization'] = f'Bearer {self.identity_token}'

    return self.session.request(method, url, **kwargs)
```
