# Containerized YTDLP for cron jobs in Kuberenetes

## Configurations
### API Configuration
#### Secrets
- Token, Refresh Token, Client ID, Client Secret
    - Either set ```$TOKEN, $REFRESH, $ID, $SECRET``` environment variables (preferably using secret injection) in the manifest or set the value in the configuration file.
    
