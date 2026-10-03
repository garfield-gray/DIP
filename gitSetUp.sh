#!/bin/bash
# This is a simple shell script for executing everytime you wanna connect to github
# make sure you've made ssh key in the sibling directory of the current one and have added it 
# to the github setting in ssh keys

echo "Hello, Abbas!"
git config --global user.email "garfield.gray.999@gmail.com"
git config --global user.name "garfield-gray"

chmod 700 ../.ssh/
chmod 600 ../.ssh/id_ed25519
chmod 644 ../.ssh/id_ed25519.pub

eval "$(ssh-agent -s)" # these two lines must be run in the terminal directly & I don't know why!
ssh-add ../.ssh/id_ed25519

ssh -T git@github.com

