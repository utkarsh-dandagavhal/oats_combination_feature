import json
import subprocess

import oapackage
from openpyxl import Workbook
import os


def generate_testing_combinations(factors, levels, runs=None):
    """
    Generates testing combinations using an orthogonal array from oapackage.

    Args:
        factors (list): A list of strings representing the testing factors (e.g., ["Browser", "Device"]).
        levels (dict): A dictionary mapping each factor to a list of its possible levels (e.g., {"Browser": ["Chrome", "Firefox"]}).
        runs (int, optional): The desired number of test cases (rows in the orthogonal array).
            Defaults to None, which uses a suitable default based on oapackage behavior.

    Returns:
        list: A list of dictionaries, where each dictionary represents a test case combination.
    """
    if len(factors) != len(levels):
        raise ValueError("Number of factors must match the number of level dictionaries.")

    if runs is None:
        runs = find_suitable_runs(factors, levels)

    array_class = oapackage.arraydata_t(len(levels[factors[0]]), runs, len(factors), len(factors))
    array_link = array_class.create_root()
    generated_array = array_link.getarray()

    combinations = []

    for i in range(runs):
        combination = {}
        for j, factor in enumerate(factors):
            combination[factor] = levels[factor][generated_array[i][j] % len(levels[factor])]
        combinations.append(combination)

    return combinations


def find_suitable_runs(factors, levels):
    """
    Find a suitable number of runs (test cases) for the orthogonal array.

    This example implementation simply returns a placeholder value.
    Replace it with your logic to determine the optimal or desired number of runs
    based on factors, levels, and testing coverage requirements.

    Args:
        factors (list): A list of testing factors.
        levels (dict): A dictionary mapping factors to their levels.

    Returns:
        int: The estimated or desired number of test cases.
    """
    return 3


def write_combinations_to_excel(combinations, filename="testing_combinations.xlsx"):
    """
    Writes testing combinations to an Excel file.

    Args:
        combinations (list): A list of dictionaries representing test case combinations.
        filename (str, optional): The filename of the Excel file. Defaults to "testing_combinations.xlsx".
    """
    wb = Workbook()
    ws = wb.active

    header_row = [factor for factor in combinations[0].keys()]
    ws.append(header_row)

    for combination in combinations:
        data_row = [combination[factor] for factor in combinations[0].keys()]
        ws.append(data_row)

    wb.save(filename)


web_dockerfile_list = 'web_dockerfile_list.txt'
android_dockerfile_list = 'android_dockerfile_list.txt'


def initialize_dockerfile_list(file_path):
    if not os.path.exists(file_path):
        with open(file_path, 'w') as f:
            f.write('Dockerfiles Generated:\n')


def update_dockerfile_list(file_path, dockerfile_name):
    with open(file_path, 'a') as f:
        f.write(dockerfile_name + '\n')


def generate_browserstack_yml(env_key, env_config, output_file):
    app_url = env_config['env'][env_key]

    platforms = []
    for device in env_config['device']:
        platform = f"""
    - platformName: android
      deviceName: {device['deviceName']}
      platformVersion: {device['platformVersion']}
            """
        platforms.append(platform)

    platforms_str = "\n".join(platforms)

    browserstack_yml_content = f"""
userName: pritikakade_mpWqaD
accessKey: qa4V3paWbWhssYuufqpt
app: {app_url}

platforms:
{platforms_str}

projectName: wm-indexnine-qa-automation
buildIdentifier: V99.99
buildName: {env_key}
buildTag: reg
parallelsPerPlatform: 1
CUSTOM_TAG_1: "Test"
framework: robot
browserstack.idleTimeout: 300
interactiveDebugging : true
browserstack.debug : true
testObservability: true
"""
    with open(output_file, 'w') as f:
        f.write(browserstack_yml_content.strip())
    print(f"browserstack.yml written to '{output_file}'")


