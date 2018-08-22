mkdir ~/.config/.gdfl
cd ~/.config/.gdfl

git clone https://github.com/Thomas-X/drivesync.git
cd drivesync
bundle install

ruby drivesync.rb

cd ../

git clone https://github.com/Thomas-X/argos.git
cd argos
mv argos@pew.worldwidemann.com ~/.local/share/gnome-shell/extensions
cd ../
rm -rf argos

git clone https://github.com/Thomas-X/google-drive-gnome.git
cd google-drive-gnome
mv top.8s+.sh ~/.config/argos