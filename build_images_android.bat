@echo off
setlocal enabledelayedexpansion

:: Define BrowserStack credentials
set BROWSERSTACK_USERNAME=pritikakade_mpWqaD
set BROWSERSTACK_ACCESS_KEY=qa4V3paWbWhssYuufqpt

:: Define the folder containing Dockerfiles
set dockerfiles_folder=android_dockerfiles

:: Define environments
set environments=qa staging prod


:: Initialize an empty variable to track image names
set image_list=

:: Loop through environments to build and push Docker images
for %%e in (%environments%) do (
    echo Building Docker image for environment: %%e

    :: Build Docker image with BrowserStack credentials using the corresponding Dockerfile
    docker build -t %%e_image --build-arg BROWSERSTACK_USERNAME=%BROWSERSTACK_USERNAME% --build-arg BROWSERSTACK_ACCESS_KEY=%BROWSERSTACK_ACCESS_KEY% -f %dockerfiles_folder%\Dockerfile_android_%%e .

    :: Check if the image was built successfully
    if !ERRORLEVEL! neq 0 (
        echo Failed to build Docker image for environment: %%e
        exit /b 1
    )


    :: Append the image name to the list
    if "!image_list!" == "" (
        set image_list=%dockerhub_username%/%repository_name%:android_%%e
    ) else (
        set image_list=!image_list!, %dockerhub_username%/%repository_name%:android_%%e
    )
)

echo All Docker images built successfully.

:: Define the filename for the image list (optional)
set filename=android_docker_images_list.txt

:: Echo the image list to the file with correct formatting (optional)
echo list=[!image_list!] > %filename%

echo Image list appended to %filename%
endlocal