def generate_dockerfile_android(env_key,output_file,dockerfiles_folder='android_dockerfiles'):

    if not os.path.exists(dockerfiles_folder):
        os.makedirs(dockerfiles_folder)


    dockerfile_content = f"""
# Use the official openjdk:8-jdk runtime as a parent image
FROM openjdk:8-jdk

# Set environment variable to avoid interactive prompts during package installations
ENV DEBIAN_FRONTEND=noninteractive

# Update package lists and install necessary dependencies
RUN apt-get update -y && \\
apt-get install -y \\
python3 \\
python3-pip \\
nodejs \\
npm \\
--no-install-recommends && \\
apt-get clean && \\
rm -rf /var/lib/apt/lists/*

# Install Robot Framework and related libraries
RUN pip3 install --no-cache-dir \\
robotframework-appiumlibrary \\
Appium-Python-Client \\
selenium==4.15.2 \\
robotframework==6.1.1 \\
robotframework-seleniumlibrary==6.2.0 \\
robotframework-retryfailed==0.2.0 \\
robotframework-pabot==2.16.0 \\
openpyxl==3.1.2 \\
allure-robotframework==2.13.2 \\
webdrivermanager \\
pandas \\
requests \\
Pillow \\
robotframework-requests \\
robotframework-doctestlibrary \\
browserstack-sdk

# Set the working directory
WORKDIR /robot

# Copy the current directory contents into the container at /robot
COPY . /robot

# Define build arguments for BrowserStack credentials
ARG BROWSERSTACK_USERNAME
ARG BROWSERSTACK_ACCESS_KEY

# Set environment variables for BrowserStack
ENV BROWSERSTACK_USERNAME=${{BROWSERSTACK_USERNAME}}
ENV BROWSERSTACK_ACCESS_KEY=${{BROWSERSTACK_ACCESS_KEY}}
ENV BROWSERSTACK_CONFIG_FILE="browserstack_android_{env_key}.yml"

# Run the test
CMD ["browserstack-sdk", "pabot", "Mobile/Android/KC/TestCases/Login/already_registered_user_test.robot"]
    """
    file_output_path = os.path.join(dockerfiles_folder, output_file)

    with open(file_output_path, 'w') as f:
        f.write(dockerfile_content.strip())
    print(f"Dockerfile written to '{file_output_path}'")

    update_dockerfile_list(android_dockerfile_list, file_output_path)


def generate_dockerfile_web(env_details, json_file, output_file, platform,dockerfiles_folder="web_dockerfiles"):

    if not os.path.exists(dockerfiles_folder):
        os.makedirs(dockerfiles_folder)

    dockerfile_content = f"""
# Use the latest Ubuntu LTS as the base image
FROM ubuntu:20.04

# Set the DEBIAN_FRONTEND to noninteractive to suppress prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Update the image and install system packages
RUN apt-get update && apt-get install -y \\
    python3 \\
    python3-pip \\
    wget \\
    xvfb \\
    zip \\
    ca-certificates \\
    libnss3-dev \\
    libasound2 \\
    libxss1 \\
    libappindicator3-1 \\
    libindicator7 \\
    gconf-service \\
    libgconf-2-4 \\
    libpango1.0-0 \\
    xdg-utils \\
    fonts-liberation \\
    wmctrl

# Install Robot Framework and SeleniumLibrary along with other required Python packages
RUN pip3 install selenium==4.15.2 \\
                 robotframework==6.1.1 \\
                 robotframework-seleniumlibrary==6.2.0 \\
                 robotframework-retryfailed==0.2.0 \\
                 robotframework-pabot==2.16.0 \\
                 openpyxl==3.1.2 \\
                 allure-robotframework==2.13.2 \\
                 webdrivermanager \\
                 pandas

# Set the working directory
WORKDIR /robot

# Copy the current directory contents into the container at /robot
COPY . /robot

# Copy the environment JSON file into the container at /robot/Runners/Environment/{platform}_environment.json
COPY {json_file} /robot/Runners/Environment/{platform}_environment.json

# Execute the Robot Framework test cases
CMD ["robot","/robot/Web/RR/TestCases/Login/login_test.robot"]
"""
    formatted_content = dockerfile_content.format(json_file=json_file, platform=platform)

    file_output_path = os.path.join(dockerfiles_folder, output_file)

    with open(file_output_path, 'w') as f:
        f.write(formatted_content.strip())
    print(f"Dockerfile written to '{file_output_path}'")

    update_dockerfile_list(web_dockerfile_list, file_output_path)


