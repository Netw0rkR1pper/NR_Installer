#!/usr/bin/python

import os
import time
import requests
import zipfile
import subprocess


repo_url = "https://github.com/Netw0rkR1pper/NetworkRipper/archive/refs/heads/main.zip"

ascii_art = """
    _   __     __                      __      ____  _                      
   / | / /__  / /__      ______  _____/ /__   / __ \(_)___  ____  ___  _____
  /  |/ / _ \/ __/ | /| / / __ \/ ___/ //_/  / /_/ / / __ \/ __ \/ _ \/ ___/
 / /|  /  __/ /_ | |/ |/ / /_/ / /  / ,<    / _, _/ / /_/ / /_/ /  __/ /    
/_/ |_/\___/\__/ |__/|__/\____/_/  /_/|_|  /_/ |_/_/ .___/ .___/\___/_/     
                                                  /_/   /_/                 
"""


def download_and_extract_github_repo(repo_url, destination_path):
    print("[+] Downloading and unpacking Network_Ripper.")
    response = requests.get(repo_url)
    if response.status_code != 200:
        print("[-] Error loading from GitHub.")
        return

    archive_path = os.path.join(destination_path, 'Network_Ripper.zip')
    with open(archive_path, 'wb') as file:
        file.write(response.content)

    with zipfile.ZipFile(archive_path, 'r') as zip_ref:
        zip_ref.extractall(destination_path)

    extracted_folder_path = os.path.join(destination_path, "Network_Ripper")
    os.rename(os.path.join(destination_path, zip_ref.namelist()[0]), extracted_folder_path)

    os.system(f"sudo mkdir {destination_path}/Network_Ripper/report")
    os.system(f"sudo mkdir {destination_path}/Network_Ripper/report/log")
    os.system(f"sudo mkdir {destination_path}/Network_Ripper/report/Attacks")
    os.system(f"sudo mkdir {destination_path}/Network_Ripper/report/Network_Information")
    os.system(f"sudo mkdir {destination_path}/Network_Ripper/report/Sniff")
    os.system(f"chmod -R 777 {destination_path}/Network_Ripper")

    os.remove(archive_path)
    print("[+] Download and unpacking DONE.\n")


def user_autologin():
    username = 'kali'
    subprocess.call(
        ['sudo', 'sed', '-i', 's/#autologin-user=/autologin-user={}/'.format(username), '/etc/lightdm/lightdm.conf'])
    subprocess.call(
        ['sudo', 'sed', '-i', 's/#autologin-user-timeout=0/autologin-user-timeout=0/', '/etc/lightdm/lightdm.conf'])


def add_to_sudoers(username, command):
    try:
        with open('/etc/sudoers', 'a') as sudoers_file:
            sudoers_file.write(f"{username} ALL=(ALL) NOPASSWD: {command}\n")
    except Exception as e:
        print(f"Error adding to sudoers: {e}")


def create_systemd_service(service_name, file_path, restart='no'):
    service_path = f'/etc/systemd/system/{service_name}.service'

    with open(service_path, 'w') as service_file:
        service_file.write(f'''
[Unit]
Description={service_name}
After=network.target

[Service]
ExecStart={file_path}
WorkingDirectory={os.path.dirname(file_path)}
StandardOutput=append:/home/Ripper/Network_Ripper/report/log/{service_name}.log
StandardError=append:/home/Ripper/Network_Ripper/report/log/{service_name}_error.log
Restart={restart}
User=kali

[Install]
WantedBy=multi-user.target
''')

    os.system(f'sudo systemctl enable {service_name}')
    print(f"[+] Added {service_name} service to systemd autorun.\n")


def install():
    os.system("clear")
    print(ascii_art)
    print("            Welcome to Network Ripper Software installer!           ")
    print("")
    print("Installing...")
    print("")

    # Installing requirements
    print("[+] Installing requirements.\n")
    os.system("sudo pip install -r requirements.txt")

    # Create user Ripper and set up privileges
    print("[+] Create user Ripper and set up privileges.\n")
    os.system("sudo useradd -m Ripper -s /bin/bash")
    os.system("echo 'Ripper:root' | sudo chpasswd")
    os.system("sudo usermod -aG sudo Ripper")

    # Configure SSH access for user Ripper
    print("[+] Configure SSH access for user Ripper.\n")
    os.system("sudo mkdir -p /home/Ripper/.ssh")
    os.system("sudo chmod 700 /home/Ripper/.ssh")
    os.system("sudo touch /home/Ripper/.ssh/authorized_keys")
    os.system("sudo chmod 600 /home/Ripper/.ssh/authorized_keys")
    os.system("sudo chown -R Ripper:Ripper /home/Ripper/.ssh")
    # Create SSH banner for user Ripper
    with open('/etc/motd', 'w') as motd_file:
        motd_file.write(ascii_art)

    print("")
    print('[i] User "Ripper" created with "root" password and SSH access configured.')
    print("")

    # Update & install system tools
    print("[+] Update & install system tools. \n")
    os.system("apt update -y")
    os.system("apt install tshark -y")
    os.system("apt install nmap -y")
    os.system("apt install routersploit -y")
    os.system("apt install metasploit-framework -y")

    print("")
    download_and_extract_github_repo(
        repo_url,
        "/home/Ripper"
    )
    time.sleep(2)

    print("[+] Set user kali autologin.\n")
    user_autologin()
    time.sleep(2)

    print("[+] Add autorun & cron service.\n")
    add_to_sudoers('kali', 'ALL')
    time.sleep(2)
    create_systemd_service(
        "Network_Ripper_Cron",
        "/home/Ripper/Network_Ripper/cron.sh",
        "always"
    )
    time.sleep(2)
    create_systemd_service(
        "Network_Ripper",
        "/home/Ripper/Network_Ripper/start.sh"
    )
    time.sleep(5)

    print(ascii_art)
    print("            Network Ripper installation was successful!              \n")
    print("Network Ripper location: /home/Ripper/Network_Ripper\n")
    print("                           I <3 XSS.IS                               ")

    time.sleep(5)
    reboot = input("Reboot now? (y or n)> ")
    if reboot.lower() in ["y", "yes"]:
        os.system("reboot")


if __name__ == "__main__":
    print(ascii_art)
    print("            Welcome to Network Ripper Software installer!           ")
    print("")
    time.sleep(5)
    os.system("clear")
    warn = input("All important information on the system may be lost, are you sure you want to install? (y or n)> ")
    if warn.lower() in ["y", "yes"]:
        install()
    else:
        os.system("clear")
        print("Bye-bye...")
        time.sleep(5)
        exit()
