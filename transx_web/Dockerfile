# docker build  --no-cache --progress=plain -t caravanacloud/transx_web .
# Use an official Python runtime as a base image
FROM python:3.12-slim

# Install dependencies
RUN pip install --no-cache-dir poetry

# ARG USERNAME=container-user
# ARG USER_UID=1000
# ARG USER_GID=$USER_UID
# RUN groupadd --gid $USER_GID $USERNAME 
# ENV USER_HOME=/home/$USERNAME
# RUN useradd --uid $USER_UID --gid $USER_GID -m $USERNAME -d "${USER_HOME}"
# USER $USERNAME

# Set the working directory in the container
ARG APP_HOME=/home/$USERNAME/transx
WORKDIR ${APP_HOME}



# Copy the project code
COPY .. .

# Build core module
WORKDIR ${APP_HOME}/transx
RUN poetry config virtualenvs.create false
RUN poetry install 

# Build web module
WORKDIR ${APP_HOME}/transx_web
RUN poetry config virtualenvs.create false
RUN poetry install 

# Expose port 8000
EXPOSE 8000

# Command to run the server
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
CMD ["find", "/usr/src/"]
