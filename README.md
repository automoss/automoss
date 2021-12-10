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
