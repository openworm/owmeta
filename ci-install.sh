pip install -e .
pip install coveralls
pip install -r test-requirements.txt
owm clone https://github.com/openworm/OpenWormData.git --branch owmeta
if [ $BUNDLE_TESTS ] ; then
    owm bundle register ./owmeta-schema-bundle.yml
    owm bundle register ./owmeta-data-bundle.yml
    owm bundle install openworm/owmeta-schema
    owm bundle install openworm/owmeta-data
fi