def update_web_environment_combinations(combinations, env_config):
    for index, combination in enumerate(combinations):
        env_key = combination.get('env', '').lower()
        browser_key = combination.get('browser', '').lower()

        if env_key in env_config['env'] and browser_key in env_config['browser']:
            updated_env = {
                "env": env_config['env'][env_key],
                "browser": env_config['browser'][browser_key],
                "window_height": env_config['window_height'],
                "window_width": env_config['window_width'],
                "receiver_email": env_config['receiver_email']
            }

            output_file = f"updated_env_web_{index+1}.json"
            with open(output_file, 'w') as f:
                json.dump(updated_env, f, indent=2)

            print(f"Updated environment combination {index+1} for web written to '{output_file}'")

            dockerfile_output_file = f"Dockerfile_web_{index + 1}"
            generate_dockerfile_web(updated_env, output_file, dockerfile_output_file, "web")


def commit_and_push_changes(branch, remote_url):
    # Add all changes to the staging area
    subprocess.run(["git", "add", "."], check=True)

    # Commit changes with a default message
    subprocess.run(["git", "commit", "-m", "Commit changes"], check=True)

    # Push changes to the specified branch on remote repository
    subprocess.run(["git", "push", "origin", branch], check=True)


def switch_and_merge_branch(branch):
    # Checkout the specified branch
    subprocess.run(["git", "checkout", branch], check=True)

    # Merge changes from git-actions-demo into the current branch
    subprocess.run(["git", "merge", "git-actions-demo", "--no-edit"], check=True)

    # Push changes to the specified branch on remote repository
    subprocess.run(["git", "push", "origin", branch], check=True)


if __name__ == "__main__":
    with open("combined_environment.json", 'r') as f:
        combined_env = json.load(f)

    web_files = []
    android_files = []

    if 'web' in combined_env:
        factors = ["env", "browser"]
        levels = {
            "env": list(combined_env['web']['env'].keys()),
            "browser": list(combined_env['web']['browser'].keys())
        }
        web_combinations = generate_testing_combinations(factors, levels)
        update_web_environment_combinations(web_combinations, combined_env['web'])

        for index in range(len(web_combinations)):
            web_files.append(f"Dockerfile_web_{index + 1}")
            web_files.append(f"updated_env_web_{index + 1}.json")

        print("Web Files:")
        for file in web_files:
            print(file)

    if 'android' in combined_env:

        environments = list(combined_env['android']['env'].keys())

        for env in environments:

            for env in environments:
                browserstack_yml_output_file = f"browserstack_android_{env}.yml"
                generate_browserstack_yml(env, combined_env['android'], browserstack_yml_output_file)
                android_files.append(browserstack_yml_output_file)

                dockerfile_output_file = f"Dockerfile_android_{env}"
                generate_dockerfile_android(env, dockerfile_output_file)
                android_files.append(dockerfile_output_file)

            print("Android Files:")
            for file in android_files:
                print(file)

    # subprocess.run(["build_images_android.bat"], shell=True)

    # subprocess.run(["build_images.bat"], shell=True)

    remote_url = input("Please enter the remote URL for git push: ")

    commit_and_push_changes("git-actions-demo", remote_url)

    # # Switch to web branch and merge changes
    # switch_and_merge_branch("web")

    # Switch to android branch and merge changes
    switch_and_merge_branch("android")
    


















