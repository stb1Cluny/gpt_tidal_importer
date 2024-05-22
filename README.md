This Python script imports a playlist to a Tidal(music streaming service) account.
This is a fun project to use ChatGPT to conversationally add features to a python script. 
Tidal requires registered apps to link to a privacy notice which will be added to this repository.

To use:
1. Install requests and requests_oauth2 modules in your Python environment
2. Put a secrets.txt file in the same dir as gpt_tidal_importer.py using this format:
    CLIENT_ID=your_client_id_here
    CLIENT_SECRET=your_client_secret_here
    REDIRECT_URI=your_redirect_uri_here
3. Run gpt_tidal_importer.py