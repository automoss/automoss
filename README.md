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
1. Build: `docker build . -t automoss`
2. Run: `docker run -p 8000:80 --rm -it automoss`

## TODO List
### High Priority
- [ ] Refactor to comply with current versions of Django and Celery
- [ ] Separate database and file storage from main application container
- [ ] Add cancel/delete functionality for jobs
- [ ] Use credentials from .env when accessing database
- [ ] Update archive processing logic to comply with current Vula assignment structure
- [ ] Account for "tar+1.gz" edge case
### Low Priority
- [ ] Restrict user permissions in Docker container
- [ ] Paginate jobs and job results
- [ ] Add map files for js libraries (some versions of Safari cause issues without these)
- [ ] Change email account to UCT-based email (instead of Gmail)
- [ ] Fix timezone issues (when using Docker container)
- [ ] Improve responsiveness for smaller screens/breakpoints
