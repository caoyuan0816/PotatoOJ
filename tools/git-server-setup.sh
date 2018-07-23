#!/usr/bin/env bash

set -e

if [ "$(id -u)" != "0" ]; then
  echo "$0 must be run as root" >&2
  exit 1
fi

# Install latest git
add-apt-repository -y ppa:git-core/ppa
apt-get update
apt-get -y install git

# Create ssh key for admin and client
ssh-keygen -N '' -f git-admin-key
ssh-keygen -N '' -f git-client-key

CLIENT_KEY="$(pwd)/git-client-key.pub"
ADMIN_KEY="$(pwd)/git-admin-key.pub"
ADMIN_PRIVATE_KEY="$(pwd)/git-admin-key"

# Create user git
adduser --system --shell /bin/bash --group --disabled-password --home /home/git git

# Install gitolite and setup
PK="$(pwd)/admin.pub"
cp "$ADMIN_KEY" "$PK"
sudo -H -E PK="$PK" -u git bash << 'EOF'
cd $HOME
git clone --branch v3.6.5 git://github.com/sitaramc/gitolite
mkdir -p $HOME/bin
gitolite/install -to $HOME/bin
rm -rf gitolite
$HOME/bin/gitolite setup -pk "$PK"
EOF
rm "$PK"

# Add client public key to gitolite
GIT_SSH_COMMAND="ssh -i $ADMIN_PRIVATE_KEY -o StrictHostKeyChecking=no" git clone git@localhost:gitolite-admin
git -C gitolite-admin/ config user.email "git@potatooj"
git -C gitolite-admin/ config user.name "potato"
cp "$CLIENT_KEY" gitolite-admin/keydir/client.pub
git -C gitolite-admin/ add keydir
git -C gitolite-admin/ commit -m "Add client public key"
cat << 'EOF' > gitolite-admin/conf/gitolite.conf
repo gitolite-admin
    RW+     =   admin

repo data/[1-9]\d*
    C       =   admin
    RW+     =   admin
    R       =   client
EOF
git -C gitolite-admin/ add conf
git -C gitolite-admin/ commit -m "Set conf"
GIT_SSH_COMMAND="ssh -i $ADMIN_PRIVATE_KEY -o StrictHostKeyChecking=no" git -C gitolite-admin/ push

rm -rf gitolite-admin

echo "Git server install and setup done!"
echo "Now copy git-client-key to judge client conf folder"
