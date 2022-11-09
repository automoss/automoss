![AutoMOSS Logo](/static/img/automoss.png)
Copyright ©️ 2021 AutoMOSS. All Rights Reserved.

---

Automate the process of detecting similarities between code for a collection of computer science assignments.

## Basic Running Instructions
1. Add `automoss/.env` file with the correct information filled in. See `automoss/example.env` for the required variables.
2. Run `make install` to install the required dependencies.
3. Run `make run` to start the server.
4. Open a web browser and go to the WebApp (e.g., http://localhost:8000).

## Running With Docker
1. Install `docker` on your local system
2. Add `automoss/.env` file with the correct information filled in. See `automoss/example.env` for the required variables.
3. Run `make docker-start` or `docker-compose up -d` to start the application.
4. Open a web browser and go to the WebApp (e.g., http://localhost:8000). 
5. Run `make docker-stop` or `docker-compose down` to stop the application.

## Help
There is a user manual `docs/user-manual.pdf` that contains basic instructions for operating the app (please ignore its running instructions). This can also be accessed via the help menu in the app.

## TODO List
- [ ] Restrict user permissions in Docker container
- [ ] Paginate jobs and job results
- [ ] Add map files for js libraries (some versions of Safari cause issues without these)
- [ ] Improve responsiveness for smaller screens/breakpoints
