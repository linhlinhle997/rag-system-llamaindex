# RAG System with LlamaIndex

This project implements a `Retrieval-Augmented Generation (RAG)` system using `FastAPI` for the backend and `Streamlit` for the frontend. The system leverages Hugging Face models for language and embedding tasks, and uses `LlamaIndex` for indexing and querying. The RAG system allows users to upload their personal files, ask questions, and receive answers ranked by relevance and score based on the contents of the uploaded files.

## Setup

### Prerequisites

- Docker
- Visual Studio Code with the Remote - Containers extension

### Using Dev Container

1. Open the project in Visual Studio Code.

2. When prompted, click on "Reopen in Container" to open the project in the dev container.

3. The dev container will automatically build and set up the environment based on the configuration in `.devcontainer/devcontainer.json` and `.devcontainer/docker-compose.yml`.

### Backend Setup (FastAPI)

1. Navigate to the `backend` directory:

   ```sh
   cd backend
   ```

2. Copy the example environment file and update it with your configuration:

   ```sh
   cp .env.example .env
   ```

3. Set up the environment variables in the .env file:

   ```sh
   LLM_MODEL_NAME=your_llm_model
   EMBED_MODEL_NAME=your_embed_model
   HF_TOKEN=your_huggingface_token_here
   ```

   - `LLM_MODEL_NAME`: Specifies the model used for language generation tasks. In this case, `Mixtral-8x7B-Instruct from Mistralai`.
   - `EMBED_MODEL_NAME`: Specifies the model used for embedding tasks. Here, `BAAI/bge-small-en-v1.5` from BAAI is used.
   - `HF_TOKEN`: Your Hugging Face authentication token. This token is required to access the Hugging Face API for model downloading and interaction. You can obtain it by creating a Hugging Face account and generating a token in the settings section.

4. Run the backend service:

   ```sh
   make run
   ```

5. The backend will be available at `http://localhost:8000`.

### Frontend Setup (Streamlit)

1. Navigate to the `frontend` directory:

   ```sh
   cd frontend
   ```

2. Copy the example environment file and update it with your configuration:

   ```sh
   cp .env.example .env
   ```

3. Run the frontend service:

   ```sh
   make run
   ```

4. The frontend will be available at `http://localhost:8501`.

## Usage

### Backend Endpoints

- **Upload File**: `POST /rag/upload_file/`

  Allows you to upload your personal file to the system.

- **Delete Files**: `DELETE /rag/delete_files/`

  Enables the deletion of uploaded files.

- **Query RAG**: `GET /rag/query`
  Submit a query to the RAG system, which will process the question against the uploaded file and return ranked answers with a score.

### Frontend

The frontend provides an easy-to-use interface to interact with the RAG system. You can upload your file, ask a question, and view the system's ranked answers.

## Video Demo

A video demonstration of the RAG System is included to show how the system works, including uploading files, querying the RAG system, and receiving ranked answers.

[Watch the RAG System Demo](./demo/rag_system_demo.webm)

---

### Optional: User Management

This project also includes a User Management feature that is optional and independent of the RAG system. If you'd like to try it, you can perform basic CRUD operations for users, including:

- **Authentication**: Users can log in and log out.
- **Create** User: Add a new user to the system.
- **Update User**: Modify the details of an existing user.
- **Delete User**: Remove a user from the system.
- **List Users**: View a list of all users in the system.

Default User:

- Email: admin@mail.com
- Password: 123123
