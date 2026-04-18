# workflow-project

Cloud Native solution for users to choose from pre-defined workflows and create their own AI powered workflow designs

# # How to use:

- First build the image in the root folder using this command
  ```bash
  docker build -t image-name:tag .
  ```
- Place the same image-name and tag in the "FROM" section of the Dockerfile present in /backend
- Install doc-ling models locally
  ```bash
  cd backend
  docling-tools models download --all -o /model_cache/docling
  ```
- Run the application using docker-compose from the project root directory
  ```bash
  docker-compose up
  ```
