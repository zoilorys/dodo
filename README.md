# DoDo - LLM experiment

### Running the project

First, install dependencies with `pdm install`.

In order to run the project you need to run following services:
- `qdrant` - vector DB for similarity search
- `rabbitmq` - as message broker for `celery`
TODO: create `docker-compose.yml` file to make it easier to launch the setup.

Also, you need to create `.env` file, based on `.env.example`.

Before running the app, in separate terminal run `pdm celery` to launch celery app.

Then, run `pdm start` to launch FastAPI app.

### Phase 1 - Embed PDF-documents and be able to ask questions about document by ID (endpoints done, ui pending)

### Phase 2 - Basic bot with single agent with RAG by attached document(-s) with conversation management (not started)

### Phase 3 - Bot with multi-agent support with supervisor (not started)

### Phase 4 - Add tool calling to perform sideeffect actions (not started)