# HorizonOS Native Services

Each service directory owns one native daemon and its tests.

Initial service ownership follows the repository architecture baseline:

- `policy/` for signed bundle ingestion and effective-policy materialization.
- `systemext/` for bridge validation, authorization, dispatch, and auditing.
