# glog
wget https://github.com/google/glog/archive/v0.3.3.tar.gz
tar zxvf v0.3.3.tar.gz
cd glog-0.3.3
./configure
make && make install
cd ..
# gflags
wget https://github.com/schuhschuh/gflags/archive/master.zip
unzip master.zip
cd gflags-master
mkdir build && cd build
export CXXFLAGS="-fPIC" && cmake .. && make VERBOSE=1
make && make install
cd ..
# lmdb
git clone https://github.com/LMDB/lmdb
cd lmdb/libraries/liblmdb
make && make install
