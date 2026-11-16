# Deploying the app

The app is `app/streamlit_app.py`. Locally: `uv sync --extra app` then `uv run streamlit run app/streamlit_app.py`.

## Streamlit Community Cloud (private)

1. Sign in at https://share.streamlit.io with the GitHub account that owns the repository, and allow Streamlit to access private repositories when asked.
2. Choose **Create app**, then **Deploy a public app from GitHub** (the app stays private for a private repository).
3. Repository `mujtabamqureshi06/priced-in`, branch `main`, main file path `app/streamlit_app.py`.
4. Under **Advanced settings**, choose Python 3.12. No secrets are needed.
5. Deploy. Dependencies install from `app/requirements.txt`, which installs this package with the `app` extra.
6. Under the app's **Settings > Sharing**, keep it restricted to invited viewers while the repository is private.

If the build log shows an install error, copy its last lines into the project chat.
