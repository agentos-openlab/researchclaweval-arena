# Built-in adapter notes

All built-in routes are marked `experimental` until they complete a fresh end-to-end run and artifact review. Check the route catalogue before starting a batch:

```bash
python3 scripts/arena.py list
```

Adapter manifests pin upstream revisions and declare the available topics. Two routes have additional requirements:

- **AI-Scientist-v2** currently accepts `gpt-4o-2024-05-13`, `gpt-4o-2024-08-06`, or `gpt-4o-mini-2024-07-18`. Its native ideation and feedback paths share this allowlist. The configured API service must provide the selected model.
- **ARIS** uses the upstream Linux x86_64 release binary. Its image cannot be built for other CPU architectures.

For every route, select an API provider that supports the framework's model and API requirements. Configure the endpoint, key, and model in a local `.env` file; the repository does not choose a provider.
