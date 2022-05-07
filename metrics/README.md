# Gremlin Jira Metrics

## Setup

1. Download Anaconda Graphical Installer
2. Install Anaconda (reopen all terminal windows)
3. Clone the `gremlin/jira` repo on github
4. In the jira directory, run `conda env create -f environment.yml`
5. Open Anaconda Navigator, it may ask you to update. Do that.
6. Go to https://id.atlassian.com/manage-profile/security/api-tokens and create an API token for Jira, save it
7. Create a ~/.netrc (`touch ~/.netrc`)file with permissions 0600 `chmod ~./netrc 0600`) and populate it with
```
machine gremlininc.atlassian.net
login YOUR_EMAIL@gremlin.com
password YOUR_API_TOKEN
```
8. launch JupyterLab in Anaconda Navigator
9. Open ticket_metrics.ipynb in jupyterlab
10. Verify config options and run.
