cd hawk-web
rm -rf ./frontend_artifacts
ng build --prod --output-path ./frontend_artifacts --output-hashing none
cp ./frontend_artifacts/*.* ../../backend/static/
cp ../../backend/static/index.html ../../backend/templates/
rm -rf frontend_artifacts

sed -i -r -e 's/\"styles\.css\"/\"\/static\/styles\.css\"/' ../../backend/templates/index.html


sed -i -r -e 's/runtime.js/\/static\/runtime.js/' ../../backend/templates/index.html
sed -i -r -e 's/polyfills.js/\/static\/polyfills.js/' ../../backend/templates/index.html
sed -i -r -e 's/main.js/\/static\/main.js/' ../../backend/templates/index.html


sed -i -r -e 's/myimage1\=\"/myimage1\=\"\/static\//g' ../../backend/static/main.js

# TODO: Below substitution is required when deploying on windows
echo "NOT Substituting for Windows deployment"
#sed -i -r -e 's/\\\\assets\\\\/\\\\static\\\\assets\\\\//g' ../../backend/static/main.js


