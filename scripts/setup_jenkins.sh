#!/usr/bin/env bash

set -xe
trap 'jobs -p | xargs --no-run-if-empty kill' INT TERM EXIT

export PATH=$PATH:/usr/local/bin
export PIP_DOWNLOAD_CACHE=~/.pip_cache

WD=`pwd`
DB_HOST_IP=${DB_HOST_IP:=127.0.0.1}
POSTGRES_PORT=${POSTGRES_PORT:=5432}

echo "Installing CKAN..."

mkdir -p ~/ckan/default
chown `whoami` ~/ckan/default
virtualenv --no-site-packages ~/ckan/default

. ~/ckan/default/bin/activate
pip install -e 'git+https://github.com/ckan/ckan.git@ckan-2.7.0#egg=ckan'
pip install -r ~/ckan/default/src/ckan/requirement-setuptools.txt
pip install -r ~/ckan/default/src/ckan/requirements.txt
deactivate

. ~/ckan/default/bin/activate
mkdir -p ~/etc/ckan/default
chown -R `whoami` ~/etc/ckan/

echo "Removing databases from old executions..."
sudo -u postgres psql -c "DROP DATABASE IF EXISTS datastore_test;"
sudo -u postgres psql -c "DROP DATABASE IF EXISTS ckan_test;"
sudo -u postgres psql -c "DROP USER IF EXISTS ckan_default;"


echo "Creating the PostgreSQL user and database..."
sudo -u postgres psql -c "CREATE USER ckan_default WITH PASSWORD 'pass';"
sudo -u postgres psql -c 'CREATE DATABASE ckan_test WITH OWNER ckan_default;'
sudo -u postgres psql -c 'CREATE DATABASE datastore_test WITH OWNER ckan_default;'


echo "Modifying the configuration to setup properly the Postgres port..."
mkdir -p data/storage

sed -i "s|\/usr\/lib\/ckan\/default\/src\/ckan\/test-core\.ini|\/home\/jenkins\/ckan\/default\/src\/ckan\/test-core\.ini|g" test.ini

echo "
sqlalchemy.url = postgresql://ckan_default:pass@$DB_HOST_IP:$POSTGRES_PORT/ckan_test
ckan.datastore.write_url = postgresql://ckan_default:pass@$DB_HOST_IP:$POSTGRES_PORT/datastore_test
ckan.datastore.read_url = postgresql://datastore_default:pass@$DB_HOST_IP:$POSTGRES_PORT/datastore_test

ckan.storage_path=data/storage" >> test.ini

echo "Installing ckanext-apinf_resources and its requirements..."
pip install -r requirements.txt
pip install -r dev-requirements.txt
python setup.py develop


echo "Running tests..."
python setup.py nosetests