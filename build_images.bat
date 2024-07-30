@echo off
setlocal enabledelayedexpansion


:: Define the folder containing Dockerfiles
set dockerfiles_folder=web_dockerfiles

:: Array of Dockerfile names
set dockerfiles[0]=Dockerfile_web_1
set dockerfiles[1]=Dockerfile_web_2
set dockerfiles[2]=Dockerfile_web_3

:: Array of image names corresponding to the Dockerfiles
set images[0]=image1
set images[1]=image2
set images[2]=image3

set image_list=

:: Clear the built_images.txt file if it exists
if exist web_docker_images.txt del web_docker_images.txt

:: Loop through the Dockerfiles and build the images
for /L %%i in (0,1,2) do (
    set dockerfile=!dockerfiles_folder!\!dockerfiles[%%i]!
    set image=!images[%%i]!

    echo Building image !image! from !dockerfile!...
    docker build -f !dockerfile! -t !image! .

    if !ERRORLEVEL! neq 0 (
        echo Failed to build !image!
        exit /b 1
    )

    :: Append the image name to the list
    if "!image_list!" == "" (
        set image_list=!image!
    ) else (
        set image_list=!image_list!, !image!
    )
)

echo All Docker images built successfully.

:: Define the filename for the image list
set filename=web_docker_images_list.txt

:: Echo the image list to the file with correct formatting
echo list=[!image_list!] > %filename%

echo Image list appended to %filename%
endlocal

